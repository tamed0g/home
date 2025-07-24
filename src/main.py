import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import config
from src.utils.logger import logger
from src.api.routes import create_flask_app

def main():
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Debug: {config.DEBUG}")
    
    app = create_flask_app()
    
    logger.info(f"Starting server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.DEBUG
    )

if __name__ == "__main__":
    main()