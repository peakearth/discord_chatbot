import discord
from discord.ext import commands
import requests
from discord import Embed

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.API_KEY = "YOUR_API_KEY"  # OpenWeatherMap API 키
        self.BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    @commands.command(name="날씨")
    async def weather(self, ctx, *, city: str):
        """도시 이름을 입력하면 날씨 정보를 알려줍니다."""
        try:
            # API 요청
            params = {
                'q': city,
                'appid': self.API_KEY,
                'units': 'metric',  # 섭씨 온도
                'lang': 'kr'        # 한국어 지원
            }
            response = requests.get(self.BASE_URL, params=params).json()

            # 오류 처리
            if response.get('cod') != 200:
                await ctx.send(f"❌ 오류: {response.get('message', '도시를 찾을 수 없습니다.')}")
                return

            # 날씨 데이터 추출
            weather_data = response['weather'][0]
            main_data = response['main']
            wind_data = response['wind']

            # Embed 생성
            embed = Embed(
                title=f"{city}의 날씨",
                description=weather_data['description'],
                color=0x00ff00
            )
            embed.add_field(name="🌡️ 온도", value=f"{main_data['temp']}°C", inline=False)
            embed.add_field(name="💧 습도", value=f"{main_data['humidity']}%", inline=False)
            embed.add_field(name="🌬️ 풍속", value=f"{wind_data['speed']} m/s", inline=False)
            embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{weather_data['icon']}@2x.png")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")
            print(f"[DEBUG] Error: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))