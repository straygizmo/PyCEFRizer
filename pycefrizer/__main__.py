"""
Allow running MCP server with: python -m pycefrizer.mcp_server
"""
import sys

if len(sys.argv) > 1 and sys.argv[1] == "mcp_server":
    from .mcp_server import main
    import asyncio
    asyncio.run(main())
else:
    from .cli import main
    main()