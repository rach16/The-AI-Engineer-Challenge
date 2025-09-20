#!/usr/bin/env python3
"""
Test script for Gemini RAG functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from aimakerspace.text_utils import CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.gemini_utils.embedding import GeminiEmbeddingModel

async def test_gemini_rag():
    """Test Gemini RAG functionality"""
    print("🧪 Testing Gemini RAG Components...")
    
    # Check if Gemini API key is set
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY environment variable not set!")
        print("💡 Set it with: export GEMINI_API_KEY='your-key-here'")
        return False
    
    print(f"✅ GEMINI_API_KEY is set (first 10 chars: {gemini_key[:10]}...)")
    
    # Test 1: Text Splitter
    print("\n1. Testing Text Splitter...")
    splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    
    sample_text = """
    Step 1: Confirm new data is on staging
    There will be a very recent run that should be green indicating staging has new data on it.
    
    Step 2: Confirm staging E2E tests are passing
    Investigate and fix failures as needed before proceeding.
    
    Step 3: Restore and set ES company-match & company-quick-search index aliases on staging
    This is a critical step that ensures proper indexing.
    
    ATTENTION: Make sure to wait for completion before proceeding to the next step.
    """
    
    chunks = splitter.split(sample_text)
    print(f"   ✅ Split text into {len(chunks)} chunks")
    print(f"   📝 First chunk: {chunks[0][:100]}...")
    
    # Test 2: Gemini Embedding Model
    print("\n2. Testing Gemini Embedding Model...")
    try:
        embedding_model = GeminiEmbeddingModel()
        print("   ✅ Gemini embedding model created")
        
        # Test single embedding
        test_text = "What is the first step in the process?"
        embedding = await embedding_model.async_get_embedding(test_text)
        print(f"   ✅ Generated embedding of length: {len(embedding)}")
        print(f"   📊 Sample embedding values: {embedding[:5]}...")
        
    except Exception as e:
        print(f"   ❌ Error with Gemini embeddings: {e}")
        return False
    
    # Test 3: Vector Database with Gemini
    print("\n3. Testing Vector Database with Gemini...")
    try:
        vector_db = VectorDatabase(embedding_model=GeminiEmbeddingModel())
        
        # Build from chunks
        print("   🔄 Building vector database from chunks...")
        vector_db = await vector_db.abuild_from_list(chunks[:3])  # Use first 3 chunks
        print(f"   ✅ Vector database built with {len(vector_db.vectors)} entries")
        
        # Test search
        query = "What should I do first?"
        print(f"   🔍 Searching for: '{query}'")
        results = vector_db.search_by_text(query, k=2, return_as_text=True)
        print(f"   ✅ Found {len(results)} relevant results")
        
        for i, result in enumerate(results, 1):
            print(f"   📝 Result {i}: {result[:80]}...")
        
    except Exception as e:
        print(f"   ❌ Error with vector database: {e}")
        return False
    
    print("\n🎉 All Gemini RAG tests passed!")
    print("💡 Your system is ready to use with Gemini API only!")
    
    return True

async def main():
    """Run the test"""
    try:
        success = await test_gemini_rag()
        if success:
            print("\n✅ Gemini RAG system is working!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
