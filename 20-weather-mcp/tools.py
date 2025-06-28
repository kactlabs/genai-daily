import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_weather_for_city(city: str) -> str:
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "❌ API key not found in .env"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        res = requests.get(url)
        data = res.json()

        if res.status_code != 200:
            return f"❌ Error: {data.get('message', 'Invalid request')}"

        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        return (
            f"🌤️ Weather in {city.title()}:\n"
            f"- Temperature: {temp}°C\n"
            f"- Condition: {weather}\n"
            f"- Humidity: {humidity}%\n"
            f"- Wind Speed: {wind_speed} m/s"
        )
    except Exception as e:
        return f"❌ Request failed: {str(e)}"
