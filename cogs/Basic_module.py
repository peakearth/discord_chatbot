from discord.ext import commands
from datetime import datetime

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('✅ Module is Now Ready for service!')

    @commands.command(name="ping")
    async def _ping(self, ctx):
        await ctx.send("🏓 Pong!")

    @commands.command(name="이름")
    async def _이름(self, ctx):
        await ctx.send(f"명령어를 입력하신 분의 이름은 {ctx.author.name} 입니다.")

    @commands.command(name="날짜")
    async def _날짜(self, ctx):
        now = datetime.now()
        await ctx.send(f"📅 오늘은 {now.year}년 {now.month}월 {now.day}일 입니다.")
        
    @commands.command(name="시간")
    async def _시간(self, ctx):
        now = datetime.now()
        await ctx.send(f"⏰ 현재 시간은 {now.hour}시 {now.minute}분 {now.second}초 입니다.")

# 비동기적으로 Cog 추가
async def setup(bot):
    await bot.add_cog(Example(bot))  # await 사용
