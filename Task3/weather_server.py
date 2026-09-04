import httpx
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("weather")

# Mapování enumu počasí na české názvy
WEATHER_CODES = {
    0: "jasno",
    1: "polojasno",
    2: "oblačno",
    3: "zataženo",
    45: "mlha",
    48: "mrznoucí mlha",
    51: "slabé mrholení",
    61: "slabý déšť",
    63: "déšť",
    65: "silný déšť",
    71: "slabé sněžení",
    73: "sněžení",
    75: "silné sněžení",
    80: "přeháňky",
    95: "bouřka"
}

@mcp.tool()
async def get_weather(city: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        geo_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "cs"},
        )
        geo_response.raise_for_status()
        results = geo_response.json().get("results")
        if not results:
            return f"Město '{city}' se nepodařilo najít."

        location = results[0]
        location_latitude = location["latitude"]
        location_longitude = location["longitude"]

        meteo_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": location_latitude, "longitude": location_longitude, "current_weather": True},
        )
        meteo_response.raise_for_status()
        current = meteo_response.json()["current_weather"]
        condition = WEATHER_CODES.get(current["weathercode"], "???")

        return (
            f"Počasí v {location['name']} ({location.get('country', '')}): "
            f"{current['temperature']}°C, {condition}, "
            f"vítr {current['windspeed']} km/h."
        )

# safe entry pokud se spustí samotný script
if __name__ == "__main__":
    mcp.run()
