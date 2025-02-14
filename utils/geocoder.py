import aiohttp
from config import Config

class Geocoder:
    @staticmethod
    async def get_coordinates(city: str, language: str = "ru"):
        """Получение координат через OSM Nominatim"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{Config.OSM_NOMINATIM_URL}/search?q={city}&format=json&accept-language={language}"
            ) as response:
                data = await response.json()
                if data:
                    return float(data[0]['lat']), float(data[0]['lon'])
                raise ValueError("Город не найден")