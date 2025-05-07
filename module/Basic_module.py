from discord.ext import commands
from datetime import datetime

class Basic(commands.Cog):
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
        
    @commands.command(name="이동훈")
    async def _이동훈(self, ctx):
        today = datetime.today().date()

        target_dates = {
            "필승! 이동훈의 군복무 시작일": datetime(2025, 8, 19).date(),
            "필승! 이동훈의 민간인 복귀일": datetime(2027, 2, 18).date()
        }

        response = "📆 남은 날짜 계산 결과:\n"
        for name, target_date in target_dates.items():
            remaining_days = (target_date - today).days
            response += f"{name}까지 {remaining_days}일 남았습니다.\n"

        await ctx.send(response)
    
    @commands.command(name="김도훈")
    async def _김도훈(self, ctx):
        today = datetime.today().date()

        target_dates = {
            "필승! 김도훈의 민간인 복귀일": datetime(2027, 2, 18).date()
        }

        response = "📆 남은 날짜 계산 결과:\n"
        for name, target_date in target_dates.items():
            remaining_days = (target_date - today).days
            response += f"{name}까지 {remaining_days}일 남았습니다.\n"

        await ctx.send(response)
        
# 비동기적으로 Cog 추가
async def setup(bot):
    await bot.add_cog(Basic(bot))  # await 사용
