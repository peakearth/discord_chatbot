import discord
from discord.ext import commands
import os

async def load_cogs(bot):
    cogs_dir = os.path.join('discord_chatbot', 'cogs')
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py'):
            cog_name = filename[:-3]  # `.py` 확장자 제거
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                print(f'✅ Cog 로드 완료: {cog_name}')
            except Exception as e:
                print(f'⚠️ {cog_name} 로드 실패: {e}')

async def main():
    prefix = '!'
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=prefix, intents=intents)

    # Cog 로드
    await load_cogs(bot)

    # 토큰 읽기
    with open('discord_chatbot/token.txt', 'r') as f:
        token = f.read().strip()

    await bot.start(token)

# 비동기 실행을 위해 아래와 같이 변경
import asyncio
asyncio.run(main())
