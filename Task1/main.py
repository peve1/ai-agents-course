import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Mock nástroje pro získání JSON dat počasí.
def get_current_weather(location: str, unit: str = "celsius") -> str:
    dummy_data = {
        "praha": {"teplota": 21, "pocasi": "polojasno"},
        "brno": {"teplota": 19, "pocasi": "zataženo"},
    }
    location_data = dummy_data.get(location.strip().lower(), {"teplota": 0, "pocasi": "neznámo"})
    result = {
        "location": location,
        "unit": unit,
        "temperature": location_data["teplota"],
        "condition": location_data["pocasi"],
    }
    return json.dumps(result)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Použij tuto funkci pro získání aktuálního počasí pro zadané město.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Název města, např. Praha, Brno, Ostrava",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Jednotka teploty",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

AVAILABLE_FUNCTIONS = {
    "get_current_weather": get_current_weather,
}

# Hardcoded uživatelský dotaz
user_prompt = "Jaké je aktuálně počasí v Praze?"

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key or api_key == "replace-me-with-key":
    raise RuntimeError("env variable 'OPENAI_API_KEY' je povinná a není nakonfigurována.")

client = OpenAI(api_key=api_key)
model = "gpt-5.4-mini"

messages = [
    {"role": "system", "content": "Jsi asistent na počasí. Používej nástroje když je to vhodné."},
    {"role": "user", "content": user_prompt},
]

response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=TOOLS,
    tool_choice="auto",
)

message = response.choices[0].message
tool_calls = message.tool_calls

if not tool_calls:
    print(f"no_tool: {message.content}")
else:
    messages.append(message)

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

        if function_to_call is None:
            function_response = json.dumps({"error": f"Neznámý nástroj: {function_name}"})
        else:
            function_response = function_to_call(**function_args)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_response,
            }
        )

    second_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    print(f"tool: {second_response.choices[0].message.content}")
