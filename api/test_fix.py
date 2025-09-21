#!/usr/bin/env python3
"""
Test script to verify the RAG API key fix works correctly.
"""

import os
import sys
from aimakerspace.gemini_utils.embedding import GeminiEmbeddingModel
from dotenv import load_dotenv

def test_embedding_with_api_key():
    """Test that GeminiEmbeddingModel accepts API keys properly"""
    load_dotenv()
    
    # Get the API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return False
    
    try:
        # Test 1: Default initialization (should use env var)
        print("🔍 Testing default initialization...")
        embedding_model_1 = GeminiEmbeddingModel()
        print("✅ Default initialization successful")
        
        # Test 2: Explicit API key initialization
        print("🔍 Testing explicit API key initialization...")
        embedding_model_2 = GeminiEmbeddingModel(api_key=api_key)
        print("✅ Explicit API key initialization successful")
        
        # Test 3: Generate a simple embedding to ensure it works
        print("🔍 Testing embedding generation...")
        test_text = "This is a test document for RAG functionality."
        embedding = embedding_model_2.get_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            return True
        else:
            print("❌ Failed to generate valid embedding")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing RAG API key fix...")
    print("=" * 50)
    
    success = test_embedding_with_api_key()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! The fix should work correctly.")
        sys.exit(0)
    else:
        print("💥 Tests failed. There might be an issue.")
        sys.exit(1)
