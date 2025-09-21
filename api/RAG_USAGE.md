# 📚 Simple RAG System Usage Guide

Welcome to your new RAG (Retrieval-Augmented Generation) system! This guide shows you how to upload documents and chat with them.

## 🚀 Quick Start

### 1. Start the Server
```bash
cd api/
export OPENAI_API_KEY="your-openai-key-here"
uvicorn app:app --reload
```

### 2. Upload a Document
**Endpoint:** `POST /api/upload-document`

```bash
curl -X POST "http://localhost:8000/api/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf"
```

**Response:**
```json
{
  "success": true,
  "message": "Document processed successfully into 15 chunks",
  "document_id": "doc_1695123456_7890",
  "chunks_count": 15,
  "usage_info": {
    "tier": "development",
    "daily_limit": "unlimited",
    "used_today": 1,
    "remaining_today": "unlimited",
    "can_use": true
  }
}
```

### 3. Chat with Your Document
**Endpoint:** `POST /api/chat-with-document`

```bash
curl -X POST "http://localhost:8000/api/chat-with-document" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main steps in the process?",
    "document_id": "doc_1695123456_7890"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Answer generated successfully",
  "answer": "Based on the document, the main steps in the process are: 1. Confirm new data is on staging, 2. Confirm staging E2E tests are passing, 3. Restore and set ES index aliases...",
  "sources": [
    "Step 1: Confirm new data is on staging\nThere will be a very recent run that should be green...",
    "Step 2: Confirm staging E2E tests are passing\nInvestigate and fix failures as needed..."
  ],
  "usage_info": {...}
}
```

## 🎯 Perfect for Your Data Promotion Guide!

This system is ideal for your complex process documents like the **CH Data Promotion Process Guide**. Here are some example questions you could ask:

### 📝 Sample Questions
- *"What's the first step in data promotion?"*
- *"What should I do after creating the clickhouse cluster?"*
- *"What are the important warnings I need to know?"*
- *"How long does hydration take?"*
- *"Show me the ArgoCD sync process"*
- *"What happens if something goes wrong during DNS swap?"*

### 🔍 Smart Features
- **Automatic chunking** preserves document structure
- **Context-aware answers** using relevant document sections
- **Source citations** show which parts of the document were used
- **Rate limiting** built-in for production use

## 🛠️ API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|---------|---------|
| `/api/upload-document` | POST | Upload and process a PDF for RAG |
| `/api/chat-with-document` | POST | Ask questions about uploaded documents |
| `/api/list-documents` | GET | See all uploaded documents |
| `/api/health` | GET | Check system status |

## 💡 Tips for Best Results

### 📄 Document Preparation
- **Use clear PDFs** with extractable text (no scanned images)
- **Well-structured documents** work best (headings, numbered steps)
- **Process documents** are perfect (like your data promotion guide)

### ❓ Question Asking
- **Be specific**: "What's step 5?" vs "Tell me about steps"
- **Ask about concepts**: "How do I sync ArgoCD?" 
- **Reference specifics**: "What warnings are there for DNS changes?"

### 🚀 Advanced Usage
```json
{
  "question": "What should I do if hydration fails?",
  "document_id": "doc_1695123456_7890",
  "api_key": "your-personal-openai-key"  // Optional: use your own key
}
```

## 🔧 Development Mode

The system runs in **development mode** by default with:
- ✅ **Unlimited usage** for testing
- 🔍 **Detailed logging** for debugging
- 🚀 **Fast iteration** for development

## 🌟 Next Steps

1. **Upload your CH Data Promotion Process Guide**
2. **Test with common questions your team asks**
3. **Integrate with your frontend** for a complete UI
4. **Add more process documents** to build a knowledge base

---

**🎉 Happy RAG-ing!** Transform your static documentation into an interactive assistant!
