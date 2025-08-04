#!/usr/bin/env python3
"""
Simple script to run the PromoSearch MCP Server demo.
"""

import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Run the demo."""
    print("🚀 Starting PromoSearch MCP Server Demo")
    print("=" * 50)
    
    try:
        # Import and run the demo
        from agents.demo_agent import main as demo_main
        await demo_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n✅ Demo completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
