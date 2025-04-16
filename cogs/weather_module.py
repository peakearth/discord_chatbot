import discord
from discord.ext import commands
import requests
from discord import Embed
import os

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
        self.API_KEY = self._load_api_key()  # API 키 로드

    def _load_api_key(self):
        # 텍스트 파일에서 API 키를 로드.
        try:
            with open("discord_chatbot/key/weather_api.txt", "r") as f:
                return f.read().strip()  # 파일 내용 읽기 및 공백 제거
        except FileNotFoundError:
            print("❌ weather_api.txt 파일을 찾을 수 없습니다.")
            return None
        except Exception as e:
            print(f"❌ API 키 로드 중 오류 발생: {e}")
            return None

    @commands.command(name="날씨")
    async def weather(self, ctx, *, city: str):
        # 도시 이름을 입력하면 현재 날씨 정보를 알려줍니다.
        if not self.API_KEY:
            await ctx.send("❌ API 키를 로드할 수 없습니다. 관리자에게 문의하세요.")
            return

        try:
            # API 요청 (현재 날씨)
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

            # 현재 날씨 데이터 추출
            weather_data = response['weather'][0]
            main_data = response['main']
            wind_data = response['wind']

            # Embed 생성
            embed = Embed(
                title=f"{city}의 현재 날씨",
                description=weather_data['description'],
                color=0x00ff00
            )
            embed.add_field(name="🌡️ 온도", value=f"{main_data['temp']}°C", inline=False)
            embed.add_field(name="🌡️ 체감 온도", value=f"{main_data['feels_like']}°C", inline=False)
            embed.add_field(name="💧 습도", value=f"{main_data['humidity']}%", inline=False)
            embed.add_field(name="🌬️ 풍속", value=f"{wind_data['speed']} m/s", inline=False)
            embed.add_field(name="📊 기압", value=f"{main_data['pressure']} hPa", inline=False)
            embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{weather_data['icon']}@2x.png")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ 오류가 발생했습니다: {str(e)}")
            print(f"[DEBUG] Error: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))