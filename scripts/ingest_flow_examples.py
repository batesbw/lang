import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to Python path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.rag_tools import RAGManager

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_flow_examples():
    """
    Scans the 'examples/flows' directory, reads each flow XML file, and ingests it
    into the Supabase 'sample_flows' table using the RAGManager.
    """
    load_dotenv()

    # Verify that necessary environment variables are set
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "OPENAI_API_KEY"]
    if not all(os.getenv(var) for var in required_vars):
        logging.error("Essential environment variables are missing. Please check your .env file.")
        return

    logging.info("Initializing RAGManager...")
    rag_manager = RAGManager()

    if not rag_manager.supabase_client:
        logging.error("Failed to initialize RAGManager or Supabase client. Aborting.")
        return

    # Define the path to the golden examples directory
    examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples', 'flows'))
    
    if not os.path.isdir(examples_dir):
        logging.error(f"Examples directory not found at: {examples_dir}")
        return

    logging.info(f"Scanning for flow examples in {examples_dir}...")
    
    successful_upserts = 0
    total_files = 0

    for filename in os.listdir(examples_dir):
        if filename.endswith('.flow-meta.xml'):
            total_files += 1
            flow_name = os.path.splitext(filename)[0]

            file_path = os.path.join(examples_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()

                # The RAGManager method now handles upserting
                if rag_manager.add_sample_flow_from_xml(flow_name, xml_content):
                    successful_upserts += 1
                    logging.info(f"Successfully processed and upserted '{flow_name}'.")
                else:
                    logging.error(f"Failed to upsert '{flow_name}'.")

            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}")

    logging.info(f"Ingestion complete. Successfully processed {successful_upserts}/{total_files} flow examples.")

if __name__ == "__main__":
    ingest_flow_examples() 