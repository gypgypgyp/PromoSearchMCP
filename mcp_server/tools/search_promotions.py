"""
Semantic search tool for finding relevant promotions.
"""

import os
import json
from typing import Dict, List, Any
from loguru import logger

from models.embedder import EmbeddingModel, PromotionIndex

# Global instances (initialized on first use)
_embedder = None
_promotion_index = None


def _get_embedder() -> EmbeddingModel:
    """Get or create the global embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingModel()
    return _embedder


def _get_promotion_index() -> PromotionIndex:
    """Get or create the global promotion index."""
    global _promotion_index
    if _promotion_index is None:
        embedder = _get_embedder()
        _promotion_index = PromotionIndex(embedder)
        _load_promotions_data()
    return _promotion_index


def _load_promotions_data():
    """Load promotions data from file."""
    data_path = os.getenv("PROMOTIONS_DATA_PATH", "data/promotions.jsonl")
    
    if not os.path.exists(data_path):
        logger.warning(f"Promotions data file not found: {data_path}, using mock data")
        _load_mock_promotions()
        return
    
    try:
        promotions = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    promotion = json.loads(line)
                    promotions.append(promotion)
        
        _promotion_index.add_promotions(promotions)
        logger.info(f"Loaded {len(promotions)} promotions from {data_path}")
        
    except Exception as e:
        logger.error(f"Error loading promotions data: {e}")
        _load_mock_promotions()


def _load_mock_promotions():
    """Load mock promotions data for testing."""
    mock_promotions = [
        {
            "id": "aws-ec2-1",
            "title": "AWS EC2 Instance Discount",
            "description": "Save 30% on AWS EC2 instances for new customers. Perfect for cloud computing and web hosting needs.",
            "link": "https://aws.amazon.com/ec2/pricing/",
            "categories": ["cloud", "computing", "aws", "hosting"],
            "price_tier": "medium",
            "base_ctr": 0.12
        },
        {
            "id": "laptop-deal-1",
            "title": "Gaming Laptop Special Offer",
            "description": "High-performance gaming laptops with RTX graphics cards. 25% off for limited time.",
            "link": "https://example.com/gaming-laptops",
            "categories": ["electronics", "gaming", "laptop", "computer"],
            "price_tier": "high",
            "base_ctr": 0.08
        },
        {
            "id": "phone-promo-1",
            "title": "Smartphone Bundle Deal",
            "description": "Latest smartphones with free accessories and extended warranty. Best value for mobile users.",
            "link": "https://example.com/phone-deals",
            "categories": ["mobile", "phone", "electronics", "smartphone"],
            "price_tier": "medium",
            "base_ctr": 0.15
        },
        {
            "id": "cloud-storage-1",
            "title": "Cloud Storage Premium Plan",
            "description": "Unlimited cloud storage with advanced security features. 50% off first year.",
            "link": "https://example.com/cloud-storage",
            "categories": ["cloud", "storage", "backup", "security"],
            "price_tier": "low",
            "base_ctr": 0.10
        },
        {
            "id": "web-hosting-1",
            "title": "Professional Web Hosting",
            "description": "Fast and reliable web hosting with 99.9% uptime guarantee. Perfect for businesses.",
            "link": "https://example.com/web-hosting",
            "categories": ["hosting", "web", "business", "server"],
            "price_tier": "medium",
            "base_ctr": 0.11
        },
        {
            "id": "software-license-1",
            "title": "Office Software Suite",
            "description": "Complete office productivity suite with word processing, spreadsheets, and presentations.",
            "link": "https://example.com/office-suite",
            "categories": ["software", "productivity", "office", "business"],
            "price_tier": "medium",
            "base_ctr": 0.09
        },
        {
            "id": "vpn-service-1",
            "title": "Premium VPN Service",
            "description": "Secure VPN with global servers and no-logs policy. Protect your privacy online.",
            "link": "https://example.com/vpn",
            "categories": ["security", "privacy", "vpn", "internet"],
            "price_tier": "low",
            "base_ctr": 0.13
        },
        {
            "id": "domain-hosting-1",
            "title": "Domain Registration Special",
            "description": "Register your domain name with free DNS management and email forwarding.",
            "link": "https://example.com/domains",
            "categories": ["domain", "web", "hosting", "business"],
            "price_tier": "low",
            "base_ctr": 0.07
        },
        {
            "id": "ai-service-1",
            "title": "AI API Platform",
            "description": "Access powerful AI models through our API. Perfect for developers and businesses.",
            "link": "https://example.com/ai-api",
            "categories": ["ai", "api", "development", "machine-learning"],
            "price_tier": "high",
            "base_ctr": 0.14
        },
        {
            "id": "database-service-1",
            "title": "Managed Database Service",
            "description": "Fully managed database with automatic backups and scaling. Focus on your application.",
            "link": "https://example.com/database",
            "categories": ["database", "cloud", "managed", "development"],
            "price_tier": "medium",
            "base_ctr": 0.06
        }
    ]
    
    _promotion_index.add_promotions(mock_promotions)
    logger.info(f"Loaded {len(mock_promotions)} mock promotions")


async def search_promotions_tool(query: str, user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search for promotions using semantic similarity and user profile.
    
    Args:
        query: Search query string
        user_profile: User profile containing user_type, interests, budget_level
        
    Returns:
        Dictionary containing results list with promotion data
    """
    try:
        max_results = int(os.getenv("MAX_SEARCH_RESULTS", "20"))
        
        # Get the promotion index
        promotion_index = _get_promotion_index()
        
        # Perform semantic search
        results = promotion_index.search(
            query=query,
            top_k=max_results,
            user_profile=user_profile
        )
        
        # Format results for MCP response
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": result.get("id", ""),
                "title": result.get("title", ""),
                "description": result.get("description", ""),
                "link": result.get("link", ""),
                "score": result.get("score", 0.0)
            }
            formatted_results.append(formatted_result)
        
        logger.info(f"Search completed: {len(formatted_results)} results for query '{query}'")
        return {"results": formatted_results}
        
    except Exception as e:
        logger.error(f"Error in search_promotions_tool: {e}")
        # Return empty results on error
        return {"results": []}
