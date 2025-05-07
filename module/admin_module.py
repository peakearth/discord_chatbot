import discord
from discord.ext import commands
import asyncio
import json
import os

class AdminModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 권한 레벨 설정 (0: 일반 사용자, 1: 모더레이터, 2: 관리자, 3: 소유자)
        self.permission_levels = {
            0: "일반 사용자",
            1: "모더레이터",
            2: "관리자",
            3: "소유자"
        }
        # 권한 데이터 파일 경로
        self.permissions_file = "data/permissions.json"
        # 권한 데이터 로드
        self.permissions = self.load_permissions()

    def load_permissions(self):
        """권한 데이터를 파일에서 로드"""
        if not os.path.exists("data"):
            os.makedirs("data")
        
        if os.path.exists(self.permissions_file):
            try:
                with open(self.permissions_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"권한 파일 로드 오류: {e}")
                return {}
        else:
            return {}

    def save_permissions(self):
        """권한 데이터를 파일에 저장"""
        with open(self.permissions_file, "w", encoding="utf-8") as f:
            json.dump(self.permissions, f, ensure_ascii=False, indent=4)

    def has_permission_level(self, user_id, required_level):
        """사용자의 권한 레벨이 요구 레벨 이상인지 확인"""
        user_id = str(user_id)  # JSON 키는 문자열이어야 함
        if user_id not in self.permissions:
            return False
        return self.permissions[user_id] >= required_level

    @commands.command(name="청소", aliases=["삭제", "clear", "purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 5):
        """
        지정된 수의 메시지를 삭제합니다.
        사용법: !청소 [개수=5]
        """
        if amount <= 0:
            await ctx.send("1개 이상의 메시지를 지정해주세요!")
            return
        elif amount > 100:
            await ctx.send("한 번에 최대 100개까지만 삭제할 수 있습니다.")
            return
        
        # 메시지 삭제 전 확인 메시지 전송
        confirmation_msg = await ctx.send(f"{amount}개의 메시지를 삭제하시겠습니까? 확인하려면 👍 반응을 추가하세요. (10초 후 자동 취소)")
        await confirmation_msg.add_reaction("👍")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "👍" and reaction.message.id == confirmation_msg.id
        
        try:
            # 10초 동안 반응을 기다림
            await self.bot.wait_for("reaction_add", timeout=10.0, check=check)
            
            # 확인 메시지와 명령어 메시지 삭제
            await confirmation_msg.delete()
            
            # 지정된 수의 메시지 삭제
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1은 명령어 메시지 포함
            
            # 삭제 완료 메시지 전송 후 3초 후 자동 삭제
            result_msg = await ctx.send(f"✅ {len(deleted) - 1}개의 메시지가 삭제되었습니다.")
            await asyncio.sleep(3)
            await result_msg.delete()
            
        except asyncio.TimeoutError:
            # 시간 초과 시 취소 메시지 전송 후 자동 삭제
            await confirmation_msg.delete()
            cancel_msg = await ctx.send("⚠️ 시간이 초과되어 메시지 삭제가 취소되었습니다.")
            await asyncio.sleep(3)
            await cancel_msg.delete()
    
    @clear_messages.error
    async def clear_messages_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ 이 명령어를 사용하려면 '메시지 관리' 권한이 필요합니다.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ 올바른 숫자를 입력해주세요.")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")
    
    @commands.command(name="대량삭제", aliases=["mass_delete"])
    @commands.has_permissions(administrator=True)
    async def mass_delete(self, ctx, amount: int):
        """
        관리자용 대량 메시지 삭제 명령어. 최대 1000개까지 삭제 가능
        사용법: !대량삭제 [개수]
        """
        if amount <= 0:
            await ctx.send("1개 이상의 메시지를 지정해주세요!")
            return
        elif amount > 1000:
            await ctx.send("한 번에 최대 1000개까지만 삭제할 수 있습니다.")
            return
        
        warning_msg = await ctx.send(f"⚠️ 주의: {amount}개의 메시지를 삭제합니다. 정말로 진행하시겠습니까? 확인하려면 `확인`을 입력하세요. (30초 후 자동 취소)")
        
        def check(m):
            return m.author == ctx.author and m.content == "확인" and m.channel == ctx.channel
        
        try:
            # 30초 동안 '확인' 메시지를 기다림
            await self.bot.wait_for("message", timeout=30.0, check=check)
            
            await warning_msg.delete()
            progress_msg = await ctx.send(f"⏳ {amount}개의 메시지 삭제 중...")
            
            # 대량 삭제 (100개씩 나눠서 삭제)
            deleted_count = 0
            while deleted_count < amount:
                delete_amount = min(100, amount - deleted_count)
                deleted = await ctx.channel.purge(limit=delete_amount + (1 if deleted_count == 0 else 0))
                deleted_count += len(deleted)
                
                # 중간 진행상황 업데이트 (200개마다)
                if deleted_count % 200 == 0 and deleted_count < amount:
                    await progress_msg.edit(content=f"⏳ {deleted_count}/{amount}개 메시지 삭제 중...")
            
            # 명령어 메시지와 '확인' 메시지가 포함될 수 있으므로 조정
            actual_deleted = min(deleted_count, amount)
            
            # 완료 메시지 전송 후 5초 후 자동 삭제
            await progress_msg.delete()
            complete_msg = await ctx.send(f"✅ 총 {actual_deleted}개의 메시지가 삭제되었습니다.")
            await asyncio.sleep(5)
            await complete_msg.delete()
            
        except asyncio.TimeoutError:
            await warning_msg.delete()
            cancel_msg = await ctx.send("⚠️ 시간이 초과되어 메시지 삭제가 취소되었습니다.")
            await asyncio.sleep(3)
            await cancel_msg.delete()
    
    @mass_delete.error
    async def mass_delete_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ 이 명령어를 사용하려면 '관리자' 권한이 필요합니다.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ 올바른 숫자를 입력해주세요.")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")

    # ---------- 역할 관리 명령어 ----------
    
    @commands.command(name="역할부여", aliases=["role_add", "addrole"])
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, member: discord.Member, *, role_name: str):
        """
        특정 사용자에게 역할을 부여합니다.
        사용법: !역할부여 @사용자 역할이름
        """
        # 역할 찾기
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"⚠️ '{role_name}' 역할을 찾을 수 없습니다.")
            return
        
        # 역할 부여 권한 확인
        if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            await ctx.send("⚠️ 자신보다 높은 또는 같은 위치의 역할은 부여할 수 없습니다.")
            return
        
        # 이미 역할을 가지고 있는지 확인
        if role in member.roles:
            await ctx.send(f"⚠️ {member.mention}님은 이미 '{role.name}' 역할을 가지고 있습니다.")
            return
        
        # 역할 부여
        try:
            await member.add_roles(role)
            await ctx.send(f"✅ {member.mention}님에게 '{role.name}' 역할을 부여했습니다.")
        except discord.Forbidden:
            await ctx.send("⚠️ 권한이 부족하여 역할을 부여할 수 없습니다.")
        except discord.HTTPException as e:
            await ctx.send(f"⚠️ 역할 부여 중 오류가 발생했습니다: {e}")
    
    @add_role.error
    async def add_role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ 이 명령어를 사용하려면 '역할 관리' 권한이 필요합니다.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("⚠️ 지정한 사용자를 찾을 수 없습니다.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ 올바른 형식: !역할부여 @사용자 역할이름")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")
    
    @commands.command(name="역할제거", aliases=["role_remove", "removerole"])
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member, *, role_name: str):
        """
        특정 사용자의 역할을 제거합니다.
        사용법: !역할제거 @사용자 역할이름
        """
        # 역할 찾기
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"⚠️ '{role_name}' 역할을 찾을 수 없습니다.")
            return
        
        # 역할 제거 권한 확인
        if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            await ctx.send("⚠️ 자신보다 높은 또는 같은 위치의 역할은 제거할 수 없습니다.")
            return
        
        # 해당 역할을 가지고 있는지 확인
        if role not in member.roles:
            await ctx.send(f"⚠️ {member.mention}님은 '{role.name}' 역할을 가지고 있지 않습니다.")
            return
        
        # 역할 제거
        try:
            await member.remove_roles(role)
            await ctx.send(f"✅ {member.mention}님의 '{role.name}' 역할을 제거했습니다.")
        except discord.Forbidden:
            await ctx.send("⚠️ 권한이 부족하여 역할을 제거할 수 없습니다.")
        except discord.HTTPException as e:
            await ctx.send(f"⚠️ 역할 제거 중 오류가 발생했습니다: {e}")
    
    @remove_role.error
    async def remove_role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ 이 명령어를 사용하려면 '역할 관리' 권한이 필요합니다.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("⚠️ 지정한 사용자를 찾을 수 없습니다.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ 올바른 형식: !역할제거 @사용자 역할이름")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")
    
    @commands.command(name="역할목록", aliases=["roles", "listroles"])
    async def list_roles(self, ctx, member: discord.Member = None):
        """
        서버의 모든 역할 또는 특정 사용자의 역할을 표시합니다.
        사용법: !역할목록 [@사용자]
        """
        if member:
            # 특정 사용자의 역할 목록
            if len(member.roles) == 1:  # @everyone 역할만 있는 경우
                embed = discord.Embed(
                    title=f"{member.display_name}님의 역할",
                    description="역할이 없습니다.",
                    color=discord.Color.blue()
                )
            else:
                # @everyone 역할을 제외하고 역할 목록 구성 (역할 위치 내림차순)
                roles = [role.mention for role in sorted(member.roles[1:], key=lambda x: x.position, reverse=True)]
                embed = discord.Embed(
                    title=f"{member.display_name}님의 역할 ({len(roles)}개)",
                    description=" ".join(roles),
                    color=discord.Color.blue()
                )
        else:
            # 서버의 모든 역할 목록
            roles = [role.mention for role in sorted(ctx.guild.roles, key=lambda x: x.position, reverse=True) if role.name != "@everyone"]
            embed = discord.Embed(
                title=f"{ctx.guild.name} 서버의 역할 ({len(roles)}개)",
                description=" ".join(roles),
                color=discord.Color.blue()
            )
        
        await ctx.send(embed=embed)
    
    @list_roles.error
    async def list_roles_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("⚠️ 지정한 사용자를 찾을 수 없습니다.")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")
    
    # ---------- 내부 권한 관리 명령어 ----------
    
    @commands.command(name="권한설정", aliases=["setperm", "set_permission"])
    @commands.has_permissions(administrator=True)
    async def set_permission(self, ctx, member: discord.Member, level: int):
        """
        사용자의 봇 내부 권한 레벨을 설정합니다.
        레벨: 0(일반 사용자), 1(모더레이터), 2(관리자), 3(소유자)
        사용법: !권한설정 @사용자 권한레벨
        """
        # 권한 레벨 범위 확인
        if level < 0 or level > 3:
            await ctx.send("⚠️ 권한 레벨은 0에서 3 사이의 값이어야 합니다.")
            return
        
        # 자신보다 높은 권한 설정 방지
        author_id = str(ctx.author.id)
        author_level = self.permissions.get(author_id, 0)
        if level >= author_level and ctx.guild.owner_id != ctx.author.id:
            await ctx.send("⚠️ 자신과 같거나 더 높은 권한 레벨은 설정할 수 없습니다.")
            return
        
        # 권한 설정
        self.permissions[str(member.id)] = level
        self.save_permissions()
        
        await ctx.send(f"✅ {member.mention}님의 권한 레벨을 {level}({self.permission_levels[level]})로 설정했습니다.")
    
    @set_permission.error
    async def set_permission_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ 이 명령어를 사용하려면 '관리자' 권한이 필요합니다.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("⚠️ 지정한 사용자를 찾을 수 없습니다.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ 올바른 형식: !권한설정 @사용자 권한레벨(0-3)")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ 올바른 형식: !권한설정 @사용자 권한레벨(0-3)")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")
    
    @commands.command(name="권한확인", aliases=["checkperm", "check_permission"])
    async def check_permission(self, ctx, member: discord.Member = None):
        """
        사용자의 현재 봇 내부 권한 레벨을 확인합니다.
        사용법: !권한확인 [@사용자]
        """
        # 대상 설정 (입력이 없으면 명령어 실행자)
        target = member if member else ctx.author
        
        # 권한 레벨 확인
        user_id = str(target.id)
        level = self.permissions.get(user_id, 0)
        
        # 응답 전송
        await ctx.send(f"🔍 {target.mention}님의 권한 레벨: {level}({self.permission_levels[level]})")
    
    @check_permission.error
    async def check_permission_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("⚠️ 지정한 사용자를 찾을 수 없습니다.")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")
    
    @commands.command(name="권한목록", aliases=["listperms", "list_permissions"])
    @commands.has_permissions(administrator=True)
    async def list_permissions(self, ctx):
        """
        모든 특별 권한을 가진 사용자의 목록을 표시합니다.
        사용법: !권한목록
        """
        # 권한 목록이 비어있는 경우
        if not self.permissions:
            await ctx.send("📝 특별 권한을 가진 사용자가 없습니다.")
            return
        
        # 권한 레벨별로 사용자 분류
        level_users = {0: [], 1: [], 2: [], 3: []}
        
        for user_id, level in self.permissions.items():
            if level > 0:  # 일반 사용자(0)는 표시하지 않음
                # 사용자 객체 가져오기 시도
                user = self.bot.get_user(int(user_id))
                name = user.mention if user else f"ID: {user_id}"
                level_users[level].append(name)
        
        # 임베드 생성
        embed = discord.Embed(
            title="🔑 권한 목록",
            description="봇 내부 권한을 가진 사용자 목록입니다.",
            color=discord.Color.gold()
        )
        
        # 레벨별 사용자 추가
        for level, users in level_users.items():
            if level > 0 and users:  # 레벨 0은 표시하지 않음
                embed.add_field(
                    name=f"레벨 {level} ({self.permission_levels[level]})",
                    value=", ".join(users) if users else "없음",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @list_permissions.error
    async def list_permissions_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ 이 명령어를 사용하려면 '관리자' 권한이 필요합니다.")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")
    
    # 권한 레벨 확인 커스텀 체크 함수
    def is_permission_level(level):
        async def predicate(ctx):
            # self에 접근하기 위한 방법
            cog = ctx.bot.get_cog("AdminModule")
            if not cog:
                return False
            return cog.has_permission_level(ctx.author.id, level)
        return commands.check(predicate)
    
    @commands.command(name="모더레이터명령", aliases=["mod_command"])
    @is_permission_level(1)  # 모더레이터 이상만 사용 가능
    async def moderator_command(self, ctx):
        """모더레이터 이상만 사용할 수 있는 명령어 예시"""
        await ctx.send("👮 이 명령어는 모더레이터 이상만 사용할 수 있습니다!")
    
    @moderator_command.error
    async def moderator_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("⚠️ 이 명령어를 사용하려면 모더레이터 이상의 권한이 필요합니다.")
        else:
            await ctx.send(f"⚠️ 오류가 발생했습니다: {error}")

async def setup(bot):
    await bot.add_cog(AdminModule(bot))