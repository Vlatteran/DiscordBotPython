from discord.ext.commands import Bot
import discord
from config import settings
from collections import deque
from youtube_dl import YoutubeDL
from asyncio import sleep


class MyBot(Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.voice_client = None
        self.music_queue = deque()

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def play(self, music, message):
        ydl_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        if self.voice_client is None:
            channel = message.author.voice
            if channel is not None:
                self.voice_client = await channel.channel.connect(timeout=60, reconnect=True)
            else:
                await message.reply('You must be connected to voice channel to play music')
        elif self.voice_client.channel != message.author.voice.channel:
            await message.reply('already connected to other channel')
            return
        elif self.voice_client.is_playing():
            await message.reply('already playing something')
            return
        with YoutubeDL(ydl_options) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{music}", download=False)['entries'][0]
            except:
                info = ydl.extract_info(music, download=False)

        url = info['formats'][0]['url']
        print(url)

        self.voice_client.play(discord.FFmpegPCMAudio(source=url, **ffmpeg_options))

        while self.voice_client.is_playing():
            await sleep(3)
        if not self.voice_client.is_paused():
            try:
                params = self.music_queue.popleft()
                await self.play(params['music'], params['message'])
            except IndexError:
                await self.voice_client.disconnect()
            self.voice_client = None

    async def add_to_queue(self, music, message):
        try:
            if self.voice_client.is_playing():
                self.music_queue.append({'music': music, 'message': message})
            else:
                await message.reply("Nothing is playing, use command !play")
        except Exception as e:
            print(e)
            await message.reply("Nothing is playing, use command !play")

    async def on_message(self, message: discord.Message):
        print(f'{message.author} in {message.guild}.{message.channel}: {message.content}')
        if message.author == self.user:
            return

        command = message.content.split(' ')[0]
        command_text = ' '.join(message.content.split(' ')[1:])
        print(f'command: {command}, params: {command_text}')
        if command == '!hello':
            await message.reply(f'Hello, {message.author.name}!')
        elif command == '!play':
            await self.play(command_text, message)
        elif command == '!playnext':
            await self.add_to_queue(command_text, message)
        elif command == '!next':
            await self.next(message)

    async def next(self, message):
        try:
            if self.voice_client.is_playing():
                self.voice_client.stop()
            else:
                await message.reply("Nothing is playing, can't execute command !next")
        except Exception as e:
            print(e)
            await message.reply("Nothing is playing, can't execute command !next")


if __name__ == '__main__':
    bot = MyBot(command_prefix=settings['prefix'])
    bot.run(settings['token'])
