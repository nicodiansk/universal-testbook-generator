"""
Vector database integration for the Universal Testbook Generator.
Handles embedding generation, vector storage, and similarity search using Pinecone and OpenAI.
"""

import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from loguru import logger

from ..models.document_models import DocumentChunk, StructuredDocument
from ..config.settings import settings

@dataclass
class SearchResult:
    """Result from vector similarity search."""
    chunk: DocumentChunk
    score: float
    metadata: Dict[str, Any]

class VectorDatabase:
    """Vector database manager using Pinecone and OpenAI embeddings."""
    
    def __init__(self):
        self.openai_client = None
        self.pinecone_client = None
        self.index = None
        self.index_name = "testbook-generator"
        self.embedding_model = settings.default_embedding_model
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small dimension
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize OpenAI and Pinecone clients."""
        try:
            # Initialize OpenAI client
            if settings.openai_api_key:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not found in settings")
            
            # Initialize Pinecone client
            if settings.pinecone_api_key:
                self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
                logger.info("Pinecone client initialized successfully")
            else:
                logger.warning("Pinecone API key not found in settings")
                
        except Exception as e:
            logger.error(f"Error initializing clients: {str(e)}")
            raise
    
    def ensure_index_exists(self) -> bool:
        """
        Ensure the Pinecone index exists, create if necessary.
        
        Returns:
            bool: True if index exists or was created successfully
        """
        try:
            if not self.pinecone_client:
                logger.error("Pinecone client not initialized")
                return False
            
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pinecone_client.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                
                # Create serverless index
                self.pinecone_client.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-west-2"
                    )
                )
                
                # Wait for index to be ready
                while not self.pinecone_client.describe_index(self.index_name).status['ready']:
                    logger.info("Waiting for index to be ready...")
                    time.sleep(1)
                
                logger.info(f"Index {self.index_name} created successfully")
            
            # Connect to index
            self.index = self.pinecone_client.Index(self.index_name)
            logger.info(f"Connected to index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring index exists: {str(e)}")
            return False
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not initialized")
            
            if not texts:
                return []
            
            logger.info(f"Generating embeddings for {len(texts)} texts using {self.embedding_model}")
            
            # Generate embeddings
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings successfully")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def upsert_document(self, document: StructuredDocument, namespace: str = "default") -> bool:
        """
        Store document chunks in the vector database.
        
        Args:
            document: The structured document to store
            namespace: Pinecone namespace for organization
            
        Returns:
            bool: Success status
        """
        try:
            if not self.ensure_index_exists():
                return False
            
            if not document.chunks:
                logger.warning(f"No chunks found in document {document.id}")
                return True
            
            logger.info(f"Upserting document {document.id} with {len(document.chunks)} chunks")
            
            # Prepare texts for embedding
            texts = [chunk.content for chunk in document.chunks]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            if len(embeddings) != len(document.chunks):
                raise ValueError("Mismatch between embeddings and chunks count")
            
            # Prepare vectors for upsert
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(document.chunks, embeddings)):
                vector_id = f"{document.id}_{chunk.id}"
                
                metadata = {
                    "document_id": document.id,
                    "document_title": document.title or document.filename,
                    "chunk_id": chunk.id,
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "section": chunk.section,
                    "word_count": chunk.metadata.get("word_count", 0),
                    "char_count": chunk.metadata.get("char_count", 0)
                }
                
                vectors.append((vector_id, embedding, metadata))
            
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully upserted document {document.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting document {document.id}: {str(e)}")
            return False
    
    def search_similar_chunks(
        self, 
        query: str, 
        top_k: int = 5, 
        namespace: str = "default",
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar document chunks.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            namespace: Pinecone namespace to search in
            filter_dict: Optional metadata filters
            
        Returns:
            List of search results with similarity scores
        """
        try:
            if not self.index:
                logger.error("Index not initialized")
                return []
            
            logger.info(f"Searching for similar chunks: '{query[:50]}...' (top_k={top_k})")
            
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Perform search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict,
                include_values=True,
                include_metadata=True
            )
            
            # Convert to SearchResult objects
            search_results = []
            for match in results.matches:
                metadata = match.metadata
                
                # Reconstruct document chunk
                chunk = DocumentChunk(
                    id=metadata.get("chunk_id", str(uuid.uuid4())),
                    content=metadata.get("content", ""),
                    page_number=metadata.get("page_number"),
                    section=metadata.get("section"),
                    metadata={
                        "word_count": metadata.get("word_count", 0),
                        "char_count": metadata.get("char_count", 0)
                    }
                )
                
                search_result = SearchResult(
                    chunk=chunk,
                    score=match.score,
                    metadata={
                        "document_id": metadata.get("document_id"),
                        "document_title": metadata.get("document_title"),
                        "vector_id": match.id
                    }
                )
                
                search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} similar chunks")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            return []
    
    def search_by_document(
        self, 
        query: str, 
        document_id: str, 
        top_k: int = 5, 
        namespace: str = "default"
    ) -> List[SearchResult]:
        """
        Search within a specific document.
        
        Args:
            query: Search query text
            document_id: Document ID to search within
            top_k: Number of results to return
            namespace: Pinecone namespace to search in
            
        Returns:
            List of search results from the specific document
        """
        filter_dict = {"document_id": {"$eq": document_id}}
        return self.search_similar_chunks(query, top_k, namespace, filter_dict)
    
    def get_document_chunks(self, document_id: str, namespace: str = "default") -> List[DocumentChunk]:
        """
        Retrieve all chunks for a specific document.
        
        Args:
            document_id: Document ID
            namespace: Pinecone namespace
            
        Returns:
            List of document chunks
        """
        try:
            # Search with a dummy query to get all chunks for the document
            filter_dict = {"document_id": {"$eq": document_id}}
            
            results = self.index.query(
                vector=[0.0] * self.embedding_dimension,  # Dummy vector
                top_k=1000,  # Large number to get all chunks
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            chunks = []
            for match in results.matches:
                metadata = match.metadata
                chunk = DocumentChunk(
                    id=metadata.get("chunk_id", str(uuid.uuid4())),
                    content=metadata.get("content", ""),
                    page_number=metadata.get("page_number"),
                    section=metadata.get("section"),
                    metadata={
                        "word_count": metadata.get("word_count", 0),
                        "char_count": metadata.get("char_count", 0)
                    }
                )
                chunks.append(chunk)
            
            logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving document chunks: {str(e)}")
            return []
    
    def delete_document(self, document_id: str, namespace: str = "default") -> bool:
        """
        Delete all vectors for a specific document.
        
        Args:
            document_id: Document ID to delete
            namespace: Pinecone namespace
            
        Returns:
            bool: Success status
        """
        try:
            if not self.index:
                logger.error("Index not initialized")
                return False
            
            logger.info(f"Deleting document {document_id} from vector database")
            
            # Delete by metadata filter
            self.index.delete(
                filter={"document_id": {"$eq": document_id}},
                namespace=namespace
            )
            
            logger.info(f"Successfully deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    def get_index_stats(self, namespace: str = "default") -> Dict[str, Any]:
        """
        Get statistics about the vector index.
        
        Args:
            namespace: Pinecone namespace
            
        Returns:
            Dictionary with index statistics
        """
        try:
            if not self.index:
                return {"error": "Index not initialized"}
            
            stats = self.index.describe_index_stats()
            
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespace_count": len(stats.namespaces) if stats.namespaces else 0,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check the health of all connections.
        
        Returns:
            Dictionary with health status of each component
        """
        health = {
            "openai_client": False,
            "pinecone_client": False,
            "index_connection": False
        }
        
        try:
            # Check OpenAI
            if self.openai_client:
                # Try a simple embedding request
                self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=["health check"]
                )
                health["openai_client"] = True
        except:
            pass
        
        try:
            # Check Pinecone
            if self.pinecone_client:
                self.pinecone_client.list_indexes()
                health["pinecone_client"] = True
        except:
            pass
        
        try:
            # Check index
            if self.index:
                self.index.describe_index_stats()
                health["index_connection"] = True
        except:
            pass
        
        return health