"""
Lightning Flow Scanner RAG Integration

This module provides specialized tools for ingesting the Lightning Flow Scanner repository
and using its rules/best practices proactively during flow generation, rather than 
reactively during validation.
"""

import os
import logging
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from langchain_core.tools import tool
from langchain_core.documents import Document
from github import Github
from ..tools.rag_tools import rag_manager

logger = logging.getLogger(__name__)

class LightningFlowScannerRAG:
    """Specialized RAG manager for Lightning Flow Scanner repository"""
    
    def __init__(self):
        self.scanner_repo_url = "https://github.com/Lightning-Flow-Scanner/lightning-flow-scanner-sfdx"
        self.scanner_owner = "Lightning-Flow-Scanner"
        self.scanner_repo = "lightning-flow-scanner-sfdx"
        
    def ingest_scanner_repository(self) -> Dict[str, Any]:
        """
        Ingest the Lightning Flow Scanner repository and extract rules/best practices
        """
        try:
            if not rag_manager.github_client:
                logger.error("GitHub client not initialized")
                return {"success": False, "message": "GitHub client not available"}
            
            # Get the repository
            repo = rag_manager.github_client.get_repo(f"{self.scanner_owner}/{self.scanner_repo}")
            
            # Extract rules and documentation
            rules_extracted = self._extract_rules_from_repo(repo)
            docs_extracted = self._extract_documentation_from_repo(repo)
            
            # Process and store the extracted knowledge
            total_added = 0
            
            # Add rule definitions as documentation
            for rule in rules_extracted:
                success = rag_manager.add_documentation(
                    content=rule["content"],
                    metadata=rule["metadata"]
                )
                if success:
                    total_added += 1
            
            # Add documentation pages
            for doc in docs_extracted:
                success = rag_manager.add_documentation(
                    content=doc["content"],
                    metadata=doc["metadata"]
                )
                if success:
                    total_added += 1
            
            return {
                "success": True,
                "message": f"Successfully ingested Lightning Flow Scanner repository",
                "rules_found": len(rules_extracted),
                "docs_found": len(docs_extracted),
                "total_added": total_added
            }
            
        except Exception as e:
            logger.error(f"Error ingesting scanner repository: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _extract_rules_from_repo(self, repo) -> List[Dict[str, Any]]:
        """Extract rule definitions from the repository"""
        rules = []
        
        try:
            # Get the src directory structure
            contents = repo.get_contents("src")
            
            # Recursively find TypeScript files that contain rule definitions
            rule_files = self._find_rule_files(repo, contents)
            
            for file_info in rule_files:
                try:
                    content = file_info.decoded_content.decode('utf-8')
                    extracted_rules = self._parse_rule_file(content, file_info.path)
                    rules.extend(extracted_rules)
                except Exception as e:
                    logger.warning(f"Error processing rule file {file_info.path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting rules: {str(e)}")
        
        return rules
    
    def _extract_documentation_from_repo(self, repo) -> List[Dict[str, Any]]:
        """Extract documentation from the repository"""
        docs = []
        
        try:
            # Get README and other markdown files
            readme = repo.get_readme()
            docs.append({
                "content": readme.decoded_content.decode('utf-8'),
                "metadata": {
                    "title": "Lightning Flow Scanner - Main Documentation",
                    "category": "flow_scanner_docs",
                    "source": "lightning_flow_scanner",
                    "file_path": readme.path,
                    "tags": ["flow_scanner", "validation", "best_practices", "rules"],
                    "created_at": datetime.now().isoformat()
                }
            })
            
            # Look for additional documentation files
            try:
                docs_contents = repo.get_contents("docs")
                for doc_file in docs_contents:
                    if doc_file.name.endswith('.md'):
                        content = doc_file.decoded_content.decode('utf-8')
                        docs.append({
                            "content": content,
                            "metadata": {
                                "title": f"Lightning Flow Scanner - {doc_file.name}",
                                "category": "flow_scanner_docs",
                                "source": "lightning_flow_scanner",
                                "file_path": doc_file.path,
                                "tags": ["flow_scanner", "documentation"],
                                "created_at": datetime.now().isoformat()
                            }
                        })
            except:
                # No docs directory or other issues
                pass
                
        except Exception as e:
            logger.error(f"Error extracting documentation: {str(e)}")
        
        return docs
    
    def _find_rule_files(self, repo, contents) -> List:
        """Recursively find TypeScript rule files"""
        rule_files = []
        
        for content in contents:
            if content.type == "dir":
                try:
                    subcontents = repo.get_contents(content.path)
                    rule_files.extend(self._find_rule_files(repo, subcontents))
                except:
                    continue
            elif content.name.endswith('.ts') and ('rule' in content.name.lower() or 'rules' in content.path.lower()):
                rule_files.append(content)
        
        return rule_files
    
    def _parse_rule_file(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse a TypeScript rule file to extract rule information"""
        rules = []
        
        try:
            # Extract class definitions that likely contain rules
            class_pattern = r'export\s+class\s+(\w+)\s*(?:extends\s+\w+)?\s*{(.*?)}'
            class_matches = re.finditer(class_pattern, content, re.DOTALL)
            
            for match in class_matches:
                class_name = match.group(1)
                class_body = match.group(2)
                
                # Extract rule information
                rule_info = self._extract_rule_info(class_name, class_body, content)
                
                if rule_info:
                    rule_doc = self._format_rule_documentation(rule_info, file_path)
                    rules.append(rule_doc)
            
            # Also look for configuration objects or rule metadata
            config_rules = self._extract_config_rules(content, file_path)
            rules.extend(config_rules)
            
        except Exception as e:
            logger.warning(f"Error parsing rule file {file_path}: {str(e)}")
        
        return rules
    
    def _extract_rule_info(self, class_name: str, class_body: str, full_content: str) -> Optional[Dict[str, Any]]:
        """Extract rule information from a class definition"""
        rule_info = {"name": class_name}
        
        # Extract description from comments
        description_pattern = r'/\*\*(.*?)\*/'
        description_match = re.search(description_pattern, full_content, re.DOTALL)
        if description_match:
            rule_info["description"] = description_match.group(1).strip()
        
        # Extract severity information
        severity_pattern = r'severity[:\s]*["\'](\w+)["\']'
        severity_match = re.search(severity_pattern, class_body)
        if severity_match:
            rule_info["default_severity"] = severity_match.group(1)
        
        # Extract category/type information
        category_pattern = r'category[:\s]*["\'](\w+)["\']'
        category_match = re.search(category_pattern, class_body)
        if category_match:
            rule_info["category"] = category_match.group(1)
        
        # Extract any validation logic patterns
        validation_patterns = re.findall(r'validate.*?\{(.*?)\}', class_body, re.DOTALL)
        if validation_patterns:
            rule_info["validation_logic"] = validation_patterns
        
        return rule_info if len(rule_info) > 1 else None
    
    def _extract_config_rules(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract rule information from configuration objects"""
        rules = []
        
        # Look for rule definitions in configuration objects
        config_pattern = r'(\w+):\s*{[^}]*(?:severity|description|expression)[^}]*}'
        config_matches = re.finditer(config_pattern, content)
        
        for match in config_matches:
            rule_name = match.group(1)
            rule_block = match.group(0)
            
            # Extract information from the rule block
            rule_info = {"name": rule_name}
            
            # Extract description
            desc_match = re.search(r'description[:\s]*["\']([^"\']+)["\']', rule_block)
            if desc_match:
                rule_info["description"] = desc_match.group(1)
            
            # Extract severity
            sev_match = re.search(r'severity[:\s]*["\'](\w+)["\']', rule_block)
            if sev_match:
                rule_info["default_severity"] = sev_match.group(1)
            
            # Extract expression
            expr_match = re.search(r'expression[:\s]*["\']([^"\']+)["\']', rule_block)
            if expr_match:
                rule_info["expression"] = expr_match.group(1)
            
            if len(rule_info) > 1:
                rule_doc = self._format_rule_documentation(rule_info, file_path)
                rules.append(rule_doc)
        
        return rules
    
    def _format_rule_documentation(self, rule_info: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Format rule information as documentation"""
        
        # Create comprehensive rule documentation
        content_parts = [
            f"# Lightning Flow Scanner Rule: {rule_info['name']}",
            "",
            f"**Source File:** {file_path}",
            ""
        ]
        
        if "description" in rule_info:
            content_parts.extend([
                "## Description",
                rule_info["description"],
                ""
            ])
        
        if "default_severity" in rule_info:
            content_parts.extend([
                "## Default Severity",
                rule_info["default_severity"],
                ""
            ])
        
        if "category" in rule_info:
            content_parts.extend([
                "## Category",
                rule_info["category"],
                ""
            ])
        
        if "expression" in rule_info:
            content_parts.extend([
                "## Validation Expression",
                f"```{rule_info['expression']}```",
                ""
            ])
        
        if "validation_logic" in rule_info:
            content_parts.extend([
                "## Validation Logic",
                "```typescript"
            ])
            for logic in rule_info["validation_logic"]:
                content_parts.append(logic)
            content_parts.extend(["```", ""])
        
        # Add best practices guidance
        content_parts.extend([
            "## Best Practice Guidance",
            f"This rule ensures flow quality by validating {rule_info['name'].lower()}. ",
            "To avoid validation issues, ensure your flow follows the patterns and requirements defined by this rule.",
            ""
        ])
        
        return {
            "content": "\n".join(content_parts),
            "metadata": {
                "title": f"Flow Scanner Rule: {rule_info['name']}",
                "category": "flow_scanner_rules",
                "rule_name": rule_info['name'],
                "source": "lightning_flow_scanner",
                "file_path": file_path,
                "severity": rule_info.get("default_severity", "unknown"),
                "tags": [
                    "flow_scanner", 
                    "validation_rule", 
                    "best_practices",
                    rule_info.get("category", "general").lower()
                ],
                "created_at": datetime.now().isoformat()
            }
        }

# Initialize the scanner RAG manager
scanner_rag = LightningFlowScannerRAG()

@tool
def ingest_lightning_flow_scanner() -> Dict[str, Any]:
    """
    Ingest the Lightning Flow Scanner repository to extract rules and best practices
    for proactive flow generation guidance.
    
    Returns:
        Summary of the ingestion process including rules and documentation added
    """
    return scanner_rag.ingest_scanner_repository()

@tool
def search_flow_scanner_rules(query: str, severity: str = None, category: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search the Lightning Flow Scanner rules for specific best practices and validation requirements.
    
    Args:
        query: The search query (e.g., "naming convention", "fault path", "unused variable")
        severity: Optional severity filter ("error", "warning", "note")
        category: Optional category filter
        max_results: Maximum number of results to return
    
    Returns:
        List of relevant scanner rules and best practices
    """
    try:
        # Build filter metadata
        filter_metadata = {"category": "flow_scanner_rules"}
        
        if severity:
            filter_metadata["severity"] = severity
        
        if category:
            filter_metadata["category"] = category
        
        docs = rag_manager.search_knowledge_base(
            query=query,
            k=max_results,
            filter_metadata=filter_metadata
        )
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "rule_name": doc.metadata.get("rule_name"),
                "severity": doc.metadata.get("severity"),
                "relevance": "high"
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching flow scanner rules: {str(e)}")
        return []

@tool
def get_proactive_flow_guidance(flow_requirements: str, flow_elements: List[str] = None) -> Dict[str, Any]:
    """
    Get proactive guidance for flow generation based on Lightning Flow Scanner best practices.
    
    Args:
        flow_requirements: Description of what the flow should accomplish
        flow_elements: Optional list of flow elements that will be used (e.g., ["Screen", "Record Update", "Decision"])
    
    Returns:
        Comprehensive guidance including relevant rules, best practices, and recommendations
    """
    try:
        guidance = {
            "general_best_practices": [],
            "element_specific_guidance": [],
            "naming_conventions": [],
            "performance_recommendations": [],
            "error_handling_guidance": [],
            "security_considerations": []
        }
        
        # Search for general best practices
        general_docs = rag_manager.search_knowledge_base(
            query=f"flow best practices {flow_requirements}",
            k=5,
            filter_metadata={"category": "flow_scanner_rules"}
        )
        
        for doc in general_docs:
            guidance["general_best_practices"].append({
                "title": doc.metadata.get("title"),
                "content": doc.page_content,
                "rule_name": doc.metadata.get("rule_name"),
                "severity": doc.metadata.get("severity")
            })
        
        # Get element-specific guidance if elements are specified
        if flow_elements:
            for element in flow_elements:
                element_docs = rag_manager.search_knowledge_base(
                    query=f"{element.lower()} flow element best practices",
                    k=3,
                    filter_metadata={"category": "flow_scanner_rules"}
                )
                
                element_guidance = []
                for doc in element_docs:
                    element_guidance.append({
                        "title": doc.metadata.get("title"),
                        "content": doc.page_content,
                        "rule_name": doc.metadata.get("rule_name")
                    })
                
                if element_guidance:
                    guidance["element_specific_guidance"].append({
                        "element": element,
                        "guidance": element_guidance
                    })
        
        # Search for specific guidance categories
        categories = [
            ("naming convention flow name", "naming_conventions"),
            ("performance optimization flow", "performance_recommendations"),
            ("fault path error handling", "error_handling_guidance"),
            ("security flow best practices", "security_considerations")
        ]
        
        for search_query, category_key in categories:
            category_docs = rag_manager.search_knowledge_base(
                query=search_query,
                k=3,
                filter_metadata={"category": "flow_scanner_rules"}
            )
            
            for doc in category_docs:
                guidance[category_key].append({
                    "title": doc.metadata.get("title"),
                    "content": doc.page_content,
                    "rule_name": doc.metadata.get("rule_name"),
                    "severity": doc.metadata.get("severity")
                })
        
        return {
            "success": True,
            "guidance": guidance,
            "total_recommendations": sum(len(v) if isinstance(v, list) else len([item for sublist in v for item in sublist.get("guidance", [])]) for v in guidance.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting proactive flow guidance: {str(e)}")
        return {
            "success": False,
            "message": f"Error retrieving guidance: {str(e)}",
            "guidance": {}
        }

# Export tools for use in agents
LIGHTNING_FLOW_SCANNER_RAG_TOOLS = [
    ingest_lightning_flow_scanner,
    search_flow_scanner_rules,
    get_proactive_flow_guidance
] 