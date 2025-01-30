from discord.ext import commands
import random

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('✅ Module is Now Ready for service!')
    
    @commands.command(name = "랜덤")
    async def _랜덤(self, ctx):
        num = random.randint(1,64)
        await ctx.send(f'오늘의 행운의 숫자는 {num} 입니다.')
        
    @commands.command(name = "복권")
    async def _복권(self, ctx):
        pass
    
    @commands.command(name  = "밥추천")
    async def _밥추천(self, ctx):
        food = list('한식', '양식', '중식', '일식', '굶어')
        rand_food = random.random(food)
        await ctx.send(f'오늘의 추천은 {rand_food} 입니다!')
    
    # @commands.command(name = "")
    
    
async def setup(bot):
    await bot.add_cog(Random(bot))