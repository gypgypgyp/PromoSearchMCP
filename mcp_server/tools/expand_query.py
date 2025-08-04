"""
Query expansion tool using LLM to generate long-tail keywords.
"""

import os
import json
from typing import Dict, List
from loguru import logger

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


async def expand_query_tool(query: str) -> Dict[str, List[str]]:
    """
    Expand a natural language query into multiple long-tail keyword variations.
    
    Args:
        query: The original user query
        
    Returns:
        Dictionary with 'expanded_queries' key containing list of expanded queries
    """
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
    max_queries = int(os.getenv("MAX_EXPANDED_QUERIES", "5"))
    
    prompt = f"""
Expand this search query into {max_queries} related long-tail keyword variations that would help find relevant promotions and deals:

Original Query: "{query}"

Generate variations that include:
- Specific product names and brands
- Feature-focused terms (e.g., "discount", "sale", "offer", "deal")
- Category-specific terms
- Price and budget related terms
- Seasonal or time-sensitive terms

Return ONLY a JSON array of strings, no other text:
["variation1", "variation2", "variation3", ...]
"""

    try:
        if provider == "openai" and OPENAI_AVAILABLE:
            expanded_queries = await _expand_with_openai(prompt)
        elif provider == "anthropic" and ANTHROPIC_AVAILABLE:
            expanded_queries = await _expand_with_anthropic(prompt)
        else:
            # Fallback to rule-based expansion
            logger.warning(f"LLM provider '{provider}' not available, using fallback")
            expanded_queries = _fallback_expansion(query)
            
        return {"expanded_queries": expanded_queries[:max_queries]}
        
    except Exception as e:
        logger.error(f"Error in query expansion: {e}")
        # Return fallback expansion on error
        return {"expanded_queries": _fallback_expansion(query)}


async def _expand_with_openai(prompt: str) -> List[str]:
    """Expand query using OpenAI API."""
    client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )
    
    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != 0:
            return json.loads(content[start:end])
        raise ValueError("Could not parse JSON response")


async def _expand_with_anthropic(prompt: str) -> List[str]:
    """Expand query using Anthropic Claude API."""
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    response = await client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = response.content[0].text.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end != 0:
            return json.loads(content[start:end])
        raise ValueError("Could not parse JSON response")


def _fallback_expansion(query: str) -> List[str]:
    """
    Fallback rule-based query expansion when LLM is not available.
    """
    query_lower = query.lower()
    expansions = [query]  # Always include original
    
    # Add common promotional terms
    promo_terms = ["deal", "discount", "sale", "offer", "promotion", "coupon"]
    for term in promo_terms:
        if term not in query_lower:
            expansions.append(f"{query} {term}")
    
    # Add category-specific expansions
    if any(word in query_lower for word in ["cloud", "aws", "server", "hosting"]):
        expansions.extend([
            f"{query} cloud computing",
            f"{query} web hosting deal",
            f"aws {query} discount"
        ])
    elif any(word in query_lower for word in ["phone", "mobile", "smartphone"]):
        expansions.extend([
            f"{query} smartphone deal",
            f"{query} mobile phone offer",
            f"{query} electronics sale"
        ])
    elif any(word in query_lower for word in ["laptop", "computer", "pc"]):
        expansions.extend([
            f"{query} computer deal",
            f"{query} laptop discount",
            f"{query} electronics promotion"
        ])
    else:
        # Generic expansions
        expansions.extend([
            f"best {query} deals",
            f"{query} special offer",
            f"cheap {query}"
        ])
    
    return expansions[:5]  # Return max 5 variations
