import sys
import logging
import argparse
import uvicorn
from app.database import init_db, seed_db
from app.tools import mcp
from app.auth import AuthMiddleware

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description="Run Multi-User Notes MCP Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the HTTP server on")
    args = parser.parse_args()

    logging.info("Initializing database...")
    init_db()
    seed_db()
    logging.info("Database initialized and seeded.")

    # Setup the streamable HTTP app
    app = mcp.streamable_http_app()
    
    # Add authentication middleware
    app.add_middleware(AuthMiddleware)

    logging.info(f"Starting MCP Notes Server on streamable-http at http://127.0.0.1:{args.port}/mcp")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_config=None)

if __name__ == "__main__":
    main()
