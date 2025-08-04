"""
Main entry point for the PromoSearch MCP Server.
"""

import os
import asyncio
from typing import Any, Dict, List
from dotenv import load_dotenv
from loguru import logger
from fastmcp import FastMCP

from .tools.expand_query import expand_query_tool
from .tools.search_promotions import search_promotions_tool
from .tools.rank_promotions import rank_promotions_tool
from .tools.optimize_ad_slots import optimize_ad_slots_tool

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("PromoSearch MCP Server")

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.add("logs/promosearch.log", rotation="1 day", level=log_level)

@mcp.tool()
async def expand_query(query: str) -> Dict[str, List[str]]:
    """
    Use LLM to expand short natural language query into a list of long-tail keyword candidates.
    
    Args:
        query: User's natural language query
        
    Returns:
        Dictionary containing expanded_queries list
    """
    logger.info(f"Expanding query: {query}")
    try:
        result = await expand_query_tool(query)
        logger.info(f"Query expanded to {len(result['expanded_queries'])} variations")
        return result
    except Exception as e:
        logger.error(f"Error expanding query: {e}")
        raise

@mcp.tool()
async def search_promotions(query: str, user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Semantic search over promotion index using query and user profile.
    
    Args:
        query: Search query string
        user_profile: User profile containing user_type, interests, budget_level
        
    Returns:
        Dictionary containing results list with promotion data
    """
    logger.info(f"Searching promotions for query: {query}")
    try:
        result = await search_promotions_tool(query, user_profile)
        logger.info(f"Found {len(result['results'])} promotion candidates")
        return result
    except Exception as e:
        logger.error(f"Error searching promotions: {e}")
        raise

@mcp.tool()
async def rank_promotions(candidates: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Rank promotion candidates based on predicted click-through rate and user profile.
    
    Args:
        candidates: List of promotion candidates
        user_profile: User profile for personalization
        
    Returns:
        Dictionary containing ranked_promotions with scores
    """
    logger.info(f"Ranking {len(candidates)} promotion candidates")
    try:
        result = await rank_promotions_tool(candidates, user_profile)
        logger.info(f"Ranked promotions successfully")
        return result
    except Exception as e:
        logger.error(f"Error ranking promotions: {e}")
        raise

@mcp.tool()
async def optimize_ad_slots(search_results: List[str], promotions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Determine where to insert promotion ads into search result context.
    
    Args:
        search_results: List of search result strings
        promotions: List of promotion objects to insert
        
    Returns:
        Dictionary containing injected_results with ads optimally placed
    """
    logger.info(f"Optimizing ad slots for {len(promotions)} promotions in {len(search_results)} results")
    try:
        result = await optimize_ad_slots_tool(search_results, promotions)
        logger.info(f"Ad slot optimization completed")
        return result
    except Exception as e:
        logger.error(f"Error optimizing ad slots: {e}")
        raise

def main():
    """Main entry point for the MCP server."""
    host = os.getenv("MCP_SERVER_HOST", "localhost")
    port = int(os.getenv("MCP_SERVER_PORT", "8000"))
    
    logger.info(f"Starting PromoSearch MCP Server on {host}:{port}")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the server
    mcp.run(host=host, port=port)

if __name__ == "__main__":
    main()
