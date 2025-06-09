import os
import sys
from dotenv import load_dotenv
import logging

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.rag_tools import RAGManager
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_flow_documentation():
    """
    Loads Flow.md, splits it into chunks, and ingests them into the Supabase vector store.
    """
    load_dotenv()
    
    # Check for necessary environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "OPENAI_API_KEY"]
    if not all(os.getenv(var) for var in required_vars):
        logging.error("Missing one or more required environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY")
        return

    logging.info("Initializing RAGManager...")
    rag_manager = RAGManager()
    
    if not rag_manager.vector_store:
        logging.error("Failed to initialize RAGManager or its vector store. Aborting.")
        return

    doc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'documentation', 'Flow.md'))
    
    if not os.path.exists(doc_path):
        logging.error(f"Documentation file not found at: {doc_path}")
        return

    logging.info(f"Loading documentation from {doc_path}...")
    loader = UnstructuredMarkdownLoader(doc_path)
    documents = loader.load()

    logging.info("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    logging.info(f"Created {len(chunks)} document chunks.")

    logging.info("Starting ingestion into Supabase...")
    successful_ingestions = 0
    for i, chunk in enumerate(chunks):
        metadata = {
            "source": "Flow.md",
            "chunk_number": i + 1,
            **chunk.metadata  # Add any metadata from the loader
        }
        
        # The add_documentation method in RAGManager expects content and metadata
        if rag_manager.add_documentation(content=chunk.page_content, metadata=metadata):
            successful_ingestions += 1
            logging.info(f"Successfully ingested chunk {i+1}/{len(chunks)}")
        else:
            logging.error(f"Failed to ingest chunk {i+1}/{len(chunks)}")

    logging.info(f"Ingestion complete. Successfully ingested {successful_ingestions}/{len(chunks)} chunks.")

if __name__ == "__main__":
    ingest_flow_documentation() 