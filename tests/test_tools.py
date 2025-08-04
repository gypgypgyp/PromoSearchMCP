"""
Basic tests for PromoSearch MCP Server tools.
"""

import pytest
import asyncio
from typing import Dict, Any

# Import the tool functions
from mcp_server.tools.expand_query import expand_query_tool
from mcp_server.tools.search_promotions import search_promotions_tool
from mcp_server.tools.rank_promotions import rank_promotions_tool
from mcp_server.tools.optimize_ad_slots import optimize_ad_slots_tool


class TestExpandQuery:
    """Test query expansion functionality."""
    
    @pytest.mark.asyncio
    async def test_expand_query_basic(self):
        """Test basic query expansion."""
        result = await expand_query_tool("cloud hosting")
        
        assert "expanded_queries" in result
        assert isinstance(result["expanded_queries"], list)
        assert len(result["expanded_queries"]) > 0
        assert "cloud hosting" in result["expanded_queries"]  # Original should be included
    
    @pytest.mark.asyncio
    async def test_expand_query_chinese(self):
        """Test query expansion with Chinese text."""
        result = await expand_query_tool("我想找AWS云主机优惠")
        
        assert "expanded_queries" in result
        assert isinstance(result["expanded_queries"], list)
        assert len(result["expanded_queries"]) > 0


class TestSearchPromotions:
    """Test semantic search functionality."""
    
    @pytest.mark.asyncio
    async def test_search_promotions_basic(self):
        """Test basic promotion search."""
        user_profile = {
            "user_type": "professional",
            "interests": ["cloud", "hosting"],
            "budget_level": "medium"
        }
        
        result = await search_promotions_tool("cloud hosting", user_profile)
        
        assert "results" in result
        assert isinstance(result["results"], list)
        
        if len(result["results"]) > 0:
            promotion = result["results"][0]
            assert "id" in promotion
            assert "title" in promotion
            assert "description" in promotion
            assert "link" in promotion
            assert "score" in promotion
    
    @pytest.mark.asyncio
    async def test_search_promotions_empty_query(self):
        """Test search with empty query."""
        user_profile = {
            "user_type": "casual",
            "interests": [],
            "budget_level": "low"
        }
        
        result = await search_promotions_tool("", user_profile)
        
        assert "results" in result
        assert isinstance(result["results"], list)


class TestRankPromotions:
    """Test promotion ranking functionality."""
    
    @pytest.mark.asyncio
    async def test_rank_promotions_basic(self):
        """Test basic promotion ranking."""
        candidates = [
            {
                "id": "test-1",
                "title": "Test Promotion 1",
                "description": "Cloud hosting service",
                "link": "https://example.com/1",
                "categories": ["cloud", "hosting"],
                "price_tier": "medium",
                "base_ctr": 0.1
            },
            {
                "id": "test-2",
                "title": "Test Promotion 2", 
                "description": "Mobile phone deal",
                "link": "https://example.com/2",
                "categories": ["mobile", "phone"],
                "price_tier": "high",
                "base_ctr": 0.15
            }
        ]
        
        user_profile = {
            "user_type": "professional",
            "interests": ["cloud", "hosting"],
            "budget_level": "medium"
        }
        
        result = await rank_promotions_tool(candidates, user_profile)
        
        assert "ranked_promotions" in result
        assert isinstance(result["ranked_promotions"], list)
        assert len(result["ranked_promotions"]) == 2
        
        # Check that results have required fields
        for ranked_promo in result["ranked_promotions"]:
            assert "id" in ranked_promo
            assert "score" in ranked_promo
            assert isinstance(ranked_promo["score"], (int, float))
    
    @pytest.mark.asyncio
    async def test_rank_promotions_empty_candidates(self):
        """Test ranking with empty candidates list."""
        user_profile = {
            "user_type": "casual",
            "interests": [],
            "budget_level": "low"
        }
        
        result = await rank_promotions_tool([], user_profile)
        
        assert "ranked_promotions" in result
        assert result["ranked_promotions"] == []


class TestOptimizeAdSlots:
    """Test ad slot optimization functionality."""
    
    @pytest.mark.asyncio
    async def test_optimize_ad_slots_basic(self):
        """Test basic ad slot optimization."""
        search_results = [
            "Best cloud hosting providers 2024",
            "How to choose web hosting",
            "Cloud computing guide",
            "Server management tips",
            "Website performance optimization"
        ]
        
        promotions = [
            {
                "id": "hosting-deal",
                "title": "Premium Web Hosting 50% Off",
                "description": "Get reliable hosting with 99.9% uptime",
                "link": "https://example.com/hosting"
            }
        ]
        
        result = await optimize_ad_slots_tool(search_results, promotions)
        
        assert "injected_results" in result
        assert isinstance(result["injected_results"], list)
        assert len(result["injected_results"]) >= len(search_results)
        
        # Check that ads are properly marked
        has_sponsored_content = any(
            "🎯 [SPONSORED]" in item 
            for item in result["injected_results"]
        )
        assert has_sponsored_content
    
    @pytest.mark.asyncio
    async def test_optimize_ad_slots_no_promotions(self):
        """Test optimization with no promotions."""
        search_results = ["Result 1", "Result 2", "Result 3"]
        
        result = await optimize_ad_slots_tool(search_results, [])
        
        assert "injected_results" in result
        assert result["injected_results"] == search_results
    
    @pytest.mark.asyncio
    async def test_optimize_ad_slots_empty_results(self):
        """Test optimization with empty search results."""
        promotions = [
            {
                "id": "test-promo",
                "title": "Test Promotion",
                "description": "Test description",
                "link": "https://example.com"
            }
        ]
        
        result = await optimize_ad_slots_tool([], promotions)
        
        assert "injected_results" in result
        assert result["injected_results"] == []


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test the complete PromoSearch pipeline."""
        # Step 1: Expand query
        query = "cloud hosting deals"
        expanded_result = await expand_query_tool(query)
        assert len(expanded_result["expanded_queries"]) > 0
        
        # Step 2: Search promotions
        user_profile = {
            "user_type": "business",
            "interests": ["hosting", "cloud", "web"],
            "budget_level": "medium"
        }
        
        search_result = await search_promotions_tool(
            expanded_result["expanded_queries"][0], 
            user_profile
        )
        promotions = search_result["results"]
        
        if len(promotions) > 0:
            # Step 3: Rank promotions
            ranking_result = await rank_promotions_tool(promotions, user_profile)
            ranked_promotions = ranking_result["ranked_promotions"]
            
            assert len(ranked_promotions) == len(promotions)
            
            # Step 4: Optimize ad slots
            mock_search_results = [
                "Cloud hosting comparison",
                "Best hosting providers",
                "Web hosting guide"
            ]
            
            # Get top promotions with details
            top_promotions = []
            promotion_lookup = {p["id"]: p for p in promotions}
            
            for ranked_promo in ranked_promotions[:2]:
                if ranked_promo["id"] in promotion_lookup:
                    promo_details = promotion_lookup[ranked_promo["id"]].copy()
                    top_promotions.append(promo_details)
            
            optimization_result = await optimize_ad_slots_tool(
                mock_search_results, 
                top_promotions
            )
            
            injected_results = optimization_result["injected_results"]
            assert len(injected_results) >= len(mock_search_results)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
