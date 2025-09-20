import os
import io
import csv
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
# Removed pandas - using built-in csv module instead
from PIL import Image
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import RAG components
from aimakerspace.text_utils import CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.gemini_utils.embedding import GeminiEmbeddingModel

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="PRD to Test Case Generator API")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Built-in API key for free tier (set via environment variable)
BUILT_IN_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

# Development mode configuration
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"  # Default to true for local testing

# Rate limiting configuration
FREE_TIER_DAILY_LIMIT = 5  # 5 free uses per day for production
UNLIMITED_DEV_LIMIT = 999999  # Unlimited for development
usage_tracker = {}  # In production, use Redis or database

# Data models
class TestCase(BaseModel):
    test_case_id: str
    feature: str
    scenario: str
    test_steps: str
    expected_result: str
    priority: str
    category: str

class ProcessResponse(BaseModel):
    success: bool
    message: str
    test_cases: List[TestCase]
    usage_info: Dict[str, Any]

# RAG Data Models
class RAGUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: str
    chunks_count: int
    usage_info: Dict[str, Any]

class RAGChatRequest(BaseModel):
    question: str
    document_id: Optional[str] = None
    api_key: Optional[str] = None

class RAGChatResponse(BaseModel):
    success: bool
    message: str
    answer: str
    sources: List[str]
    usage_info: Dict[str, Any]

def get_client_identifier(request: Request) -> str:
    """Get a unique identifier for rate limiting (IP + User Agent)"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    return f"{client_ip}_{hash(user_agent)}"

def check_free_tier_usage(client_id: str) -> Dict[str, Any]:
    """Check and update free tier usage"""
    today = datetime.now().date().isoformat()
    
    # In development mode, provide unlimited usage
    if DEVELOPMENT_MODE:
        if client_id not in usage_tracker:
            usage_tracker[client_id] = {}
        if today not in usage_tracker[client_id]:
            usage_tracker[client_id][today] = 0
        
        current_usage = usage_tracker[client_id][today]
        return {
            "tier": "development",
            "daily_limit": "unlimited",
            "used_today": current_usage,
            "remaining_today": "unlimited",
            "can_use": True,
            "development_mode": True
        }
    
    # Production mode with rate limiting
    if client_id not in usage_tracker:
        usage_tracker[client_id] = {}
    
    if today not in usage_tracker[client_id]:
        usage_tracker[client_id][today] = 0
    
    current_usage = usage_tracker[client_id][today]
    remaining = max(0, FREE_TIER_DAILY_LIMIT - current_usage)
    
    return {
        "tier": "free",
        "daily_limit": FREE_TIER_DAILY_LIMIT,
        "used_today": current_usage,
        "remaining_today": remaining,
        "can_use": remaining > 0,
        "development_mode": False
    }

def increment_free_tier_usage(client_id: str):
    """Increment free tier usage counter"""
    today = datetime.now().date().isoformat()
    
    if client_id not in usage_tracker:
        usage_tracker[client_id] = {}
    
    if today not in usage_tracker[client_id]:
        usage_tracker[client_id][today] = 0
    
    usage_tracker[client_id][today] += 1
    
    # Log usage in development mode for statistics
    if DEVELOPMENT_MODE:
        print(f"[DEV MODE] API call #{usage_tracker[client_id][today]} for client {client_id[:10]}... on {today}")

# Simple in-memory storage for RAG documents
rag_documents: Dict[str, VectorDatabase] = {}

class SimpleRAG:
    """Simple RAG system using the aimakerspace library"""
    
    def __init__(self):
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    async def process_document(self, text: str, document_id: str) -> int:
        """Process a document and store it in the vector database"""
        try:
            # Split text into chunks
            chunks = self.text_splitter.split(text)
            
            # Create vector database with Gemini embeddings
            vector_db = VectorDatabase(embedding_model=GeminiEmbeddingModel())
            
            # Build embeddings and populate vector database
            vector_db = await vector_db.abuild_from_list(chunks)
            
            # Store in memory (in production, use persistent storage)
            rag_documents[document_id] = vector_db
            
            return len(chunks)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    def search_document(self, question: str, document_id: str, k: int = 3) -> List[str]:
        """Search for relevant chunks in a document"""
        if document_id not in rag_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        vector_db = rag_documents[document_id]
        results = vector_db.search_by_text(question, k=k, return_as_text=True)
        return results
    
    async def generate_answer(self, question: str, context_chunks: List[str], api_key: str = "") -> str:
        """Generate an answer using the context chunks"""
        context = "\n\n".join(context_chunks)
        
        # Use provided API key or built-in key
        gemini_key = api_key if api_key else BUILT_IN_GEMINI_KEY
        if not gemini_key:
            return "API key required for RAG functionality."
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Based on the following context, please answer the question. If the answer cannot be found in the context, say "I cannot find the answer in the provided document."

Context:
{context}

Question: {question}

Answer:"""
        
        response = model.generate_content(prompt)
        return response.text

