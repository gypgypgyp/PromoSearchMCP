"""
Ad slot optimization tool for determining optimal insertion positions.
"""

import re
from typing import Dict, List, Any
from loguru import logger


async def optimize_ad_slots_tool(search_results: List[str], promotions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Determine where to insert promotion ads into search result context.
    
    Args:
        search_results: List of search result strings
        promotions: List of promotion objects to insert
        
    Returns:
        Dictionary containing injected_results with ads optimally placed
    """
    try:
        if not search_results:
            logger.warning("No search results provided")
            return {"injected_results": []}
        
        if not promotions:
            logger.info("No promotions to inject")
            return {"injected_results": search_results}
        
        # Apply ad slot optimization strategy
        injected_results = _optimize_insertion_strategy(search_results, promotions)
        
        logger.info(f"Optimized ad slots: inserted {len(promotions)} promotions into {len(search_results)} results")
        return {"injected_results": injected_results}
        
    except Exception as e:
        logger.error(f"Error in optimize_ad_slots_tool: {e}")
        # Return original results on error
        return {"injected_results": search_results}


def _optimize_insertion_strategy(search_results: List[str], promotions: List[Dict[str, Any]]) -> List[str]:
    """
    Apply intelligent ad insertion strategy.
    
    Strategy:
    1. Never insert at position 0 (preserve top organic result)
    2. Insert after every 3-4 organic results
    3. Limit to maximum 3 ads per page
    4. Generate contextual ad copy based on surrounding results
    5. Ensure ads are clearly marked as promotional content
    """
    if len(search_results) < 2:
        # Too few results to insert ads meaningfully
        return search_results
    
    # Limit number of ads to insert
    max_ads = min(len(promotions), 3, (len(search_results) // 3))
    if max_ads == 0:
        return search_results
    
    selected_promotions = promotions[:max_ads]
    injected_results = []
    
    # Calculate insertion positions
    insertion_positions = _calculate_insertion_positions(len(search_results), max_ads)
    
    promotion_index = 0
    for i, result in enumerate(search_results):
        # Add the organic result
        injected_results.append(result)
        
        # Check if we should insert an ad after this position
        if i + 1 in insertion_positions and promotion_index < len(selected_promotions):
            promotion = selected_promotions[promotion_index]
            
            # Generate contextual ad copy
            ad_copy = _generate_ad_copy(promotion, search_results, i)
            injected_results.append(ad_copy)
            
            promotion_index += 1
    
    return injected_results


def _calculate_insertion_positions(num_results: int, num_ads: int) -> List[int]:
    """
    Calculate optimal positions to insert ads.
    
    Args:
        num_results: Total number of organic results
        num_ads: Number of ads to insert
        
    Returns:
        List of positions (1-indexed) where ads should be inserted
    """
    if num_ads == 0 or num_results < 2:
        return []
    
    positions = []
    
    if num_results <= 5:
        # For short result lists, insert after position 2
        if num_ads >= 1:
            positions.append(2)
        if num_ads >= 2 and num_results >= 4:
            positions.append(4)
    else:
        # For longer lists, distribute more evenly
        # Start after position 2, then every 3-4 positions
        positions.append(2)
        
        if num_ads >= 2:
            positions.append(5)
        
        if num_ads >= 3 and num_results >= 9:
            positions.append(8)
    
    # Ensure positions don't exceed result count
    positions = [pos for pos in positions if pos < num_results]
    
    return positions[:num_ads]


def _generate_ad_copy(promotion: Dict[str, Any], search_results: List[str], current_position: int) -> str:
    """
    Generate contextual ad copy based on the promotion and surrounding results.
    
    Args:
        promotion: Promotion data
        search_results: All search results for context
        current_position: Current position in results
        
    Returns:
        Formatted ad copy string
    """
    title = promotion.get("title", "Special Offer")
    description = promotion.get("description", "")
    link = promotion.get("link", "#")
    
    # Analyze surrounding context for better ad copy
    context_keywords = _extract_context_keywords(search_results, current_position)
    
    # Generate contextual intro based on keywords
    contextual_intro = _generate_contextual_intro(context_keywords)
    
    # Format the ad copy
    ad_copy = f"""
🎯 [SPONSORED] {contextual_intro}

**{title}**
{description}

👉 Learn more: {link}

---
""".strip()
    
    return ad_copy


def _extract_context_keywords(search_results: List[str], position: int) -> List[str]:
    """Extract relevant keywords from surrounding search results."""
    # Look at results before and after current position
    context_window = 2
    start_pos = max(0, position - context_window)
    end_pos = min(len(search_results), position + context_window + 1)
    
    context_text = " ".join(search_results[start_pos:end_pos])
    
    # Extract meaningful keywords (simple approach)
    # Remove common words and extract potential keywords
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', context_text.lower())
    keywords = [word for word in words if word not in common_words]
    
    # Return top keywords by frequency
    from collections import Counter
    keyword_counts = Counter(keywords)
    return [word for word, count in keyword_counts.most_common(5)]


def _generate_contextual_intro(keywords: List[str]) -> str:
    """Generate a contextual introduction based on extracted keywords."""
    if not keywords:
        return "Looking for great deals?"
    
    # Check for specific categories
    tech_keywords = {'cloud', 'server', 'hosting', 'aws', 'api', 'database', 'software'}
    mobile_keywords = {'phone', 'mobile', 'smartphone', 'android', 'ios'}
    business_keywords = {'business', 'enterprise', 'professional', 'office', 'productivity'}
    
    keyword_set = set(keywords)
    
    if keyword_set & tech_keywords:
        return "Perfect for your tech needs!"
    elif keyword_set & mobile_keywords:
        return "Great mobile deals for you!"
    elif keyword_set & business_keywords:
        return "Boost your business with these offers!"
    else:
        # Generic contextual intro
        if len(keywords) > 0:
            return f"Related to {keywords[0]} - check this out!"
        else:
            return "You might be interested in this:"
