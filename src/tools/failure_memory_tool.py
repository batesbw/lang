import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class FailureRecord(BaseModel):
    """Model for storing failure information"""
    id: str = Field(description="Unique identifier for the failure")
    timestamp: str = Field(description="When the failure occurred")
    failure_type: str = Field(description="Category of failure (deployment, compilation, etc.)")
    error_message: str = Field(description="Original error message")
    flow_xml_hash: str = Field(description="Hash of the Flow XML that failed")
    component_errors: Optional[List[str]] = Field(default=None, description="Specific component errors")
    attempted_fix: Optional[str] = Field(default=None, description="What fix was attempted")
    fix_successful: Optional[bool] = Field(default=None, description="Whether the fix worked")
    failure_category: str = Field(description="Categorized failure type")
    severity: str = Field(description="Severity level: low, medium, high, critical")

class FailurePattern(BaseModel):
    """Model for storing patterns and solutions"""
    pattern_id: str = Field(description="Unique identifier for the pattern")
    error_pattern: str = Field(description="Regex or text pattern that matches this error")
    category: str = Field(description="Category of this failure pattern")
    description: str = Field(description="Human-readable description of the issue")
    recommended_solution: str = Field(description="Recommended fix for this pattern")
    success_rate: float = Field(description="Success rate of the recommended solution")
    examples: List[str] = Field(description="Example error messages matching this pattern")

