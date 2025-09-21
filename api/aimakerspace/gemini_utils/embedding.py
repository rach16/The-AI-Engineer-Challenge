import asyncio
import os
from typing import Iterable, List

import google.generativeai as genai
from dotenv import load_dotenv


class GeminiEmbeddingModel:
    """Helper for generating embeddings via the Google Gemini API."""

    def __init__(self, embeddings_model_name: str = "models/text-embedding-004"):
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key is None:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Please configure it with your Gemini API key."
            )

        self.embeddings_model_name = embeddings_model_name
        genai.configure(api_key=self.gemini_api_key)

    async def async_get_embeddings(self, list_of_text: Iterable[str]) -> List[List[float]]:
        """Return embeddings for ``list_of_text`` using Gemini API."""
        embeddings = []
        
        # Process each text individually (Gemini API handles one at a time)
        for text in list_of_text:
            embedding = await self.async_get_embedding(text)
            embeddings.append(embedding)
        
        return embeddings

    async def async_get_embedding(self, text: str) -> List[float]:
        """Return an embedding for a single text using Gemini API."""
        try:
            # Use Gemini's embed_content method
            result = genai.embed_content(
                model=self.embeddings_model_name,
                content=text,
                task_type="retrieval_document"  # Optimize for document retrieval
            )
            return result['embedding']
        except Exception as e:
            print(f"Error getting Gemini embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 768  # Standard embedding dimension

    def get_embeddings(self, list_of_text: Iterable[str]) -> List[List[float]]:
        """Return embeddings for ``list_of_text`` using Gemini API (sync)."""
        embeddings = []
        
        for text in list_of_text:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        
        return embeddings

    def get_embedding(self, text: str) -> List[float]:
        """Return an embedding for a single text using Gemini API (sync)."""
        try:
            result = genai.embed_content(
                model=self.embeddings_model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error getting Gemini embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 768


if __name__ == "__main__":
    embedding_model = GeminiEmbeddingModel()
    print(asyncio.run(embedding_model.async_get_embedding("Hello, world!")))
    print(
        asyncio.run(
            embedding_model.async_get_embeddings(["Hello, world!", "Goodbye, world!"])
        )
    )
