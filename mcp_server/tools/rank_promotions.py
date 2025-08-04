"""
Promotion ranking tool using CTR/CVR prediction models.
"""

from typing import Dict, List, Any
from loguru import logger

from models.ranker import get_ranker


async def rank_promotions_tool(candidates: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Rank promotion candidates based on predicted click-through rate and user profile.
    
    Args:
        candidates: List of promotion candidates with id, title, description, link
        user_profile: User profile containing user_type, interests, budget_level
        
    Returns:
        Dictionary containing ranked_promotions with id and score
    """
    try:
        if not candidates:
            logger.warning("No candidates provided for ranking")
            return {"ranked_promotions": []}
        
        # Get the ranker instance
        ranker = get_ranker()
        
        # Rank the promotions
        ranked_promotions = ranker.rank_promotions(candidates, user_profile)
        
        logger.info(f"Ranked {len(candidates)} promotions successfully")
        return {"ranked_promotions": ranked_promotions}
        
    except Exception as e:
        logger.error(f"Error in rank_promotions_tool: {e}")
        # Return candidates with default scores on error
        fallback_results = []
        for i, candidate in enumerate(candidates):
            fallback_results.append({
                "id": candidate.get("id", f"promo_{i}"),
                "score": 0.1  # Default score
            })
        return {"ranked_promotions": fallback_results}
