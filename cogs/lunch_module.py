import discord
from discord.ext import commands
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import aiohttp
import asyncio
import json
import random

class LunchModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = Path(__file__).parent.parent / 'data' / 'lunch_menu.db'
        self._init_database()
        self.cafeteria_update_task = self.bot.loop.create_task(self.update_cafeteria_menu_daily())

    def _init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        if not self.db_path.parent.exists():
            os.makedirs(self.db_path.parent)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SQL 파일에서 초기 설정 스크립트 읽기
        sql_file_path = self.db_path.parent / 'lunch_menu.sql'
        if sql_file_path.exists():
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
        
        conn.commit()
        conn.close()

    async def update_cafeteria_menu_daily(self):
        """매일 학식 메뉴 업데이트"""
        while True:
            try:
                now = datetime.now()
                # 매일 자정에 실행
                next_run = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
                await asyncio.sleep((next_run - now).seconds)
                
                # 학식 메뉴 업데이트
                await self.fetch_cafeteria_menu()
            except Exception as e:
                print(f"학식 메뉴 업데이트 중 오류 발생: {e}")
                await asyncio.sleep(3600)  # 오류 발생시 1시간 후 재시도

    async def fetch_cafeteria_menu(self):
        """동아대학교 학식 메뉴 가져오기"""
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"https://www.donga.ac.kr/kor/CMS/DietMenuMgr/list.do?mCode=MN199&searchDay={today}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        
                        # 오늘 날짜의 기존 메뉴 삭제
                        cursor.execute("DELETE FROM cafeteria_menu WHERE menu_date = ?", (today,))
                        
                        # 새로운 메뉴 추가
                        for menu in data['menus']:
                            cursor.execute("""
                                INSERT INTO cafeteria_menu (location, menu_type, menu_name, price, menu_date)
                                VALUES (?, ?, ?, ?, ?)
                            """, (menu['location'], menu['type'], menu['name'], menu['price'], today))
                        
                        conn.commit()
                        conn.close()
        except Exception as e:
            print(f"학식 메뉴 가져오기 실패: {e}")

    @commands.command(name='점심추천')
    async def recommend_lunch(self, ctx, category: str = None):
        """사용자 선호도를 고려한 점심 메뉴 추천"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 사용자의 선호도가 높은 메뉴 가중치 부여
        if category:
            cursor.execute("""
                SELECT m.id, m.menu_name, m.category, 
                       COALESCE(AVG(up.rating), 0) as avg_rating,
                       r.name as restaurant_name,
                       r.location as restaurant_location
                FROM lunch_menu m
                LEFT JOIN user_preferences up ON m.id = up.menu_id
                LEFT JOIN restaurants r ON r.category = m.category
                WHERE m.category = ?
                GROUP BY m.id
                ORDER BY avg_rating DESC, RANDOM()
                LIMIT 3
            """, (category,))
        else:
            cursor.execute("""
                SELECT m.id, m.menu_name, m.category,
                       COALESCE(AVG(up.rating), 0) as avg_rating,
                       r.name as restaurant_name,
                       r.location as restaurant_location
                FROM lunch_menu m
                LEFT JOIN user_preferences up ON m.id = up.menu_id
                LEFT JOIN restaurants r ON r.category = m.category
                GROUP BY m.id
                ORDER BY avg_rating DESC, RANDOM()
                LIMIT 3
            """)
        
        results = cursor.fetchall()
        
        if results:
            embed = discord.Embed(
                title="🍱 오늘의 점심 메뉴 추천",
                description="당신의 선호도를 반영한 추천 메뉴입니다!",
                color=discord.Color.green()
            )
            
            for menu_id, menu_name, category, avg_rating, rest_name, rest_location in results:
                value = f"카테고리: {category}\n"
                if rest_name:
                    value += f"추천 식당: {rest_name}\n"
                if rest_location:
                    value += f"위치: {rest_location}\n"
                if avg_rating > 0:
                    value += f"평균 평점: {'⭐' * int(avg_rating)}"
                
                embed.add_field(
                    name=menu_name,
                    value=value,
                    inline=False
                )
            
            # 반응 추가를 위한 메시지 전송
            msg = await ctx.send(embed=embed)
            
            # 평가를 위한 반응 추가
            reactions = ['1️⃣', '2️⃣', '3️⃣']
            for reaction in reactions:
                await msg.add_reaction(reaction)
            
            # 메시지 ID와 메뉴 ID 저장
            self.last_recommendation = {
                'message_id': msg.id,
                'menus': [(menu_id, menu_name) for menu_id, *_ in results]
            }
        else:
            await ctx.send("추천할 메뉴가 없습니다. 데이터베이스를 확인해주세요.")
        
        conn.close()

    @commands.command(name='메뉴목록')
    async def list_menus(self, ctx, category: str = None):
        """저장된 메뉴 목록을 보여줍니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT m.menu_name, m.category, r.name as restaurant_name
                FROM lunch_menu m
                LEFT JOIN restaurants r ON r.category = m.category
                WHERE m.category = ?
                ORDER BY m.menu_name
            """, (category,))
        else:
            cursor.execute("""
                SELECT m.menu_name, m.category, r.name as restaurant_name
                FROM lunch_menu m
                LEFT JOIN restaurants r ON r.category = m.category
                ORDER BY m.category, m.menu_name
            """)
        
        results = cursor.fetchall()
        
        if results:
            embed = discord.Embed(
                title="📋 저장된 메뉴 목록",
                color=discord.Color.blue()
            )
            
            # 카테고리별로 메뉴 정리
            menu_by_category = {}
            for menu_name, cat, rest_name in results:
                if cat not in menu_by_category:
                    menu_by_category[cat] = []
                menu_info = menu_name
                if rest_name:
                    menu_info += f" ({rest_name})"
                menu_by_category[cat].append(menu_info)
            
            # 카테고리별로 필드 추가
            for cat, menus in menu_by_category.items():
                embed.add_field(
                    name=f"[{cat}]",
                    value="\n".join(menus),
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("저장된 메뉴가 없습니다.")
        
        conn.close()

    @commands.command(name='학식메뉴')
    async def show_cafeteria_menu(self, ctx, location: str = None):
        """오늘의 학식 메뉴를 보여줍니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if location:
            cursor.execute("""
                SELECT location, menu_type, menu_name, price
                FROM cafeteria_menu
                WHERE menu_date = ? AND location LIKE ?
                ORDER BY menu_type
            """, (today, f"%{location}%"))
        else:
            cursor.execute("""
                SELECT location, menu_type, menu_name, price
                FROM cafeteria_menu
                WHERE menu_date = ?
                ORDER BY location, menu_type
            """, (today,))
        
        results = cursor.fetchall()
        
        if results:
            embed = discord.Embed(
                title=f"🏫 {today} 학식 메뉴",
                color=discord.Color.gold()
            )
            
            # 식당별로 메뉴 정리
            menu_by_location = {}
            for loc, menu_type, menu_name, price in results:
                if loc not in menu_by_location:
                    menu_by_location[loc] = []
                price_str = f"{price:,}원" if price else "가격 정보 없음"
                menu_by_location[loc].append(f"- {menu_type}: {menu_name} ({price_str})")
            
            # 식당별로 필드 추가
            for loc, menus in menu_by_location.items():
                embed.add_field(
                    name=loc,
                    value="\n".join(menus),
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("오늘의 학식 메뉴 정보가 없습니다.")
        
        conn.close()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """메뉴 추천에 대한 사용자 평가 처리"""
        if user.bot:
            return
            
        if not hasattr(self, 'last_recommendation'):
            return
            
        if reaction.message.id != self.last_recommendation['message_id']:
            return
            
        # 반응에 따른 메뉴 인덱스
        reactions = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2}
        if reaction.emoji not in reactions:
            return
            
        menu_idx = reactions[reaction.emoji]
        if menu_idx >= len(self.last_recommendation['menus']):
            return
            
        menu_id, menu_name = self.last_recommendation['menus'][menu_idx]
        
        # 사용자 평가 저장
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_preferences (user_id, menu_id, rating)
            VALUES (?, ?, 5)
            ON CONFLICT (user_id, menu_id) DO UPDATE SET rating = 5
        """, (str(user.id), menu_id))
        
        conn.commit()
        conn.close()
        
        await reaction.message.channel.send(
            f"{user.mention}님이 '{menu_name}' 메뉴를 선호하는 것으로 기록했습니다! 👍"
        )

async def setup(bot):
    await bot.add_cog(LunchModule(bot))