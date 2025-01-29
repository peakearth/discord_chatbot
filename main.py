import discord
from discord.ext import commands
import os

def main():
    prefix = '!'
    intents = discord.Intents.all()  # 봇이 멤버의 정보, 리스트를 불러 옴
    
    # command_prefix = 접두사의 의미 (!를 등록하는데 더 초점을 둔다)
    client = commands.Bot(command_prefix=prefix, intents=intents)
    
    # 토큰 읽어오기
    with open('discord_chatbot/token.txt', 'r') as f:
        token = f.read()
        
    # 생성된 Bot 객체에 토큰을 넣어서 생성
    client.run(token)
    
if __name__ == '__main__':
    main()


