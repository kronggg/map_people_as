import aiohttp
from config import Config
from typing import Tuple, Optional
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

class GeocodingError(Exception):
    """Кастомное исключение для ошибок геокодирования"""
    pass

@dataclass
class Location:
    latitude: float
    longitude: float
    display_name: Optional[str] = None

class Geocoder:
    """Класс для работы с API OpenStreetMap Nominatim"""
    
    _BASE_URL = "https://nominatim.openstreetmap.org"
    _USER_AGENT = "GDPR-Bot/1.0 (Professional Network Service)"
    _TIMEOUT = 10  # сек

    @classmethod
    async def _make_request(cls, endpoint: str, params: dict) -> dict:
        """Базовый метод для выполнения запросов к API"""
        headers = {
            "User-Agent": cls._USER_AGENT,
            "Accept": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{cls._BASE_URL}/{endpoint}",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=cls._TIMEOUT)
                ) as response:
                    if response.status != 200:
                        raise GeocodingError(f"API error: {response.status}")
                    
                    data = await response.text()
                    return json.loads(data)
                    
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            logger.error(f"Geocoding request failed: {e}")
            raise GeocodingError("Ошибка подключения к сервису геокодирования")

    @classmethod
    async def get_coordinates(cls, city: str) -> Location:
        """
        Прямое геокодирование: город → координаты
        
        Args:
            city: Название города на любом языке
        
        Returns:
            Location: Объект с координатами и названием
        
        Raises:
            GeocodingError: Если город не найден или произошла ошибка
        """
        params = {
            "q": city,
            "format": "json",
            "limit": 1,
            "accept-language": Config.GEOCODING_LANGUAGE
        }

        try:
            data = await cls._make_request("search", params)
            if not data:
                raise GeocodingError("Город не найден")

            return Location(
                latitude=float(data[0]['lat']),
                longitude=float(data[0]['lon']),
                display_name=data[0].get('display_name')
            )
            
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Invalid API response: {e}")
            raise GeocodingError("Некорректный ответ от сервиса геокодирования")

    @classmethod
    async def reverse_geocode(cls, lat: float, lon: float) -> str:
        """
        Обратное геокодирование: координаты → адрес
        
        Args:
            lat: Широта
            lon: Долгота
        
        Returns:
            str: Отформатированное название места
        
        Raises:
            GeocodingError: Если локация не найдена
        """
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,  # Уровень детализации
            "accept-language": Config.GEOCODING_LANGUAGE
        }

        try:
            data = await cls._make_request("reverse", params)
            return data.get('display_name', 'Неизвестное местоположение')
            
        except KeyError as e:
            logger.error(f"Reverse geocoding failed: {e}")
            raise GeocodingError("Ошибка определения местоположения")

    @classmethod
    async def validate_city(cls, city: str) -> bool:
        """Проверка существования города через геокодирование"""
        try:
            await cls.get_coordinates(city)
            return True
        except GeocodingError:
            return False