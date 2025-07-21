import asyncio
import sys
from pathlib import Path


sys.append(str(Path(__file__).parent.parent))

from src.confing import config
from src.utils.logger import logger
from src.api.routes import create_flask_app
from src.devices.yandex_station import YandexStationManager

class SmartHomeSystem:
    
    def __init__(self):
        self.flask_app = None
        self.device_manager = None
        self.running = False

        logger.info(f"Initializing{config.APP_NAME} v{config.APP_VERSION}")
        logger.info(f"Environment: {config.ENVIRONMENT}")
        logger.info(f"Debug mode: {config.DEBUG}")

    def initialize(self):
        try:
            self.flask_app = create_flask_app()
            logger.info("Flask app created")

            self.device_manager = YandexStationManager()
            logger.info("Device manager initialized")

            self.running = True
            logger.info("System is running")
        except Exception as e:
            logger.error(f"failed to initialize the system: {e}")
            raise
    
    def start_flask_server(self):
        logger.info(f"Starting Flask server on {config.FLASK_HOST}:{config.FLASK_PORT}")

        try:
            self.flask_app.run(
                host=config.FLASK_HOST,
                port=config.FLASK_PORT,
                debug=config.DEBUG
                use_reloafer=False
            )
        except Exception as e:
            logger.error(f"Failed to start Flask server: {e}")
            raise

    def run(self):
        try:
            self.initialize()

            logger.info("Starting Flask server...")
            logger.info(f"API will be availabe as http://{config.FLASK_HOST}:{config.FLASK_PORT}")

            self.start_flask_server()

        except KeyboardInterrupt:
            logger.info("Received KeyboardInterrupt, shutting down...")
        except Exception as e:
            logger.error(f"Failed to run the system: {e}")
            raise
        finally:
            self.shutdown()
            logger.info("System shutdown")

    def shutdown(self):
        logger.info("Shutting down the system...")
        self.running = False

        if self.device_manager:
            self.device_manager.shutdown()

        logger.info("System shutdown complete")

    def main():
        system = SmartHomeSystem()
        system.run()
    
    
    if __name__=="__main__":
        main() 
        

