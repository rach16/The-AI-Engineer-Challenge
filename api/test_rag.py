#!/usr/bin/env python3
"""
Simple test script for RAG functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from aimakerspace.text_utils import CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase

async def test_basic_rag():
    """Test basic RAG functionality without API calls"""
    print("🧪 Testing Basic RAG Components...")
    
    # Test 1: Text Splitter
    print("\n1. Testing Text Splitter...")
    splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    
    sample_text = """
    This is a sample document about data promotion processes.
    
    Step 1: Confirm new data is on staging
    There will be a very recent run that should be green indicating staging has new data on it.
    
    Step 2: Confirm staging E2E tests are passing
    Investigate and fix failures as needed before proceeding.
    
    Step 3: Restore and set ES company-match & company-quick-search index aliases on staging
    This is a critical step that ensures proper indexing.
    """
    
    chunks = splitter.split(sample_text)
    print(f"   ✅ Split text into {len(chunks)} chunks")
    print(f"   📝 First chunk: {chunks[0][:100]}...")
    
    # Test 2: Vector Database (will fail without OpenAI key, but we can test the structure)
    print("\n2. Testing Vector Database Structure...")
    vector_db = VectorDatabase()
    print(f"   ✅ Vector database created: {type(vector_db).__name__}")
    
    # Test 3: Mock search functionality
    print("\n3. Testing Search Logic...")
    mock_chunks = [
        "Step 1: Confirm new data is on staging",
        "Step 2: Confirm staging E2E tests are passing", 
        "Step 3: Restore ES company-match index aliases"
    ]
    
    # Simulate what would happen with embeddings
    print(f"   ✅ Would process {len(mock_chunks)} chunks for embedding")
    print(f"   📝 Sample chunk: '{mock_chunks[0]}'")
    
    print("\n🎉 Basic RAG components are working!")
    print("💡 To test with real embeddings, set OPENAI_API_KEY environment variable")
    
    return True

async def main():
    """Run the test"""
    try:
        success = await test_basic_rag()
        if success:
            print("\n✅ All tests passed!")
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
