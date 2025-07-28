import asyncio
import aiohttp
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
import logging

class YandexStation:
    """Единственная Яндекс Станция в системе"""
    
    def __init__(self, name: str = "Яндекс Станция", ip_address: str = None):
        # ИСПРАВЛЕНО: Убрали super().__init__() и добавили все атрибуты вручную
        self.device_id = "main_station"
        self.name = name
        self.device_type = "yandex_station"
        self.ip_address = ip_address
        self.session = None
        self.volume = 50
        self.is_playing = False
        self.current_track = None
        self.is_connected = False
        self.last_seen = None
        self.properties = {}
        self.command_handlers: Dict[str, Callable] = {}
        
        # ИСПРАВЛЕНО: Добавили простой логгер
        self.logger = logging.getLogger(f"YandexStation.{name}")
        
        # Регистрируем стандартные команды
        self._register_default_commands()
        
    def _register_default_commands(self):
        """Регистрация стандартных команд"""
        
        def lights_control(params):
            action = params.get("action", "toggle")
            room = params.get("room", "вся квартира")
            
            if action == "on":
                message = f"Включаю свет в {room}"
            elif action == "off":
                message = f"Выключаю свет в {room}"
            else:
                message = f"Переключаю свет в {room}"
            
            return {"status": "success", "message": message, "speech": message}
        
        def climate_control(params):
            temperature = params.get("temperature", 22)
            room = params.get("room", "дом")
            message = f"Устанавливаю температуру {temperature}°C в {room}"
            return {"status": "success", "message": message, "speech": message}
        
        def security_system(params):
            action = params.get("action", "status")
            
            if action == "arm":
                message = "Включаю охрану. Система активна."
            elif action == "disarm":
                message = "Отключаю охрану. Дом в безопасности."
            else:
                message = "Система безопасности в норме."
                
            return {"status": "success", "message": message, "speech": message}
        
        def weather_info(params):
            city = params.get("city", "вашем городе")
            message = f"Погода в {city}: солнечно, плюс 20 градусов"
            return {"status": "success", "message": message, "speech": message}
        
        def news_info(params):
            category = params.get("category", "главные")
            message = f"Последние {category} новости загружаются..."
            return {"status": "success", "message": message, "speech": message}
        
        # Регистрируем команды
        self.command_handlers.update({
            "lights": lights_control,
            "climate": climate_control,
            "security": security_system,
            "weather": weather_info,
            "news": news_info
        })
        
    def register_command(self, command_name: str, handler: Callable):
        """Регистрация новой команды"""
        self.command_handlers[command_name] = handler
        self.logger.info(f"Registered command: {command_name}")
        
    # ИСПРАВЛЕНО: Добавили метод update_property
    def update_property(self, key: str, value: Any):
        """Обновление свойства устройства"""
        self.properties[key] = value
        self.last_seen = datetime.now()
        
    async def connect(self) -> bool:
        """Подключение к Яндекс Станции"""
        try:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            
            if self.ip_address:
                await self._test_connection()
            
            self.is_connected = True
            self.last_seen = datetime.now()
            self.logger.info(f"Connected to Yandex Station: {self.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Отключение от Яндекс Станции"""
        if self.session:
            await self.session.close()
        self.is_connected = False
        self.logger.info("Disconnected from Yandex Station")
    
    async def _test_connection(self):
        """Тестирование подключения"""
        if not self.session or not self.ip_address:
            return False
            
        try:
            async with self.session.get(f"http://{self.ip_address}/api/info") as response:
                if response.status == 200:
                    data = await response.json()
                    self.update_property("device_info", data)
                    return True
        except:
            pass
        return False
    
    async def send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Отправка команды станции"""
        if not self.is_connected:
            return {"error": "Station not connected"}
        
        params = params or {}
        
        try:
            # Проверяем пользовательские команды
            if command in self.command_handlers:
                result = self.command_handlers[command](params)
                self.last_seen = datetime.now()
                return result
            
            # Базовые команды станции
            result = await self._execute_station_command(command, params)
            
            # Попытка отправить реальную команду через API
            if self.ip_address and self.session:
                await self._send_real_command(command, params)
            
            self.last_seen = datetime.now()
            return result
            
        except Exception as e:
            self.logger.error(f"Command failed: {command}, error: {e}")
            return {"error": str(e)}
    
    async def _execute_station_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Базовые команды станции"""
        
        if command == "play":
            query = params.get("query", "музыка")
            self.is_playing = True
            self.current_track = query
            self.update_property("is_playing", True)
            self.update_property("current_track", query)
            return {
                "status": "success", 
                "message": f"Включаю: {query}",
                "speech": f"Включаю {query}"
            }
        
        elif command == "stop":
            self.is_playing = False
            self.current_track = None
            self.update_property("is_playing", False)
            self.update_property("current_track", None)
            return {
                "status": "success", 
                "message": "Воспроизведение остановлено",
                "speech": "Останавливаю воспроизведение"
            }
        
        elif command == "pause":
            self.is_playing = False
            self.update_property("is_playing", False)
            return {
                "status": "success", 
                "message": "Воспроизведение приостановлено",
                "speech": "Ставлю на паузу"
            }
        
        elif command == "resume":
            self.is_playing = True
            self.update_property("is_playing", True)
            return {
                "status": "success", 
                "message": "Воспроизведение возобновлено",
                "speech": "Продолжаю воспроизведение"
            }
        
        elif command == "volume":
            volume = params.get("level", 50)
            volume = max(0, min(100, int(volume)))
            self.volume = volume
            self.update_property("volume", volume)
            return {
                "status": "success", 
                "message": f"Громкость установлена: {volume}%",
                "speech": f"Устанавливаю громкость {volume} процентов"
            }
        
        elif command == "say":
            text = params.get("text", "")
            return {
                "status": "success", 
                "message": f"Озвучиваю: {text}",
                "speech": text
            }
        
        else:
            return {"error": f"Unknown command: {command}"}
    
    async def _send_real_command(self, command: str, params: Dict[str, Any]):
        """Отправка реальной команды через API"""
        if not self.session or not self.ip_address:
            return
        
        try:
            payload = {"command": command, "params": params}
            async with self.session.post(f"http://{self.ip_address}/api/command", json=payload) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            self.logger.debug(f"Real command failed (expected in demo): {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Получение полного статуса станции"""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "is_connected": self.is_connected,
            "is_playing": self.is_playing,
            "volume": self.volume,
            "current_track": self.current_track,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "properties": self.properties,
            "available_commands": list(self.command_handlers.keys()) + [
                "play", "stop", "pause", "resume", "volume", "say"
            ]
        }
    
    def add_custom_command(self, name: str, description: str, handler: Callable):
        """Удобный метод для добавления пользовательских команд"""
        def wrapper(params):
            try:
                result = handler(params)
                if isinstance(result, str):
                    return {"status": "success", "message": result, "speech": result}
                return result
            except Exception as e:
                return {"error": str(e)}
        
        self.register_command(name, wrapper)
        self.logger.info(f"Added custom command: {name} - {description}")


# Простые функции для добавления команд
def create_simple_command(message_template: str):
    """Создание простой команды с текстовым ответом"""
    def handler(params):
        message = message_template.format(**params)
        return {"status": "success", "message": message, "speech": message}
    return handler

def create_device_command(device_name: str, actions: Dict[str, str]):
    """Создание команды управления устройством"""
    def handler(params):
        action = params.get("action", "toggle").lower()
        if action in actions:
            message = actions[action].format(device=device_name, **params)
        else:
            available = ", ".join(actions.keys())
            message = f"Неизвестное действие для {device_name}. Доступные: {available}"
        
        return {"status": "success", "message": message, "speech": message}
    return handler