import asyncio
import sys

from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

load_dotenv()

INSTRUCTIONS = (
    "Jsi specializovaný výhradně na počasí. "
    "Pro zjištění aktuálního počasí vždy použij nástroj get_weather. "
    "Odpovídej stručně a v češtině."
)

# Uživatelský dotaz na počasí - možné libovolně měnit.
USER_QUERY = "Jaké je aktuální počasí v Praze?"

async def main() -> None:
    async with MCPServerStdio(
        name="weather-mcp",
        params={"command": sys.executable, "args": ["weather_server.py"]},
    ) as weather_server:
        agent = Agent(
            name="WeatherAgent",
            instructions=INSTRUCTIONS,
            mcp_servers=[weather_server],
            model="gpt-5.4-mini"
        )

        print(f"Dotaz: {USER_QUERY}")
        result = await Runner.run(agent, USER_QUERY)
        print(f"Odpověď: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
