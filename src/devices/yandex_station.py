import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from src.config import config
from src.utils.logger import get_logger

logger = get_logger("yandex_station")


class YandexDevice:
    """Represents a single Yandex device"""
    
    def __init__(self, device_data: Dict[str, Any]):
        self.id = device_data.get('id')
        self.name = device_data.get('name', 'Unknown Device')
        self.type = device_data.get('type', 'unknown')
        self.platform = device_data.get('platform', 'yandexstation')
        self.capabilities = device_data.get('capabilities', [])
        self.online = device_data.get('online', False)
        self.last_updated = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'platform': self.platform,
            'capabilities': self.capabilities,
            'online': self.online,
            'last_updated': self.last_updated.isoformat()
        }


class YandexStationManager:
    """Manager for Yandex Station devices"""
    
    def __init__(self):
        self.oauth_token = config.YANDEX_OAUTH_TOKEN
        self.api_key = config.YANDEX_API_KEY
        self.skill_id = config.YANDEX_SKILL_ID
        
        self.devices: Dict[str, YandexDevice] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        
        self.base_url = "https://api.iot.yandex.net/v1.0"
        
        logger.info("YandexStationManager initialized")
        
        if not self.oauth_token:
            logger.warning("Yandex OAuth token not provided. Some functions will not work.")
    
    async def initialize(self):
        """Initialize the manager"""
        try:
            if not self.oauth_token:
                logger.error("Cannot initialize without OAuth token")
                return False
            
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.oauth_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            self.running = True
            await self.discover_devices()
            logger.info("YandexStationManager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize YandexStationManager: {e}")
            return False
    
    async def discover_devices(self):
        """Discover Yandex devices"""
        try:
            if not self.session:
                logger.error("Session not initialized")
                return
            
            url = f"{self.base_url}/user/info"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    devices_data = data.get('devices', [])
                    
                    for device_data in devices_data:
                        device = YandexDevice(device_data)
                        self.devices[device.id] = device
                        logger.info(f"Discovered device: {device.name} ({device.id})")
                    
                    logger.info(f"Discovered {len(self.devices)} devices")
                else:
                    logger.error(f"Failed to discover devices: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
    
    async def send_command(self, device_id: str, command: str, parameters: Dict = None) -> bool:
        """Send command to a specific device"""
        try:
            if not self.session:
                logger.error("Session not initialized")
                return False
            
            if device_id not in self.devices:
                logger.error(f"Device {device_id} not found")
                return False
            
            url = f"{self.base_url}/devices/{device_id}/actions"
            
            payload = {
                "actions": [{
                    "type": command,
                    "parameters": parameters or {}
                }]
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Command '{command}' sent successfully to device {device_id}")
                    return True
                else:
                    logger.error(f"Failed to send command: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
    
    async def speak_text(self, device_id: str, text: str) -> bool:
        """Make device speak text"""
        return await self.send_command(device_id, "speak", {"text": text})
    
    async def play_music(self, device_id: str, query: str = None) -> bool:
        """Play music on device"""
        parameters = {}
        if query:
            parameters["query"] = query
        
        return await self.send_command(device_id, "play_music", parameters)
    
    async def stop_music(self, device_id: str) -> bool:
        """Stop music on device"""
        return await self.send_command(device_id, "stop", {})
    
    async def set_volume(self, device_id: str, volume: int) -> bool:
        """Set device volume (0-100)"""
        volume = max(0, min(100, volume))  # Clamp between 0-100
        return await self.send_command(device_id, "set_volume", {"volume": volume})
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of all devices"""
        return [device.to_dict() for device in self.devices.values()]
    
    def get_device(self, device_id: str) -> Optional[YandexDevice]:
        """Get specific device by ID"""
        return self.devices.get(device_id)
    
    def is_device_online(self, device_id: str) -> bool:
        """Check if device is online"""
        device = self.get_device(device_id)
        return device.online if device else False
    
    async def refresh_devices(self):
        """Refresh device list"""
        await self.discover_devices()
    
    def shutdown(self):
        """Shutdown the manager"""
        logger.info("Shutting down YandexStationManager")
        self.running = False
        
        if self.session:
            # Note: In production, you should properly close the session
            # This is a simplified version
            try:
                asyncio.create_task(self.session.close())
            except Exception as e:
                logger.error(f"Error closing session: {e}")
    
    # Synchronous wrapper methods for Flask compatibility
    def sync_speak_text(self, device_id: str, text: str) -> bool:
        """Synchronous wrapper for speak_text"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.speak_text(device_id, text))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in sync_speak_text: {e}")
            return False
    
    def sync_play_music(self, device_id: str, query: str = None) -> bool:
        """Synchronous wrapper for play_music"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.play_music(device_id, query))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in sync_play_music: {e}")
            return False
    
    def sync_initialize(self) -> bool:
        """Synchronous wrapper for initialize"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.initialize())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in sync_initialize: {e}")
            return False