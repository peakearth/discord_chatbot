import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# OpenWeatherMap API 키
with open('discord_chatbot/key/weather_api.txt', 'r') as f:
    API_KEY = f.read().strip()

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@bot.command(name="날씨")
async def weather(ctx, *, city: str):
    # API 요청
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  # 섭씨 온도
        'lang': 'kr'  # 한국어 지원
    }
    response = requests.get(BASE_URL, params=params).json()

    # 날씨 정보 추출
    if response.get('cod') != 200:
        await ctx.send("❌ 도시를 찾을 수 없습니다.")
        return

    weather_data = response['weather'][0]
    main_data = response['main']
    wind_data = response['wind']

    # Embed 생성
    embed = discord.Embed(
        title=f"{city}의 날씨",
        description=weather_data['description'],
        color=0x00ff00
    )
    embed.add_field(name="🌡️ 온도", value=f"{main_data['temp']}°C", inline=False)
    embed.add_field(name="💧 습도", value=f"{main_data['humidity']}%", inline=False)
    embed.add_field(name="🌬️ 풍속", value=f"{wind_data['speed']} m/s", inline=False)
    embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{weather_data['icon']}@2x.png")

    await ctx.send(embed=embed)

# 봇 실행
bot.run('YOUR_BOT_TOKEN')