from discord.ext import commands
import json
import random
import discord
import sqlite3
import os
from pathlib import Path

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
        for i in range(1):
            lotto_num = random.sample(range(1,46), 6)
            lotto_num.sort()
            await ctx.send(f'오늘의 로또 번호 추천은 {lotto_num} 입니다.')
            

async def setup(bot):
    await bot.add_cog(Random(bot))