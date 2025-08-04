"""
Demo agent script showing how to use the PromoSearch MCP Server tools.
"""

import asyncio
import json
from typing import Dict, Any, List


# Mock MCP client functions (in real usage, these would be MCP calls)
async def call_mcp_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock function to simulate MCP tool calls.
    In real usage, this would be replaced with actual MCP client calls.
    """
    print(f"🔧 Calling MCP tool: {tool_name}")
    print(f"   Args: {json.dumps(args, indent=2)}")
    
    # Import the actual tool functions for demonstration
    if tool_name == "expand_query":
        from mcp_server.tools.expand_query import expand_query_tool
        result = await expand_query_tool(args["query"])
    elif tool_name == "search_promotions":
        from mcp_server.tools.search_promotions import search_promotions_tool
        result = await search_promotions_tool(args["query"], args["user_profile"])
    elif tool_name == "rank_promotions":
        from mcp_server.tools.rank_promotions import rank_promotions_tool
        result = await rank_promotions_tool(args["candidates"], args["user_profile"])
    elif tool_name == "optimize_ad_slots":
        from mcp_server.tools.optimize_ad_slots import optimize_ad_slots_tool
        result = await optimize_ad_slots_tool(args["search_results"], args["promotions"])
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    print(f"✅ Result: {json.dumps(result, indent=2)}")
    print("-" * 50)
    return result


async def demo_full_pipeline():
    """Demonstrate the complete PromoSearch pipeline."""
    print("🚀 PromoSearch MCP Server Demo")
    print("=" * 50)
    
    # Sample user query and profile
    query = "我想找最近 AWS 云主机有哪些优惠"
    user_profile = {
        "user_type": "professional",
        "interests": ["cloud", "aws", "hosting", "development"],
        "budget_level": "medium"
    }
    
    print(f"📝 Original Query: {query}")
    print(f"👤 User Profile: {json.dumps(user_profile, indent=2)}")
    print()
    
    # Step 1: Expand query
    print("🔍 Step 1: Query Expansion")
    expanded_result = await call_mcp_tool("expand_query", {"query": query})
    expanded_queries = expanded_result["expanded_queries"]
    
    # Step 2: Search promotions for each expanded query
    print("🔍 Step 2: Semantic Search")
    all_promotions = []
    for expanded_query in expanded_queries[:3]:  # Limit to top 3 for demo
        search_result = await call_mcp_tool("search_promotions", {
            "query": expanded_query,
            "user_profile": user_profile
        })
        all_promotions.extend(search_result["results"])
    
    # Remove duplicates based on ID
    seen_ids = set()
    unique_promotions = []
    for promo in all_promotions:
        if promo["id"] not in seen_ids:
            unique_promotions.append(promo)
            seen_ids.add(promo["id"])
    
    print(f"📊 Found {len(unique_promotions)} unique promotions")
    
    # Step 3: Rank promotions
    print("🔍 Step 3: Promotion Ranking")
    ranking_result = await call_mcp_tool("rank_promotions", {
        "candidates": unique_promotions,
        "user_profile": user_profile
    })
    ranked_promotions = ranking_result["ranked_promotions"]
    
    # Get top promotions with their details
    top_promotions = []
    promotion_lookup = {p["id"]: p for p in unique_promotions}
    
    for ranked_promo in ranked_promotions[:3]:  # Top 3
        promo_id = ranked_promo["id"]
        if promo_id in promotion_lookup:
            promo_details = promotion_lookup[promo_id].copy()
            promo_details["rank_score"] = ranked_promo["score"]
            top_promotions.append(promo_details)
    
    # Step 4: Optimize ad slots
    print("🔍 Step 4: Ad Slot Optimization")
    
    # Mock search results (in real usage, these would come from a search engine)
    mock_search_results = [
        "AWS EC2 Documentation - Learn about Amazon Elastic Compute Cloud instances",
        "AWS Pricing Calculator - Calculate your cloud computing costs",
        "AWS Free Tier - Get started with AWS for free",
        "Cloud Computing Best Practices - Guide to efficient cloud usage",
        "AWS Instance Types - Choose the right instance for your workload",
        "Server Migration to AWS - Step-by-step migration guide",
        "AWS Security Best Practices - Keep your cloud infrastructure secure",
        "Cost Optimization on AWS - Reduce your cloud spending"
    ]
    
    optimization_result = await call_mcp_tool("optimize_ad_slots", {
        "search_results": mock_search_results,
        "promotions": top_promotions
    })
    
    # Display final results
    print("🎯 Final Results with Optimized Ad Placement")
    print("=" * 50)
    
    for i, result in enumerate(optimization_result["injected_results"], 1):
        if result.startswith("🎯 [SPONSORED]"):
            print(f"\n🎯 AD SLOT {i}:")
            print(result)
        else:
            print(f"{i}. {result}")
    
    print("\n✨ Demo completed successfully!")


async def demo_individual_tools():
    """Demonstrate each tool individually."""
    print("\n🧪 Individual Tool Demonstrations")
    print("=" * 50)
    
    # Demo 1: Query Expansion
    print("\n1️⃣ Query Expansion Demo")
    await call_mcp_tool("expand_query", {
        "query": "cheap laptop deals"
    })
    
    # Demo 2: Semantic Search
    print("\n2️⃣ Semantic Search Demo")
    await call_mcp_tool("search_promotions", {
        "query": "cloud hosting services",
        "user_profile": {
            "user_type": "business",
            "interests": ["hosting", "cloud", "web"],
            "budget_level": "high"
        }
    })
    
    # Demo 3: Ranking
    print("\n3️⃣ Promotion Ranking Demo")
    sample_candidates = [
        {
            "id": "test-1",
            "title": "Test Promotion 1",
            "description": "Sample promotion for testing",
            "link": "https://example.com/1",
            "categories": ["cloud", "hosting"],
            "price_tier": "medium",
            "base_ctr": 0.1
        },
        {
            "id": "test-2", 
            "title": "Test Promotion 2",
            "description": "Another sample promotion",
            "link": "https://example.com/2",
            "categories": ["software", "productivity"],
            "price_tier": "low",
            "base_ctr": 0.15
        }
    ]
    
    await call_mcp_tool("rank_promotions", {
        "candidates": sample_candidates,
        "user_profile": {
            "user_type": "professional",
            "interests": ["cloud", "hosting"],
            "budget_level": "medium"
        }
    })
    
    # Demo 4: Ad Slot Optimization
    print("\n4️⃣ Ad Slot Optimization Demo")
    await call_mcp_tool("optimize_ad_slots", {
        "search_results": [
            "Best web hosting providers 2024",
            "How to choose a hosting plan",
            "Shared vs VPS hosting comparison",
            "Domain registration guide",
            "Website security best practices"
        ],
        "promotions": [
            {
                "id": "hosting-deal",
                "title": "Premium Web Hosting 50% Off",
                "description": "Get reliable web hosting with 99.9% uptime guarantee",
                "link": "https://example.com/hosting"
            }
        ]
    })


async def main():
    """Main demo function."""
    try:
        # Run full pipeline demo
        await demo_full_pipeline()
        
        # Run individual tool demos
        await demo_individual_tools()
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
