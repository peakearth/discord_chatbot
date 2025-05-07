import discord
from discord.ext import commands
import yt_dlp

class MusicModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # 서버별 큐 저장
        self.loop_modes = {}  # {guild_id: "none"/"single"/"queue"}
        self.current_tracks = {}  # {guild_id: 현재 재생 곡 정보}
        
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.9"'
        }

    def get_queue(self, guild_id):
        """서버별 음악 큐 반환"""
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    async def connect_voice(self, ctx):
        """음성 채널 연결"""
        if not ctx.author.voice:
            raise commands.CommandError("❌ 먼저 음성 채널에 접속해주세요!")
        
        permissions = ctx.author.voice.channel.permissions_for(ctx.guild.me)
        if not permissions.connect or not permissions.speak:
            raise commands.CommandError("❌ 봇에게 '연결' 및 '말하기' 권한이 필요합니다!")
        
        return await ctx.author.voice.channel.connect()

    async def play_music(self, ctx, song_info):
        """음악 재생"""
        try:
            vc = ctx.voice_client or await self.connect_voice(ctx)

            # 현재 재생 곡 저장
            self.current_tracks[ctx.guild.id] = song_info  

            vc.play(
                discord.FFmpegPCMAudio(song_info['url'], **self.ffmpeg_options),
                after=lambda e: self.bot.loop.create_task(self.play_next(ctx.guild))
            )
            await ctx.send(f"🎵 **{song_info['title']}** 재생 시작!")

        except Exception as e:
            await ctx.send(f"❌ 재생 오류: {str(e)}")
            print(f"[DEBUG] Play Error: {e}")

    async def play_next(self, guild):
        """큐에서 다음 곡 재생"""
        guild_id = guild.id
        queue = self.get_queue(guild_id)
        loop_mode = self.loop_modes.get(guild_id, "none")

        if loop_mode == "single" and guild_id in self.current_tracks:
            # 현재 곡 다시 재생
            track = self.current_tracks[guild_id]
        elif queue:
            # 큐에서 다음 곡 가져오기
            track = queue.pop(0)
            self.current_tracks[guild_id] = track  
            if loop_mode == "queue":
                queue.append(track)  # 큐 반복 모드면 다시 추가
        else:
            # 큐가 비었으면 종료
            await self._cleanup(guild)
            return

        vc = guild.voice_client
        if vc and vc.is_connected():
            vc.play(
                discord.FFmpegPCMAudio(track['url'], **self.ffmpeg_options),
                after=lambda e: self.bot.loop.create_task(self.play_next(guild))
            )

    @commands.command(name="재생")
    @commands.guild_only()
    async def play(self, ctx, *, query):
        """음악 재생"""
        try:
            # 유튜브 정보 추출
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'default_search': 'ytsearch',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                
                song_info = {
                    'title': info.get('title', '알 수 없는 제목'),
                    'url': info['url']
                }

            # 바로 재생 or 큐에 추가
            vc = ctx.voice_client
            if vc and vc.is_playing():
                self.get_queue(ctx.guild.id).append(song_info)
                await ctx.send(f"🎶 **{song_info['title']}** 곡이 큐에 추가되었습니다!")
            else:
                await self.play_music(ctx, song_info)

        except Exception as e:
            await ctx.send(f"❌ 처리 중 오류 발생: {str(e)}")

    @commands.command(name="일시정지")
    @commands.guild_only()
    async def pause(self, ctx):
        """재생 일시정지"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ 재생을 일시정지했습니다.")
        else:
            await ctx.send("❌ 재생중인 음악이 없습니다")

    @commands.command(name="다시재생")
    @commands.guild_only()
    async def resume(self, ctx):
        """재생 재개"""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ 재생을 다시 시작합니다.")

    @commands.command(name="정지")
    @commands.guild_only()
    async def stop(self, ctx):
        """재생 정지 및 큐 초기화"""
        if ctx.voice_client:
            self.queues.pop(ctx.guild.id, None)
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ 재생을 정지했습니다.")

    @commands.command(name="스킵")
    @commands.guild_only()
    async def skip(self, ctx):
        """현재 곡 스킵"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏩ 현재 곡을 스킵합니다.")

    @commands.command(name="큐")
    @commands.guild_only()
    async def queue(self, ctx):
        """현재 재생 큐 확인"""
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return await ctx.send("❌ 현재 큐에 곡이 없습니다.")
        
        embed = discord.Embed(title="🎶 재생 큐", color=0x00ff00)
        for idx, song in enumerate(queue, 1):
            embed.add_field(name=f"{idx}. {song['title']}", value="\u200b", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="반복재생")
    async def loop(self, ctx, mode: str):
        """반복 재생 모드 설정 (none/single/queue)"""
        if mode not in ["none", "single", "queue"]:
            return await ctx.send("❌ 잘못된 반복 모드입니다! (가능한 값: none, single, queue)")

        self.loop_modes[ctx.guild.id] = mode
        await ctx.send(f"🔁 반복 재생 모드가 `{mode}`(으)로 설정되었습니다.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """봇이 강제로 음성 채널에서 추방되면 큐 초기화"""
        if member == self.bot.user and not after.channel:
            self.queues.pop(member.guild.id, None)

    async def _cleanup(self, guild):
        """음성 채널에서 나가고 큐 초기화"""
        if guild.voice_client:
            await guild.voice_client.disconnect()
        self.queues.pop(guild.id, None)
        self.current_tracks.pop(guild.id, None)

async def setup(bot):
    await bot.add_cog(MusicModule(bot))
