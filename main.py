import discord
from discord.ext import commands

# 봇 객체 생성
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용을 읽을 수 있는 권한 추가
bot = commands.Bot(command_prefix="!", intents=intents)

# Cog 로드 함수 (비동기적으로 수정)
async def load_cogs():
    try:
        await bot.load_extension("module.Basic_module")  # cogs -> module로 변경
        print("✅ BASIC MODULE 로드 성공")
    except Exception as e:
        print(f"⚠️ BASIC MODULE 로드 실패: {e}")

    try:
        await bot.load_extension("module.music_module")  # cogs -> module로 변경
        print("✅ MUSIC MODULE 로드 성공")
    except Exception as e:
        print(f"⚠️ MUSIC MODULE 로드 실패: {e}")

    try:
        await bot.load_extension("module.random_module")  # cogs -> module로 변경
        print("✅ RANDOM MODULE 로드 성공")
    except Exception as e:
        print(f"⚠️ RANDOM MODULE 로드 실패: {e}")

    try:
        await bot.load_extension("module.weather_module")  # cogs -> module로 변경
        print("✅ WEATHER MODULE 로드 성공")
    except Exception as e:
        print(f"⚠️ WEATHER MODULE 로드 실패: {e}")

    # try:
    #     await bot.load_extension("module.lunch_module")  # cogs -> module로 변경
    #     print("✅ LUNCH MODULE 로드 성공")
    # except Exception as e:
    #     print(f"⚠️ LUNCH MODULE 로드 실패: {e}")