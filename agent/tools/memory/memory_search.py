"""
Memory search tool

Allows agents to search their memory using semantic and keyword search
"""

from typing import Dict, Any, Optional
from agent.tools.base_tool import BaseTool


class MemorySearchTool(BaseTool):
    """Tool for searching agent memory"""
    
    name: str = "memory_search"
    description: str = (
        "Search agent's long-term memory using semantic and keyword search. "
        "Use this to recall past conversations, preferences, and knowledge."
    )
    params: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (can be natural language question or keywords)"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 10)",
                "default": 10
            },
            "min_score": {
                "type": "number",
                "description": "Minimum relevance score (0-1, default: 0.1)",
                "default": 0.1
            }
        },
        "required": ["query"]
    }
    
    def __init__(self, memory_manager, user_id: Optional[str] = None):
        """
        Initialize memory search tool
        
        Args:
            memory_manager: MemoryManager instance
            user_id: Optional user ID for scoped search
        """
        super().__init__()
        self.memory_manager = memory_manager
        self.user_id = user_id

        from config import conf
        parts = [
            "Search agent's long-term memory using local hybrid search",
        ]
        if getattr(memory_manager, "mem0", None):
            parts.append("and Mem0 cloud semantic memory")
        if conf().get("knowledge", True):
            parts.append("and the knowledge base")
        self.description = (
            f"{' '.join(parts)}. "
            "Use this to recall past conversations, preferences, and durable facts."
        )
    
    def execute(self, args: dict):
        """
        Execute memory search
        
        Args:
            args: Dictionary with query, max_results, min_score
            
        Returns:
            ToolResult with formatted search results
        """
        from agent.tools.base_tool import ToolResult

        query = args.get("query")
        max_results = args.get("max_results", 10)
        min_score = args.get("min_score", 0.1)
        
        if not query:
            return ToolResult.fail("Error: query parameter is required")
        
        try:
            # Safe under both CLI (no loop) and web/async channels (running loop).
            from common.async_utils import run_async

            results = run_async(self.memory_manager.search(
                query=query,
                user_id=self.user_id,
                max_results=max_results,
                min_score=min_score,
                include_shared=True
            ))
            
            if not results:
                # Return clear message that no memories exist yet
                # This prevents infinite retry loops
                return ToolResult.success(
                    f"No memories found for '{query}'. "
                    f"This is normal if no memories have been stored yet. "
                    f"Store facts in MEMORY.md / memory/ daily files"
                    + (
                        ", or continue chatting so Mem0 can extract durable facts."
                        if getattr(self.memory_manager, "mem0", None)
                        else "."
                    )
                )
            
            # Format results
            output = [f"Found {len(results)} relevant memories:\n"]
            
            for i, result in enumerate(results, 1):
                if getattr(result, "source", "") == "mem0" or str(result.path).startswith("mem0://"):
                    output.append(f"\n{i}. [Mem0 cloud] score={result.score:.3f}")
                    output.append(f"   {result.snippet}")
                else:
                    output.append(
                        f"\n{i}. {result.path} (lines {result.start_line}-{result.end_line})"
                    )
                    output.append(f"   Score: {result.score:.3f}")
                    output.append(f"   Snippet: {result.snippet}")
            
            return ToolResult.success("\n".join(output))
            
        except Exception as e:
            return ToolResult.fail(f"Error searching memory: {str(e)}")
