import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.config import config
from src.utils.logger import logger
from src.api.routes import create_flask_app
from src.devices.yandex_station import YandexStation


class SmartHomeSystem:
    
    def __init__(self):
        self.flask_app = None
        self.running = False
        self.yandex_station = None

        logger.info(f"Initializing {config.APP_NAME} v{config.APP_VERSION}")
        logger.info(f"Environment: {config.ENVIRONMENT}")
        logger.info(f"Debug mode: {config.DEBUG}")

    def initialize(self):
        try:
            station_name = "Главная станция"
            station_ip = "192.168.0.16"  #заменить ip на свои

            self.yandex_station = YandexStation(station_name, station_ip)
            logger.info(f"✅ Yandex Station created: {station_name}")

            self.flask_app = create_flask_app(self.yandex_station)
            logger.info("Flask app created")


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
                debug=config.DEBUG,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Failed to start Flask server: {e}")
            raise


    async def _get_current_time(self):
        """Получение текущего времени"""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%H:%M")
    

    async def start_system(self):
        """Запуск системы"""
        try:
            # Подключаемся к станции
            logger.info("Connecting to Yandex Station...")
            connection_success = await self.yandex_station.connect()
            
            if connection_success:
                logger.info("✅ Yandex Station connected successfully")
            else:
                logger.warning("⚠️  Yandex Station connection failed, but system will continue")
            
            logger.info("System is ready!")
            logger.info(f"🌐 API available at: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            raise        
    
    

    def run(self):
        try:
            self.initialize()
            asyncio.run(self.start_system())
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
     
        if self.yandex_station:
            try:
                asyncio.run(self.yandex_station.disconnect())
            except Exception as e:
                logger.error(f"Error during station disconnect: {e}")


        logger.info("System shutdown complete")

# Исправлено: функция main() вынесена из класса
def main():
    system = SmartHomeSystem()
    system.run()

if __name__ == "__main__":
    main()