from discord.ext import commands
import discord
import yt_dlp

class MusicModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # 음악 큐

    # 음악 재생
    @commands.command(name="재생")
    async def play(self, ctx, *, url):
        try:
            # 음성 채널 연결
            vc = ctx.voice_client

            # 봇이 음성 채널에 없으면 자동 연결
            if not vc:
                if ctx.author.voice:
                    vc = await ctx.author.voice.channel.connect()
                else:
                    await ctx.send("❌ 먼저 음성 채널에 접속해주세요!")
                    return
            
            # YouTube 링크에서 오디오 URL 추출
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'extractaudio': True,
                'noplaylist': True,
                'default_search': 'ytsearch',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    info = info['entries'][0]  # 첫 번째 검색 결과 사용
                url2 = info['url']
                title = info['title']

            # FFmpeg로 음악 재생
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel quiet',
                'options': '-vn -filter:a "volume=0.9,aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo"',
            }
            vc.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options))
            await ctx.send(f"🎵 `{title}`을(를) 재생합니다!")
        
        except Exception as e:
            await ctx.send(f"❌ 음악을 재생할 수 없습니다: {str(e)}")
            print(f"❌ [디버그] 오류 발생: {e}")

    # ⏸️ !일시정지
    @commands.command(name="일시정지")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ 음악을 일시 정지했습니다.")

    # ▶️ !다시재생
    @commands.command(name="다시재생")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ 음악을 다시 재생합니다 :) ")

    # ⏹️ !정지
    @commands.command(name="정지")
    async def stop(self, ctx):
        if ctx.voice_client:
            self.queue.clear()
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ 음악을 정지하고 음성 채널에서 나갑니다.")

    # ⏭️ !스킵
    @commands.command(name="스킵")
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await self.play_next(ctx)
            await ctx.send("⏩ 다음 음악을 재생합니다.")

    # !볼륨 [0~100]
    @commands.command(name="볼륨")
    async def set_volume(self, ctx, volume: int):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send("❌ 현재 재생 중인 음악이 없습니다.")
        
        ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 볼륨을 {volume}%로 설정했습니다!")

    # !핑 (네트워크 상태 확인)
    @commands.command(name="핑")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)  # 밀리초 변환
        await ctx.send(f"🏓 현재 핑: {latency}ms")

    # !나가 (봇 음성 채널에서 나가기)
    @commands.command(name="나가")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 봇이 음성 채널에서 나갔습니다!")
        else:
            await ctx.send("❌ 봇이 현재 음성 채널에 없습니다.")

    async def play_next(self, ctx):
        # 음악 큐에서 다음 음악을 재생하는 기능을 추가할 수 있음
        pass

# Cog 로드
async def setup(bot):
    await bot.add_cog(MusicModule(bot))
