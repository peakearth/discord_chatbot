import discord
from discord.ext import commands
import yt_dlp

class MusicModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="재생")
    async def play_music(self, ctx, *, query):
        try:
            # 음성 채널 연결
            if not ctx.voice_client:
                if ctx.author.voice:
                    vc = await ctx.author.voice.channel.connect()
                else:
                    await ctx.send("❌ 먼저 음성 채널에 접속해주세요!")
                    return
            else:
                vc = ctx.voice_client

            # 유튜브에서 음악을 검색하여 URL 추출
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'extractaudio': True,
                'noplaylist': True,
                'default_search': 'ytsearch'
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]  # 첫 번째 검색 결과 사용
                url2 = info['url']
                title = info['title']

            # FFmpeg로 음악 재생
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel quiet',
                'options': '-vn -filter:a "volume=0.9,aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo"'
            }

            vc.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options))
            await ctx.send(f"🎵 `{title}`을(를) 재생합니다! ▶️")
        except Exception as e:
            await ctx.send(f"❌ 음악을 재생할 수 없습니다: {str(e)}")
            print(f"❌ 오류 발생: {e}")

    @commands.command(name="나가")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 봇이 음성 채널에서 나갔습니다!")
        else:
            await ctx.send("❌ 봇이 현재 음성 채널에 없습니다.")

# Cog를 봇에 추가하는 함수
async def setup(bot):
    await bot.add_cog(MusicModule(bot))

