import discord
from discord.ext import commands

# 봇 객체 생성
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용을 읽을 수 있는 권한 추가
bot = commands.Bot(command_prefix="!", intents=intents)

# Cog 로드 함수 (비동기적으로 수정)
async def load_cogs():
    try:
        await bot.load_extension("cogs.Basic_module")  # example.py 파일 로드
        print("✅ basic_module.py 로드 성공")
    except Exception as e:
        print(f"⚠️ Cog 로드 실패: {e}")

    try:
        await bot.load_extension("cogs.music_module")  # music_module.py 파일 로드
        print("✅ music_module.py 로드 성공")
    except Exception as e:
        print(f"⚠️ Cog 로드 실패: {e}")

    try:
        await bot.load_extension("cogs.random_module")  # random_module.py 파일 로드
        print("✅ random_module.py 로드 성공")
    except Exception as e:
        print(f"⚠️ Cog 로드 실패: {e}")

# 봇 준비 완료 이벤트
@bot.event
async def on_ready():
    print(f"✅ 봇이 로그인되었습니다: {bot.user}")
    await load_cogs()  # 비동기적으로 Cog 로드

# 봇 실행
def main():
    with open('discord_chatbot/token.txt', 'r') as f:
        token = f.read().strip()  # 토큰 파일에서 읽어옴
    bot.run(token)  # 봇 실행

if __name__ == "__main__":
    main()