# Initialize RAG system
rag_system = SimpleRAG()

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text content from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_image(file_content: bytes, gemini_model) -> str:
    """Extract text content from image using Gemini Vision"""
    try:
        # Open image with PIL
        image = Image.open(io.BytesIO(file_content))
        
        # Use Gemini to extract text from image
        prompt = """
        Please extract all text content from this image. This appears to be a Product Requirements Document (PRD).
        Return only the extracted text content, maintaining the structure and formatting as much as possible.
        """
        
        response = gemini_model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

def generate_test_cases(prd_content: str, gemini_model) -> List[TestCase]:
    """Generate test cases from PRD content using Gemini AI"""
    try:
        prompt = f"""
        You are a senior QA engineer. Based on the following Product Requirements Document (PRD), generate comprehensive test cases.

        PRD Content:
        {prd_content}

        Please generate test cases covering:
        1. Functional testing scenarios
        2. UI/UX testing scenarios  
        3. Edge cases and error handling
        4. Performance considerations
        5. Security testing scenarios
        6. Integration testing scenarios

        For each test case, provide:
        - test_case_id: A unique identifier (TC001, TC002, etc.)
        - feature: The feature being tested
        - scenario: Brief description of the test scenario
        - test_steps: Detailed step-by-step instructions
        - expected_result: What should happen when the test is executed
        - priority: High, Medium, or Low
        - category: Functional, UI/UX, Performance, Security, Integration, or Edge Case

        Return the response as a JSON array with exactly this structure:
        [
            {{
                "test_case_id": "TC001",
                "feature": "Feature name",
                "scenario": "Test scenario description",
                "test_steps": "1. Step one\\n2. Step two\\n3. Step three",
                "expected_result": "Expected outcome",
                "priority": "High",
                "category": "Functional"
            }}
        ]

        Generate at least 10-15 comprehensive test cases. Ensure the JSON is valid and properly formatted.
        """
        
        response = gemini_model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            test_cases_data = json.loads(response_text)
            
            # Convert to TestCase objects
            test_cases = [TestCase(**case) for case in test_cases_data]
            return test_cases
            
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                try:
                    test_cases_data = json.loads(json_match.group(0))
                    test_cases = [TestCase(**case) for case in test_cases_data]
                    return test_cases
                except:
                    pass
            
            raise HTTPException(status_code=500, detail=f"Error parsing AI response: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")

