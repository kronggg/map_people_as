import aiohttp
from config import Config

class GeocodingError(Exception):
    """Кастомное исключение для ошибок геокодирования"""
    pass

class Geocoder:
    @staticmethod
    async def get_coordinates(city: str, language: str = "ru"):
        """Получение координат через OSM Nominatim"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{Config.OSM_NOMINATIM_URL}/search?q={city}&format=json&accept-language={language}"
                ) as response:
                    data = await response.json()
                    if data:
                        return float(data[0]['lat']), float(data[0]['lon'])
                    raise GeocodingError("Город не найден")
        except Exception as e:
            raise GeocodingError(f"Ошибка при запросе к OSM: {e}")

    @staticmethod
    async def reverse_geocode(lat: float, lon: float, language: str = "ru"):
        """Обратное геокодирование: координаты → адрес"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{Config.OSM_NOMINATIM_URL}/reverse?lat={lat}&lon={lon}&format=json&accept-language={language}"
                ) as response:
                    data = await response.json()
                    if data and 'display_name' in data:
                        return data['display_name']
                    raise GeocodingError("Не удалось определить адрес")
        except Exception as e:
            raise GeocodingError(f"Ошибка при запросе к OSM: {e}")