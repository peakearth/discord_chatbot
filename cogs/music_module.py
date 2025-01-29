import discord
from discord.ext import commands
import yt_dlp

class MusicModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def play_music(self, ctx, url):
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

            # play()는 비동기 함수가 아니므로 await을 사용할 필요가 없음
            vc.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options), after=lambda e: print('음악 재생 종료됨', e))

            await ctx.send(f"🎵 `{title}`을(를) 재생합니다! ▶️")

        except Exception as e:
            await ctx.send(f"❌ 음악을 재생할 수 없습니다: {str(e)}")
            print(f"❌ [디버그] 오류 발생: {e}")

    @commands.command(name="재생")
    async def play(self, ctx, *, query):
        await self.play_music(ctx, query)

    @commands.command(name="볼륨")
    async def set_volume(self, ctx, volume: int):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send("❌ 현재 재생 중인 음악이 없습니다.")
        
        ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 볼륨을 {volume}%로 설정했습니다!")

    @commands.command(name="핑")
    async def ping(self, ctx):
        latency = round(ctx.bot.latency * 1000)  # 밀리초 변환
        await ctx.send(f"🏓 현재 핑: {latency}ms")

    @commands.command(name="나가")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 봇이 음성 채널에서 나갔습니다!")
        else:
            await ctx.send("❌ 봇이 현재 음성 채널에 없습니다.")

# Cog 로드 함수
async def setup(bot):
    await bot.add_cog(MusicModule(bot))  # MusicModule을 봇에 추가