@app.post("/api/upload-prd", response_model=ProcessResponse)
async def upload_prd(
    request: Request,
    file: UploadFile = File(...)
):
    """Upload PRD file and generate test cases using built-in API key"""
    
    # Validate file type
    allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload PDF, JPEG, JPG, or PNG files."
        )
    
    # Check if built-in API key is available
    if not BUILT_IN_GEMINI_KEY:
        raise HTTPException(
            status_code=503, 
            detail="Service temporarily unavailable. Please try again later."
        )
    
    # Check rate limiting
    client_id = get_client_identifier(request)
    usage_info = check_free_tier_usage(client_id)
    
    if not usage_info["can_use"]:
        limit_text = "unlimited" if DEVELOPMENT_MODE else str(FREE_TIER_DAILY_LIMIT)
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit ({limit_text} uses) reached. Please try again tomorrow."
        )

    try:
        # Configure Gemini with built-in API key
        genai.configure(api_key=BUILT_IN_GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        if file.content_type == 'application/pdf':
            prd_text = extract_text_from_pdf(file_content)
        else:  # Image files
            prd_text = extract_text_from_image(file_content, model)
        
        if not prd_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Generate test cases
        test_cases = generate_test_cases(prd_text, model)
        
        # Update usage tracking
        increment_free_tier_usage(client_id)
        
        # Get updated usage info
        updated_usage_info = check_free_tier_usage(client_id)
        if DEVELOPMENT_MODE:
            updated_usage_info["message"] = f"✅ Success! Development mode - unlimited usage (call #{updated_usage_info['used_today']})"
        else:
            updated_usage_info["message"] = f"✅ Success! {updated_usage_info['remaining_today']} uses remaining today"
        
        return ProcessResponse(
            success=True,
            message=f"Successfully generated {len(test_cases)} test cases",
            test_cases=test_cases,
            usage_info=updated_usage_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/usage-info")
async def get_usage_info(request: Request):
    """Get current usage information for the client"""
    client_id = get_client_identifier(request)
    usage_info = check_free_tier_usage(client_id)
    
    return {
        "service_available": bool(BUILT_IN_GEMINI_KEY),
        "free_tier_available": bool(BUILT_IN_GEMINI_KEY),
        "development_mode": DEVELOPMENT_MODE,
        **usage_info
    }

@app.post("/api/download-csv")
async def download_csv(test_cases: List[TestCase]):
    """Download test cases as CSV file"""
    try:
        # Create CSV content using built-in csv module (lighter than pandas)
        csv_buffer = io.StringIO()
        fieldnames = ['Test Case ID', 'Feature', 'Scenario', 'Test Steps', 'Expected Result', 'Priority', 'Category']
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write test case data
        for tc in test_cases:
            writer.writerow({
                'Test Case ID': tc.test_case_id,
                'Feature': tc.feature,
                'Scenario': tc.scenario,
                'Test Steps': tc.test_steps,
                'Expected Result': tc.expected_result,
                'Priority': tc.priority,
                'Category': tc.category
            })
        
        csv_content = csv_buffer.getvalue()
        
        # Return as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=test_cases.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating CSV: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "service": "PRD to Test Case Generator",
        "free_tier_available": bool(BUILT_IN_GEMINI_KEY),
        "daily_free_limit": "unlimited" if DEVELOPMENT_MODE else FREE_TIER_DAILY_LIMIT,
        "development_mode": DEVELOPMENT_MODE,
        "tier": "development" if DEVELOPMENT_MODE else "production"
    }

# Additional data models for prompting tool
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant" 
    content: str
    timestamp: Optional[datetime] = None

class PromptRequest(BaseModel):
    message: str
    context: Optional[str] = None  # Current test cases context
    test_cases: Optional[List[TestCase]] = None  # Current test cases for refinement
    api_key: Optional[str] = None

class PromptResponse(BaseModel):
    success: bool
    message: str
    response: str
    updated_test_cases: Optional[List[TestCase]] = None
    usage_info: Dict[str, Any]

class RefineTestCasesRequest(BaseModel):
    test_cases: List[TestCase]
    refinement_prompt: str
    api_key: Optional[str] = None

async def generate_llm_response(prompt: str, context: str = "", api_key: str = "") -> str:
    """Generate response from Gemini LLM"""
    try:
        # Use provided API key or built-in key
        gemini_key = api_key if api_key else BUILT_IN_GEMINI_KEY
        if not gemini_key:
            return """## ⚠️ API Key Required

To use the chatbot functionality, you need to provide a Google Gemini API key.

### How to get an API key:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it in the API key field

### Alternative:
You can also set the `GEMINI_API_KEY` environment variable in the backend for automatic usage."""
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Construct the full prompt with context
        full_prompt = f"""You are a helpful AI assistant. You MUST format your response using markdown syntax.

CRITICAL: Your response MUST start with ## and use proper markdown formatting throughout.

FORMATTING REQUIREMENTS:
- Start with ## for the main topic
- Use ### for subtopics
- Use **bold** for important terms
- Use - for bullet points
- Use 1. 2. 3. for numbered lists
- Use `backticks` for code/technical terms

CONTEXT: {context}

USER QUERY: {prompt}

RESPONSE FORMAT (copy this structure):
## [Main Topic Title]

### [Subtopic 1]
- **Key point 1**: Explanation
- **Key point 2**: More details

### [Subtopic 2]
1. **Step 1**: Description
2. **Step 2**: More details

Remember: Start with ## and use markdown formatting throughout your entire response."""
        response = model.generate_content(full_prompt)
        response_text = response.text
        
        # Post-process to ensure proper markdown formatting
        if not response_text.startswith('##'):
            # Restructure the response with proper markdown formatting
            lines = response_text.strip().split('\n')
            formatted_lines = []
            
            # Add main heading
            formatted_lines.append("## Object-Oriented Programming Explanation")
            formatted_lines.append("")
            
            # Process the content
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this looks like a section header
                if any(keyword in line.lower() for keyword in ['objects:', 'properties:', 'methods:', 'the power', 'in short', 'let\'s say']):
                    if current_section:
                        formatted_lines.append("")
                    formatted_lines.append(f"### {line}")
                    current_section = line
                else:
                    # Regular content line
                    if line.startswith('* '):
                        formatted_lines.append(line)
                    else:
                        formatted_lines.append(f"- {line}")
            
            response_text = '\n'.join(formatted_lines)
        
        return response_text
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/api/chat")
async def chat_with_llm(request: PromptRequest, http_request: Request):
    """Chat with LLM for test case guidance and refinement"""
    try:
        client_id = get_client_identifier(http_request)
        
        # Check usage limits
        usage_info = check_free_tier_usage(client_id)
        
        # Use provided API key or check free tier
        if not request.api_key and not usage_info["can_use"]:
            return PromptResponse(
                success=False,
                message="Daily free tier limit reached. Please provide your own API key.",
                response="",
                usage_info=usage_info
            )
        
        # Prepare context from current test cases
        context = ""
        if request.test_cases:
            context = f"Current test cases:\n"
            for i, tc in enumerate(request.test_cases[:5], 1):  # Limit to first 5 for context
                context += f"{i}. Feature: {tc.feature}\n   Scenario: {tc.scenario}\n   Priority: {tc.priority}\n\n"
        
        if request.context:
            context += f"\nAdditional context: {request.context}"
        
        # Generate LLM response
        response_text = await generate_llm_response(
            request.message, 
            context, 
            request.api_key or BUILT_IN_GEMINI_KEY
        )
        
        # Increment usage if using free tier
        if not request.api_key:
            increment_free_tier_usage(client_id)
            usage_info = check_free_tier_usage(client_id)
        
        return PromptResponse(
            success=True,
            message="Response generated successfully",
            response=response_text,
            usage_info=usage_info
        )
        
    except Exception as e:
        return PromptResponse(
            success=False,
            message=f"Error: {str(e)}",
            response="",
            usage_info=usage_info if 'usage_info' in locals() else {}
        )

@app.post("/api/refine-test-cases")
async def refine_test_cases(request: RefineTestCasesRequest, http_request: Request):
    """Refine existing test cases based on user feedback"""
    try:
        client_id = get_client_identifier(http_request)
        
        # Check usage limits
        usage_info = check_free_tier_usage(client_id)
        
        # Use provided API key or check free tier
        if not request.api_key and not usage_info["can_use"]:
            return PromptResponse(
                success=False,
                message="Daily free tier limit reached. Please provide your own API key.",
                response="",
                usage_info=usage_info
            )
        
        # Prepare context with current test cases
        context = "Current test cases to refine:\n"
        for i, tc in enumerate(request.test_cases, 1):
            context += f"{i}. ID: {tc.test_case_id}\n"
            context += f"   Feature: {tc.feature}\n"
            context += f"   Scenario: {tc.scenario}\n"
            context += f"   Test Steps: {tc.test_steps}\n"
            context += f"   Expected Result: {tc.expected_result}\n"
            context += f"   Priority: {tc.priority}\n"
            context += f"   Category: {tc.category}\n\n"
        
        # Create refinement prompt
        refinement_prompt = f"""Please help improve these test cases based on this feedback: "{request.refinement_prompt}"

{context}

RESPONSE FORMATTING REQUIREMENTS:
- Use clear markdown formatting with ## headings
- Organize suggestions into logical sections
- Use bullet points (-) for individual suggestions
- Use numbered lists (1.) for step-by-step improvements
- Use **bold** for important points
- Provide specific, actionable recommendations

Provide helpful suggestions for making these test cases clearer, more comprehensive, and more effective."""

        # Generate LLM response
        response_text = await generate_llm_response(
            refinement_prompt, 
            "", 
            request.api_key or BUILT_IN_GEMINI_KEY
        )
        
        # Increment usage if using free tier
        if not request.api_key:
            increment_free_tier_usage(client_id)
            usage_info = check_free_tier_usage(client_id)
        
        return PromptResponse(
            success=True,
            message="Test cases refined successfully",
            response=response_text,
            usage_info=usage_info
        )
        
    except Exception as e:
        return PromptResponse(
            success=False,
            message=f"Error refining test cases: {str(e)}",
            response="",
            usage_info=usage_info if 'usage_info' in locals() else {}
        )

# RAG Endpoints

@app.post("/api/upload-document", response_model=RAGUploadResponse)
async def upload_document_for_rag(
    request: Request,
    file: UploadFile = File(...)
):
    """Upload and process a document for RAG"""
    
    # Validate file type
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported for RAG functionality."
        )
    
    # Check rate limiting
    client_id = get_client_identifier(request)
    usage_info = check_free_tier_usage(client_id)
    
    if not usage_info["can_use"]:
        limit_text = "unlimited" if DEVELOPMENT_MODE else str(FREE_TIER_DAILY_LIMIT)
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit ({limit_text} uses) reached. Please try again tomorrow."
        )
    
    try:
        # Read and extract text from PDF
        file_content = await file.read()
        text_content = extract_text_from_pdf(file_content)
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the PDF")
        
        # Generate unique document ID
        document_id = f"doc_{int(datetime.now().timestamp())}_{hash(text_content[:100]) % 10000}"
        
        # Process document with RAG
        chunks_count = await rag_system.process_document(text_content, document_id)
        
        # Update usage tracking
        increment_free_tier_usage(client_id)
        updated_usage_info = check_free_tier_usage(client_id)
        
        if DEVELOPMENT_MODE:
            updated_usage_info["message"] = f"✅ Document processed! Development mode - unlimited usage"
        else:
            updated_usage_info["message"] = f"✅ Document processed! {updated_usage_info['remaining_today']} uses remaining today"
        
        return RAGUploadResponse(
            success=True,
            message=f"Document processed successfully into {chunks_count} chunks",
            document_id=document_id,
            chunks_count=chunks_count,
            usage_info=updated_usage_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/api/chat-with-document", response_model=RAGChatResponse)
async def chat_with_document(
    request: RAGChatRequest,
    http_request: Request
):
    """Chat with an uploaded document using RAG"""
    
    # Check rate limiting
    client_id = get_client_identifier(http_request)
    usage_info = check_free_tier_usage(client_id)
    
    # Use provided API key or check free tier
    if not request.api_key and not usage_info["can_use"]:
        return RAGChatResponse(
            success=False,
            message="Daily free tier limit reached. Please provide your own API key.",
            answer="",
            sources=[],
            usage_info=usage_info
        )
    
    try:
        # If no document_id specified, check if there's any document available
        if not request.document_id:
            if not rag_documents:
                raise HTTPException(status_code=400, detail="No document uploaded. Please upload a document first.")
            # Use the most recent document
            request.document_id = list(rag_documents.keys())[-1]
        
        # Search for relevant chunks
        relevant_chunks = rag_system.search_document(
            request.question, 
            request.document_id, 
            k=3
        )
        
        if not relevant_chunks:
            return RAGChatResponse(
                success=True,
                message="No relevant information found",
                answer="I cannot find relevant information in the document to answer your question.",
                sources=[],
                usage_info=usage_info
            )
        
        # Generate answer using RAG
        answer = await rag_system.generate_answer(
            request.question,
            relevant_chunks,
            request.api_key or BUILT_IN_GEMINI_KEY
        )
        
        # Update usage if using free tier
        if not request.api_key:
            increment_free_tier_usage(client_id)
            usage_info = check_free_tier_usage(client_id)
        
        return RAGChatResponse(
            success=True,
            message="Answer generated successfully",
            answer=answer,
            sources=relevant_chunks[:2],  # Return top 2 source chunks
            usage_info=usage_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return RAGChatResponse(
            success=False,
            message=f"Error: {str(e)}",
            answer="",
            sources=[],
            usage_info=usage_info if 'usage_info' in locals() else {}
        )

@app.get("/api/list-documents")
async def list_documents():
    """List all uploaded documents"""
    documents = []
    for doc_id in rag_documents.keys():
        documents.append({
            "document_id": doc_id,
            "chunks_count": len(rag_documents[doc_id].vectors)
        })
    
    return {
        "success": True,
        "documents": documents,
        "total_documents": len(documents)
    }

# Entry point for running the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