class FailureMemoryTool(BaseTool):
    """Tool for managing deployment failure memory and learning"""
    
    name: str = "failure_memory_tool"
    description: str = "Manages persistent storage of deployment failures and categorizes them for learning"
    memory_path: str = Field(default_factory=lambda: os.getenv("FAILURE_MEMORY_PATH", "./failure_memory.json"))
    enabled: bool = Field(default_factory=lambda: os.getenv("ENABLE_FAILURE_MEMORY", "true").lower() == "true")
        
    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Run the failure memory tool with specified action"""
        if not self.enabled:
            return {"success": True, "message": "Failure memory is disabled"}
            
        if action == "load_failures":
            return self._load_failures()
        elif action == "save_failure":
            return self._save_failure(**kwargs)
        elif action == "categorize_failure":
            return self._categorize_failure(**kwargs)
        elif action == "get_similar_failures":
            return self._get_similar_failures(**kwargs)
        elif action == "update_fix_result":
            return self._update_fix_result(**kwargs)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _load_failures(self) -> Dict[str, Any]:
        """Load failure history from persistent storage"""
        try:
            if not Path(self.memory_path).exists():
                self._initialize_memory_file()
                
            with open(self.memory_path, 'r') as f:
                data = json.load(f)
                
            return {
                "success": True,
                "failures": data.get("failures", []),
                "patterns": data.get("patterns", []),
                "statistics": data.get("statistics", {})
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to load failures: {str(e)}"}
    
    def _save_failure(self, error_message: str, flow_xml: str, component_errors: Optional[List[str]] = None, deployment_id: Optional[str] = None) -> Dict[str, Any]:
        """Save a new failure record"""
        try:
            # Create failure record
            failure_id = hashlib.md5(f"{error_message}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
            flow_xml_hash = hashlib.md5(flow_xml.encode()).hexdigest()[:16]
            
            failure_record = FailureRecord(
                id=failure_id,
                timestamp=datetime.now().isoformat(),
                failure_type="deployment",
                error_message=error_message,
                flow_xml_hash=flow_xml_hash,
                component_errors=component_errors,
                failure_category=self._categorize_error(error_message),
                severity=self._assess_severity(error_message, component_errors)
            )
            
            # Load existing data
            data = self._load_memory_file()
            data["failures"].append(failure_record.model_dump())
            
            # Update statistics
            self._update_statistics(data, failure_record)
            
            # Save updated data
            self._save_memory_file(data)
            
            return {
                "success": True,
                "failure_id": failure_id,
                "category": failure_record.failure_category,
                "severity": failure_record.severity
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to save failure: {str(e)}"}
    
    def _categorize_failure(self, error_message: str) -> Dict[str, Any]:
        """Categorize a failure and suggest solutions based on learned patterns"""
        category = self._categorize_error(error_message)
        
        # Generate solutions based on learned patterns and similar failures
        suggested_solutions = self._generate_solutions_from_patterns(error_message, category)
        
        # Load patterns that match this error
        data = self._load_memory_file()
        patterns = data.get("patterns", [])
        
        matching_patterns = []
        for pattern in patterns:
            if self._pattern_matches(pattern["error_pattern"], error_message):
                matching_patterns.append(pattern)
        
        return {
            "success": True,
            "category": category,
            "matching_patterns": matching_patterns,
            "suggested_solutions": suggested_solutions
        }
    
    def _get_similar_failures(self, error_message: str, flow_xml_hash: str) -> Dict[str, Any]:
        """Find similar failures for learning"""
        try:
            data = self._load_memory_file()
            failures = data.get("failures", [])
            
            similar_failures = []
            for failure in failures:
                similarity_score = self._calculate_similarity(error_message, failure["error_message"])
                if similarity_score > 0.7:  # 70% similarity threshold
                    similar_failures.append({
                        **failure,
                        "similarity_score": similarity_score
                    })
            
            # Sort by similarity score
            similar_failures.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "success": True,
                "similar_failures": similar_failures[:5],  # Return top 5
                "total_found": len(similar_failures)
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to find similar failures: {str(e)}"}
    
    def _update_fix_result(self, failure_id: str, attempted_fix: str, success: bool) -> Dict[str, Any]:
        """Update a failure record with fix attempt results"""
        try:
            data = self._load_memory_file()
            failures = data.get("failures", [])
            
            # Find and update the failure record
            updated_failure = None
            for failure in failures:
                if failure["id"] == failure_id:
                    failure["attempted_fix"] = attempted_fix
                    failure["fix_successful"] = success
                    updated_failure = failure
                    break
            
            if updated_failure and success:
                # Learn from successful fix - create or update pattern
                self._learn_pattern_from_success(data, updated_failure, attempted_fix)
            
            self._save_memory_file(data)
            
            return {"success": True, "message": f"Updated failure {failure_id} with fix result"}
        except Exception as e:
            return {"success": False, "error": f"Failed to update fix result: {str(e)}"}
    
    def _learn_pattern_from_success(self, data: Dict[str, Any], failure: Dict[str, Any], successful_fix: str) -> None:
        """Learn a new pattern from a successful fix"""
        patterns = data.get("patterns", [])
        error_message = failure["error_message"]
        category = failure["failure_category"]
        
        # Check if we already have a pattern for this category
        existing_pattern = None
        for pattern in patterns:
            if pattern["category"] == category:
                existing_pattern = pattern
                break
        
        if existing_pattern:
            # Update existing pattern with new success data
            if successful_fix not in existing_pattern.get("successful_fixes", []):
                existing_pattern.setdefault("successful_fixes", []).append(successful_fix)
                existing_pattern.setdefault("examples", []).append(error_message)
                
                # Update success rate
                total_attempts = existing_pattern.get("total_attempts", 0) + 1
                successful_attempts = existing_pattern.get("successful_attempts", 0) + 1
                existing_pattern["total_attempts"] = total_attempts
                existing_pattern["successful_attempts"] = successful_attempts
                existing_pattern["success_rate"] = successful_attempts / total_attempts
        else:
            # Create new pattern
            # Extract key words from error message to create pattern
            error_words = [word.lower() for word in error_message.split() if len(word) > 3]
            pattern_keywords = error_words[:3]  # Use first 3 significant words
            
            new_pattern = {
                "pattern_id": f"{category}_{len(patterns)}",
                "error_pattern": "|".join(pattern_keywords),  # Simple word matching
                "category": category,
                "description": f"Pattern learned from: {error_message[:100]}...",
                "successful_fixes": [successful_fix],
                "examples": [error_message],
                "total_attempts": 1,
                "successful_attempts": 1,
                "success_rate": 1.0,
                "learned_from": failure["id"]
            }
            patterns.append(new_pattern)
        
        data["patterns"] = patterns
    
    def _generate_solutions_from_patterns(self, error_message: str, category: str) -> List[str]:
        """Generate solutions based on learned patterns"""
        data = self._load_memory_file()
        patterns = data.get("patterns", [])
        failures = data.get("failures", [])
        
        solutions = []
        
        # First, look for patterns that match this category
        for pattern in patterns:
            if pattern["category"] == category and pattern.get("successful_fixes"):
                # Sort fixes by success rate
                fixes = pattern["successful_fixes"]
                success_rate = pattern.get("success_rate", 0)
                
                for fix in fixes:
                    solutions.append({
                        "solution": fix,
                        "success_rate": success_rate,
                        "source": "learned_pattern",
                        "pattern_id": pattern["pattern_id"]
                    })
        
        # Second, look for similar successful fixes in failure history
        for failure in failures:
            if (failure.get("fix_successful") and 
                failure.get("attempted_fix") and
                self._calculate_similarity(error_message, failure["error_message"]) > 0.7):
                
                solutions.append({
                    "solution": failure["attempted_fix"],
                    "success_rate": 1.0,  # This specific fix worked
                    "source": "similar_failure",
                    "failure_id": failure["id"]
                })
        
        # Remove duplicates and sort by success rate
        seen_solutions = set()
        unique_solutions = []
        for sol in solutions:
            if sol["solution"] not in seen_solutions:
                seen_solutions.add(sol["solution"])
                unique_solutions.append(sol["solution"])
        
        return unique_solutions[:3]  # Return top 3 solutions
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message dynamically based on learned patterns"""
        # Load existing patterns from memory
        data = self._load_memory_file()
        patterns = data.get("patterns", [])
        
        # Check against learned patterns first
        for pattern in patterns:
            if self._pattern_matches(pattern["error_pattern"], error_message):
                return pattern["category"]
        
        # If no patterns match, create a dynamic category based on key words
        error_lower = error_message.lower()
        
        # Simple heuristic categorization for new errors
        if "duplicate" in error_lower:
            return "duplicate_error"
        elif "field" in error_lower and ("not found" in error_lower or "does not exist" in error_lower):
            return "missing_field"
        elif "object" in error_lower and ("not found" in error_lower or "does not exist" in error_lower):
            return "missing_object"
        elif "permission" in error_lower or "access" in error_lower:
            return "permission_error"
        elif "syntax" in error_lower or "invalid" in error_lower:
            return "syntax_error"
        elif "required" in error_lower and "missing" in error_lower:
            return "missing_required_field"
        elif "reference" in error_lower:
            return "reference_error"
        else:
            # Create a unique category based on error message hash for truly unknown errors
            import hashlib
            error_hash = hashlib.md5(error_message.encode()).hexdigest()[:8]
            return f"unknown_{error_hash}"
    
    def _assess_severity(self, error_message: str, component_errors: Optional[List[str]]) -> str:
        """Assess severity of the failure"""
        error_lower = error_message.lower()
        
        if "critical" in error_lower or "fatal" in error_lower:
            return "critical"
        elif "permission" in error_lower or "access" in error_lower:
            return "high"
        elif component_errors and len(component_errors) > 5:
            return "high"
        elif "warning" in error_lower:
            return "low"
        else:
            return "medium"
    
    def _pattern_matches(self, pattern: str, error_message: str) -> bool:
        """Check if an error pattern matches the error message"""
        import re
        try:
            return bool(re.search(pattern, error_message, re.IGNORECASE))
        except re.error:
            # If regex fails, do simple string matching
            return pattern.lower() in error_message.lower()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two error messages"""
        # Simple similarity based on common words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    def _load_memory_file(self) -> Dict[str, Any]:
        """Load the memory file"""
        if not Path(self.memory_path).exists():
            self._initialize_memory_file()
            
        with open(self.memory_path, 'r') as f:
            return json.load(f)
    
    def _save_memory_file(self, data: Dict[str, Any]) -> None:
        """Save data to memory file"""
        with open(self.memory_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_memory_file(self) -> None:
        """Initialize an empty memory file with default structure"""
        default_data = {
            "failures": [],
            "patterns": self._get_default_patterns(),
            "statistics": {
                "total_failures": 0,
                "categories": {},
                "success_rates": {}
            }
        }
        
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        self._save_memory_file(default_data)
    
    def _get_default_patterns(self) -> List[Dict[str, Any]]:
        """Get default failure patterns - start with empty patterns that will be learned dynamically"""
        return []
    
    def _update_statistics(self, data: Dict[str, Any], failure_record: FailureRecord) -> None:
        """Update failure statistics"""
        stats = data.get("statistics", {})
        stats["total_failures"] = stats.get("total_failures", 0) + 1
        
        categories = stats.get("categories", {})
        categories[failure_record.failure_category] = categories.get(failure_record.failure_category, 0) + 1
        stats["categories"] = categories
        
        data["statistics"] = stats

    def store_failure(self, error_message: str, component_errors: Optional[List[str]] = None, flow_name: str = "Unknown", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Convenience method to store a failure and return the failure ID"""
        flow_xml = metadata.get("flow_xml", "") if metadata else ""
        result = self._run("save_failure", 
                          error_message=error_message, 
                          flow_xml=flow_xml, 
                          component_errors=component_errors)
        
        if result.get("success"):
            return result.get("failure_id", "unknown")
        else:
            raise Exception(f"Failed to store failure: {result.get('error')}")
    
    def get_failure_analysis(self, failure_id: str) -> Dict[str, Any]:
        """Convenience method to get failure analysis for a stored failure"""
        # Load the failure record to get its details
        load_result = self._run("load_failures")
        if not load_result.get("success"):
            return {"category": "unknown", "severity": "medium", "suggested_solutions": [], "similar_failures": []}
        
        # Find the specific failure
        failures = load_result.get("failures", [])
        target_failure = None
        for failure in failures:
            if failure.get("id") == failure_id:
                target_failure = failure
                break
        
        if not target_failure:
            return {"category": "unknown", "severity": "medium", "suggested_solutions": [], "similar_failures": []}
        
        # Categorize the failure to get suggestions
        categorization = self._run("categorize_failure", error_message=target_failure["error_message"])
        
        # Get similar failures
        similar_failures_result = self._run("get_similar_failures", 
                                           error_message=target_failure["error_message"],
                                           flow_xml_hash=target_failure.get("flow_xml_hash", ""))
        
        return {
            "category": target_failure.get("failure_category", "unknown"),
            "severity": target_failure.get("severity", "medium"),
            "suggested_solutions": categorization.get("suggested_solutions", []),
            "similar_failures": similar_failures_result.get("similar_failures", []),
            "patterns_matched": categorization.get("matching_patterns", [])
        } 