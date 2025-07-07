import hashlib
from datetime import datetime
from pathlib import Path
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

DATA_DIR = Path("data")
DB_DIR = Path("knowledge_db") 
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "llama3.2"
BATCH_SIZE = 100

OllamaEmbeddings

class MarkdownKnowledgeETL:
    """ETL pipeline for markdown knowledge base."""
    def __init__(self):
        self.data_dir = DATA_DIR
        self.db_dir = DB_DIR
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP
        self.ollama_url = OLLAMA_URL
        self.embedding_model = EMBEDDING_MODEL
        
        self.embeddings = OllamaEmbeddings(
            base_url=self.ollama_url,
            model=self.embedding_model
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_markdown_files(self) -> List[Document]:
        """Extract all markdown files from the data directory."""
        logger.info(f"Extracting markdown files from {self.data_dir}")
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        loader = DirectoryLoader(
            str(self.data_dir),
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader,
            show_progress=True,
            use_multithreading=True
        )
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} markdown documents")
        
        for doc in documents:
            file_path = Path(doc.metadata.get("source", ""))
            doc.metadata.update({
                "file_name": file_path.name,
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.data_dir)),
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
                "modified_time": datetime.fromtimestamp(
                    file_path.stat().st_mtime if file_path.exists() else 0
                ).isoformat(),
                "extracted_at": datetime.now().isoformat()
            })
        
        return documents
    
    def transform_documents(self, documents: List[Document]) -> List[Document]:
        """Transform documents by chunking and enriching metadata."""
        logger.info("Transforming documents: chunking and enriching metadata")
        
        all_chunks = []
        
        for doc in documents:
            chunks = self.text_splitter.split_documents([doc])
            
            # Enrich each chunk with additional metadata
            for i, chunk in enumerate(chunks):
                # Create unique chunk ID
                content_hash = hashlib.md5(chunk.page_content.encode()).hexdigest()
                chunk_id = f"{doc.metadata['file_name']}_{i}_{content_hash[:8]}"
                
                chunk.metadata.update({
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk.page_content),
                    "doc_type": "markdown",
                    "processing_timestamp": datetime.now().isoformat()
                })
                
                all_chunks.append(chunk)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def load_to_chromadb(self, chunks: List[Document]) -> Chroma:
        """Load chunks into ChromaDB vector store."""
        logger.info(f"Loading {len(chunks)} chunks into ChromaDB at {self.db_dir}")
        
        # Ensure database directory exists
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create or load existing ChromaDB
        vectorstore = Chroma(
            persist_directory=str(self.db_dir),
            embedding_function=self.embeddings,
            collection_name="knowledge_base"
        )
        
        # Check for existing documents to avoid duplicates
        existing_ids = set()
        try:
            existing_collection = vectorstore.get()
            if existing_collection and existing_collection.get("metadatas"):
                existing_ids = {
                    metadata.get("chunk_id") 
                    for metadata in existing_collection["metadatas"] 
                    if metadata.get("chunk_id")
                }
                logger.info(f"Found {len(existing_ids)} existing chunks in database")
        except Exception as e:
            logger.warning(f"Could not check existing documents: {e}")
        
        # Filter out existing chunks
        new_chunks = [
            chunk for chunk in chunks 
            if chunk.metadata.get("chunk_id") not in existing_ids
        ]
        
        if not new_chunks:
            logger.info("No new chunks to add - all documents already exist")
            return vectorstore
        
        logger.info(f"Adding {len(new_chunks)} new chunks to database")
        
        # Add documents in batches to avoid memory issues
        for i in range(0, len(new_chunks), BATCH_SIZE):
            batch = new_chunks[i:i + BATCH_SIZE]
            batch_texts = [chunk.page_content for chunk in batch]
            batch_metadatas = [chunk.metadata for chunk in batch]
            batch_ids = [chunk.metadata["chunk_id"] for chunk in batch]
            
            vectorstore.add_texts(
                texts=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            
            logger.info(f"Added batch {i//BATCH_SIZE + 1}/{(len(new_chunks)-1)//BATCH_SIZE + 1}")
        
        # Persist the database
        vectorstore.persist()
        logger.info("Successfully persisted vector database")
        
        return vectorstore
    
    def run_etl(self) -> Dict[str, Any]:
        """Run the complete ETL pipeline."""
        logger.info("Starting Knowledge Base ETL Pipeline")
        start_time = datetime.now()
        
        try:
            documents = self.extract_markdown_files()

            chunks = self.transform_documents(documents)
            
            vectorstore = self.load_to_chromadb(chunks)
            
            collection = vectorstore.get()

            total_chunks = len(collection["ids"]) if collection and collection.get("ids") else 0
            
            end_time = datetime.now()

            duration = (end_time - start_time).total_seconds()
            
            stats = {
                "status": "success",
                "duration_seconds": duration,
                "documents_processed": len(documents),
                "chunks_created": len(chunks),
                "total_chunks_in_db": total_chunks,
                "database_path": str(self.db_dir),
                "completed_at": end_time.isoformat()
            }
            
            logger.info(f"ETL Pipeline completed successfully in {duration:.2f}s")
            logger.info(f"Final stats: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

def print_results(result: Dict[str, Any]):
    """Print the results of the ETL process."""
    if result["status"] == "success":
        print(f"\nETL completed successfully!")
        print(f"Processed {result['documents_processed']} documents")
        print(f"Created {result['chunks_created']} chunks")
        print(f"Total chunks in database: {result['total_chunks_in_db']}")
        print(f"Duration: {result['duration_seconds']:.2f}s")
        print(f"Database location: {result['database_path']}")
    else:
        print(f"\nETL failed: {result['error']}")
        exit(1)

def main():
    """Main entry point for the ETL script."""
    etl = MarkdownKnowledgeETL()
    result = etl.run_etl()
    print_results(result)


if __name__ == "__main__":
    main()
