import discord
from discord.ext import commands, tasks
import youtube_dl

from random import choice


youtube_dl.utils.bug_reports_message=lambda:''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client=commands.Bot(command_prefix=";")
status=['stoned', 'sober']
response=['hey; //not the cliche hey', 'hello ji ki hal chal', 'Groovy killer here']

@client.event
async def on_ready():
    change_status.start()
    print('Bot is Online!')

@client.command(name='ping', help='returns latency')
async def ping(ctx):
    await ctx.send(f'latency:{round(client.latency*1000)}ms')

@client.command(name='hello', help='random welcome message')
async def hello(ctx):
    await ctx.send(choice(response))

@client.command(name='p', help='plays songs', )
async def p(ctx):
    if not ctx.message.author.voice:
        await ctx.send('You aren\'t connected to a voice channel')
        return
    else:
        channel=ctx.message.author.voice.channel
        
    await channel.connect()

    server=ctx.message.guild
    voice_channel=server.voice_client

    async with ctx.typing():
        player=await YTDLSource.from_url(url, client.loop)
        voice_channel.p(player, after=lambda e:print('error: %s' %e) if e else None)

    await ctx.send(f'**Now playing:**{player.title}')


@client.command(name='dc', help='disconnects')
async def dc(ctx):
    voice_client=ctx.message.guild.voice_client
    await voice_client.disconnect()

@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))




client.run('ODU0NTIyNzM1NTY4ODc5NjI2.YMlKUA.l1Q1EhbZtBjCIKr-iZ2iTwReHQ4')

