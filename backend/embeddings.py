import chromadb
import openai
import os
from typing import List, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="articles",
            metadata={"hnsw:space": "cosine"}
        )
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding vector for text using OpenAI's text-embedding-3-small"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            raise e
    
    def add_article(self, article_id: int, content: str, metadata: dict) -> None:
        """Add article to ChromaDB collection"""
        try:
            # Create chunks for better retrieval
            chunks = self.chunk_text(content)
            
            # Add each chunk with article metadata
            for i, chunk in enumerate(chunks):
                embedding = self.create_embedding(chunk)
                chunk_id = f"article_{article_id}_chunk_{i}"
                
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        **metadata,
                        "article_id": article_id,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }],
                    ids=[chunk_id]
                )
        except Exception as e:
            print(f"Error adding article to ChromaDB: {e}")
            raise e
    
    def delete_article(self, article_id: int) -> None:
        """Delete all chunks of an article from ChromaDB"""
        try:
            # Get all chunks for this article
            results = self.collection.get(
                where={"article_id": article_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
        except Exception as e:
            print(f"Error deleting article from ChromaDB: {e}")
    
    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        """Split text into overlapping chunks with better sentence awareness"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                for punct in ['. ', '! ', '? ', '\n\n']:
                    last_punct = text.rfind(punct, start + chunk_size - 200, end)
                    if last_punct != -1:
                        end = last_punct + len(punct)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start forward, accounting for overlap
            start = max(start + chunk_size - overlap, end - overlap)
            
            if start >= len(text):
                break
        
        return chunks if chunks else [text]
    
    def search_similar_articles(self, query: str, user_id: int, limit: int = 5) -> List[Tuple[int, float, str]]:
        """
        Find most similar article chunks to query
        Returns: List of (article_id, similarity_score, content) tuples
        """
        try:
            query_embedding = self.create_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                where={"user_id": user_id},
                n_results=limit * 3,  # Get more results to deduplicate articles
                include=["documents", "metadatas", "distances"]
            )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            # Process results and deduplicate by article_id
            seen_articles = set()
            unique_results = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                article_id = metadata['article_id']
                
                if article_id not in seen_articles:
                    # Convert distance to similarity (ChromaDB returns distance, we want similarity)
                    similarity = 1 - distance
                    unique_results.append((article_id, float(similarity), doc))
                    seen_articles.add(article_id)
                    
                    if len(unique_results) >= limit:
                        break
            
            return unique_results
            
        except Exception as e:
            print(f"Error searching similar articles: {e}")
            return []
    
    def get_article_context(self, article_id: int, query: str = "", max_chunks: int = 4) -> str:
        """Get relevant context from article chunks for Q&A with query-based ranking"""
        try:
            if query:
                # Get query-relevant chunks by re-searching within this article
                query_embedding = self.create_embedding(query)
                
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    where={"article_id": article_id},
                    n_results=max_chunks * 2,  # Get more to select best ones
                    include=["documents", "distances"]
                )
                
                if results['documents'] and results['documents'][0]:
                    # Sort by relevance (distance) and take best chunks
                    chunk_pairs = list(zip(results['documents'][0], results['distances'][0]))
                    chunk_pairs.sort(key=lambda x: x[1])  # Sort by distance (lower is better)
                    
                    best_chunks = [doc for doc, _ in chunk_pairs[:max_chunks]]
                    return " ".join(best_chunks)
            
            # Fallback to original method if no query provided
            results = self.collection.get(
                where={"article_id": article_id},
                include=["documents", "metadatas"]
            )
            
            if not results['documents']:
                return ""
            
            # Sort chunks by chunk_id to maintain order and take first few
            if results['metadatas']:
                chunk_data = list(zip(results['documents'], results['metadatas']))
                chunk_data.sort(key=lambda x: x[1].get('chunk_id', 0))
                sorted_chunks = [doc for doc, _ in chunk_data[:max_chunks]]
                return " ".join(sorted_chunks)
            else:
                # Fallback without metadata
                chunks = results['documents'][:max_chunks]
                return " ".join(chunks)
            
        except Exception as e:
            print(f"Error getting article context: {e}")
            return ""

# Global instance
embedding_service = EmbeddingService()