#!/usr/bin/env python3
"""
Script to add Salesforce Metadata API documentation from PDF to the RAG database

This script extracts specific metadata types from the official Salesforce 
Metadata API PDF and adds them to the knowledge base with intelligent chunking.
"""

import os
import sys
import asyncio
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import tiktoken

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.tools.rag_tools import rag_manager

# Import PDF processing
try:
    import PyPDF2
    import requests
except ImportError:
    print("Missing required packages. Installing...")
    os.system("pip install PyPDF2 requests")
    import PyPDF2
    import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SalesforceMetadataPDFProcessor:
    """Processes Salesforce Metadata API PDF with intelligent chunking"""
    
    def __init__(self, pdf_path: str = "salesforce_api_meta.pdf"):
        self.pdf_path = pdf_path
        self.pdf_url = "https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/api_meta.pdf"
        self.encoding = tiktoken.get_encoding('cl100k_base')  # GPT-4 tokenizer
        self.target_chunk_size = 1500  # Target tokens per chunk
        self.max_chunk_size = 2500     # Maximum tokens per chunk
        self.overlap_size = 200        # Overlap between chunks
        
    async def download_pdf(self) -> bool:
        """Download the Salesforce Metadata API PDF if not exists"""
        if os.path.exists(self.pdf_path):
            logger.info(f"PDF already exists: {self.pdf_path}")
            return True
            
        logger.info(f"Downloading PDF from: {self.pdf_url}")
        try:
            response = requests.get(self.pdf_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(self.pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            file_size = os.path.getsize(self.pdf_path) / (1024 * 1024)
            logger.info(f"✅ Downloaded PDF: {file_size:.1f} MB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download PDF: {str(e)}")
            return False
    
    def extract_table_of_contents(self) -> Dict[str, int]:
        """Extract table of contents to find metadata type locations"""
        logger.info("📖 Extracting table of contents...")
        
        toc = {}
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Scan first 50 pages for TOC entries
                for page_num in range(min(50, len(reader.pages))):
                    page_text = reader.pages[page_num].extract_text()
                    
                    # Look for metadata type entries (CapitalizedWord followed by dots and page number)
                    toc_pattern = r'^([A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]*)*)\s*\.{3,}\s*(\d+)$'
                    
                    for line in page_text.split('\n'):
                        line = line.strip()
                        match = re.match(toc_pattern, line)
                        if match:
                            metadata_type = match.group(1)
                            page_number = int(match.group(2))
                            
                            # Filter for actual metadata types (avoid section headers)
                            if (len(metadata_type) > 2 and 
                                not metadata_type in ['Contents', 'Introduction', 'Overview', 'Index'] and
                                page_number > 50):  # Metadata types start after intro sections
                                toc[metadata_type] = page_number
                                
                logger.info(f"✅ Found {len(toc)} metadata types in TOC")
                
                # Show some examples
                examples = list(toc.items())[:10]
                for name, page in examples:
                    logger.info(f"  - {name}: page {page}")
                    
                return toc
                
        except Exception as e:
            logger.error(f"❌ Failed to extract TOC: {str(e)}")
            return {}
    
    def get_available_metadata_types(self) -> List[str]:
        """Get list of available metadata types from TOC"""
        toc = self.extract_table_of_contents()
        
        # Filter for Flow-related and common metadata types
        flow_related = [name for name in toc.keys() if 'flow' in name.lower()]
        common_types = [name for name in toc.keys() if name in [
            'Flow', 'CustomObject', 'ApexClass', 'Layout', 'Profile', 
            'PermissionSet', 'CustomField', 'Workflow', 'ValidationRule'
        ]]
        
        # Combine and deduplicate
        priority_types = list(dict.fromkeys(flow_related + common_types))
        all_types = list(toc.keys())
        
        logger.info(f"Priority metadata types found: {priority_types}")
        return all_types, priority_types
    
    def extract_metadata_type_content(self, metadata_type: str, toc: Dict[str, int]) -> str:
        """Extract content for a specific metadata type"""
        if metadata_type not in toc:
            logger.warning(f"Metadata type '{metadata_type}' not found in TOC")
            return ""
            
        start_page = toc[metadata_type]
        
        # Find end page (next metadata type or end of document)
        sorted_types = sorted(toc.items(), key=lambda x: x[1])
        end_page = None
        
        for i, (name, page) in enumerate(sorted_types):
            if name == metadata_type and i + 1 < len(sorted_types):
                end_page = sorted_types[i + 1][1]
                break
                
        logger.info(f"📄 Extracting {metadata_type}: pages {start_page}-{end_page or 'end'}")
        
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                content = ""
                
                actual_end = min(end_page or len(reader.pages), len(reader.pages))
                
                for page_num in range(start_page - 1, actual_end - 1):  # Convert to 0-based
                    if page_num < len(reader.pages):
                        page_text = reader.pages[page_num].extract_text()
                        content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                logger.info(f"✅ Extracted {len(content)} characters for {metadata_type}")
                return content
                
        except Exception as e:
            logger.error(f"❌ Failed to extract content for {metadata_type}: {str(e)}")
            return ""
    
    def chunk_content(self, content: str, metadata_type: str) -> List[Dict[str, Any]]:
        """Intelligently chunk content with semantic boundaries"""
        if not content.strip():
            return []
            
        logger.info(f"🔪 Chunking {metadata_type} content...")
        
        chunks = []
        
        # Split by semantic boundaries (page breaks, major headings)
        sections = re.split(r'\n--- Page \d+ ---\n', content)
        
        current_chunk = ""
        current_tokens = 0
        chunk_num = 1
        
        for section in sections:
            if not section.strip():
                continue
                
            section_tokens = len(self.encoding.encode(section))
            
            # If section is too large, split by paragraphs
            if section_tokens > self.max_chunk_size:
                paragraphs = section.split('\n\n')
                for paragraph in paragraphs:
                    para_tokens = len(self.encoding.encode(paragraph))
                    
                    if current_tokens + para_tokens > self.target_chunk_size and current_chunk:
                        # Save current chunk
                        chunks.append(self._create_chunk(current_chunk, metadata_type, chunk_num))
                        chunk_num += 1
                        
                        # Start new chunk with overlap
                        current_chunk = self._get_overlap(current_chunk) + paragraph
                        current_tokens = len(self.encoding.encode(current_chunk))
                    else:
                        current_chunk += f"\n\n{paragraph}"
                        current_tokens += para_tokens
            
            # If adding entire section would exceed target, save current chunk
            elif current_tokens + section_tokens > self.target_chunk_size and current_chunk:
                chunks.append(self._create_chunk(current_chunk, metadata_type, chunk_num))
                chunk_num += 1
                
                # Start new chunk with overlap
                current_chunk = self._get_overlap(current_chunk) + section
                current_tokens = len(self.encoding.encode(current_chunk))
            else:
                current_chunk += section
                current_tokens += section_tokens
        
        # Save final chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, metadata_type, chunk_num))
        
        logger.info(f"✅ Created {len(chunks)} chunks for {metadata_type}")
        return chunks
    
    def _create_chunk(self, content: str, metadata_type: str, chunk_num: int) -> Dict[str, Any]:
        """Create a chunk with metadata"""
        token_count = len(self.encoding.encode(content))
        
        return {
            "content": content.strip(),
            "metadata": {
                "title": f"Salesforce {metadata_type} Metadata Documentation - Part {chunk_num}",
                "metadata_type": metadata_type,
                "chunk_number": chunk_num,
                "token_count": token_count,
                "source": "Salesforce Metadata API PDF",
                "document_type": "official_documentation",
                "content_type": "metadata_specification",
                "tags": ["salesforce", "metadata", metadata_type.lower(), "api", "xml"],
                "extraction_method": "PDF Processing with Semantic Chunking"
            }
        }
    
    def _get_overlap(self, text: str) -> str:
        """Get overlap text for context continuity"""
        sentences = text.split('. ')
        if len(sentences) <= 2:
            return text
            
        # Take last few sentences for overlap
        overlap_sentences = sentences[-2:]
        overlap = '. '.join(overlap_sentences)
        
        # Ensure overlap doesn't exceed overlap size
        overlap_tokens = len(self.encoding.encode(overlap))
        if overlap_tokens > self.overlap_size:
            return text[-self.overlap_size:]
            
        return overlap + "\n\n"

def get_user_metadata_types() -> List[str]:
    """Get metadata types to process from user input"""
    processor = SalesforceMetadataPDFProcessor()
    all_types, priority_types = processor.get_available_metadata_types()
    
    print("\n🎯 Available Metadata Types:")
    print("\nPriority Types (commonly used):")
    for i, mtype in enumerate(priority_types[:10], 1):
        print(f"  {i}. {mtype}")
    
    print(f"\nTotal metadata types available: {len(all_types)}")
    print("\nExamples:", ", ".join(all_types[:5]))
    
    print("\n" + "="*60)
    print("📝 Enter metadata types to process:")
    print("  - Separate multiple types with commas")
    print("  - Use 'all' for all types (warning: ~894K tokens!)")
    print("  - Press Enter for default: 'Flow'")
    print("="*60)
    
    user_input = input("\nMetadata types: ").strip()
    
    if not user_input:
        selected_types = ["Flow"]
        print(f"Using default: {selected_types}")
    elif user_input.lower() == 'all':
        selected_types = all_types
        print(f"⚠️  Processing ALL {len(selected_types)} metadata types!")
    else:
        # Parse comma-separated list
        selected_types = [t.strip() for t in user_input.split(',')]
        
        # Validate types exist
        valid_types = []
        for mtype in selected_types:
            if mtype in all_types:
                valid_types.append(mtype)
            else:
                print(f"❌ Unknown metadata type: {mtype}")
        
        selected_types = valid_types
    
    print(f"\n✅ Will process: {selected_types}")
    return selected_types

async def main():
    """Main function to process Salesforce Metadata API PDF"""
    
    print("🚀 Salesforce Metadata API PDF Processor")
    print("=" * 50)
    
    # Check if RAG manager is properly initialized
    if not rag_manager.vector_store:
        print("❌ RAG system not properly initialized. Please check your environment variables:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_KEY") 
        print("   - OPENAI_API_KEY")
        return
    
    print("✅ RAG system initialized successfully")
    
    # Initialize processor
    processor = SalesforceMetadataPDFProcessor()
    
    # Download PDF if needed
    if not await processor.download_pdf():
        print("❌ Failed to download PDF. Exiting.")
        return
    
    # Get user selection of metadata types
    selected_types = get_user_metadata_types()
    
    if not selected_types:
        print("❌ No valid metadata types selected. Exiting.")
        return
    
    # Extract table of contents
    toc = processor.extract_table_of_contents()
    if not toc:
        print("❌ Failed to extract table of contents. Exiting.")
        return
    
    # Process each selected metadata type
    total_chunks = 0
    total_tokens = 0
    
    for metadata_type in selected_types:
        print(f"\n📋 Processing {metadata_type}...")
        
        # Extract content for this metadata type
        content = processor.extract_metadata_type_content(metadata_type, toc)
        if not content:
            print(f"❌ No content found for {metadata_type}")
            continue
        
        # Chunk the content
        chunks = processor.chunk_content(content, metadata_type)
        if not chunks:
            print(f"❌ No chunks created for {metadata_type}")
            continue
        
        # Add chunks to RAG database
        successful_chunks = 0
        for chunk in chunks:
            success = rag_manager.add_documentation(
                content=chunk["content"],
                metadata=chunk["metadata"]
            )
            
            if success:
                successful_chunks += 1
                total_tokens += chunk["metadata"]["token_count"]
            
        total_chunks += successful_chunks
        print(f"✅ Added {successful_chunks}/{len(chunks)} chunks for {metadata_type}")
    
    print("\n" + "=" * 50)
    print("🎉 Processing completed!")
    print(f"📊 Total chunks added: {total_chunks}")
    print(f"🔢 Total tokens processed: {total_tokens:,}")
    print(f"📚 Metadata types processed: {len(selected_types)}")
    
    print("\nTo test the knowledge base:")
    print("from src.tools.rag_tools import search_flow_knowledge_base")
    print('results = search_flow_knowledge_base("flow metadata structure")')

if __name__ == "__main__":
    asyncio.run(main()) 