import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # 음악 대기열
        self.currently_playing = None  # 현재 재생 중인 음악
        
    @commands.command(name="상태")
    async def status(self, ctx):
        vc = ctx.voice_client
        if vc is None:
            await ctx.send("❌ 봇이 음성 채널에 접속해 있지 않습니다.")
        else:
            await ctx.send(f"✅ 봇이 {vc.channel.name} 채널에 접속해 있습니다.")
    
    # 🎧 사용자가 음성 채널에 접속해야만 실행 가능
    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("🎧 먼저 음성 채널에 접속해주세요!")
            return False
        return True

    # 🎶 YouTube에서 음악 검색 후 오디오 URL 가져오기
    def search_youtube(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                result = ydl.extract_info(f"ytsearch:{query}", download=False)
                if 'entries' in result and result['entries']:
                    url = result['entries'][0]['url']
                    print(f"🎵 [디버그] 검색된 URL: {url}")  # ✅ 디버깅 메시지 추가
                    return url
                else:
                    print("❌ [디버그] YouTube 검색 결과 없음")
                    return None
            except Exception as e:
                print(f"❌ [디버그] YouTube 검색 오류: {e}")
                return None

    # 🎵 음악 재생 함수
    async def play_next(self, ctx):
        if self.queue:
            url = self.queue.pop(0)
            self.currently_playing = url

            ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
            'options': '-vn -loglevel panic',
            }

            vc = ctx.voice_client
            if vc is None:
                print("❌ [디버그] 봇이 음성 채널에 연결되지 않음")
                return

            vc.stop()
            print("🎧 [디버그] 음악 재생 시작!")  # ✅ 디버깅 메시지 추가
            vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
        else:
            self.currently_playing = None
            await ctx.voice_client.disconnect()

    # 🎼 !재생 [노래 제목]
    @commands.command(name="재생")
    async def play(self, ctx, *, query):
        if not await self.ensure_voice(ctx):
            return

        url = self.search_youtube(query)
        if url is None:
            await ctx.send(f"❌ `{query}` 검색 결과가 없습니다.")
            return

        if ctx.voice_client is None:
            vc = await ctx.author.voice.channel.connect()
        else:
            vc = ctx.voice_client

        self.queue.append(url)

        if self.currently_playing is None:
            await self.play_next(ctx)

        await ctx.send(f"🎵 `{query}`을(를) 재생합니다! ▶️")

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
            await ctx.send("▶️ 음악을 다시 재생합니다.")

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

# ✅ 봇에 Cog 등록
async def setup(bot):
    await bot.add_cog(Music(bot))
