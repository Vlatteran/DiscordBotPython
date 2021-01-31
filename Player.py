import discord
from youtube_dl import YoutubeDL
from asyncio import sleep


def search(query):
    ydl_options = {'format': 'bestaudio',
                   'noplaylist': 'True',
                   'quiet': True}
    with YoutubeDL(ydl_options) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        except:
            info = ydl.extract_info(query, download=False)

    return info


class Player:
    voice_client: discord.voice_client
    player_message: discord.Message

    def __init__(self):
        self.is_paused = False
        self.is_previous = False
        self.is_next = False
        self.music_list = []
        self.voice_client = None
        self.player_message = None
        self.current = 0
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

    async def connect(self, channel: discord.guild.VoiceChannel):
        self.voice_client = await channel.connect(timeout=60, reconnect=True)

    async def disconnect(self):
        await self.voice_client.disconnect()
        self.voice_client = None

    async def play(self, message):
        while self.current <= len(self.music_list) - 1:
            print(f'[Player.play()] current = {self.current}')
            info = self.music_list[self.current]

            url = info['formats'][0]['url']

            if self.player_message is None:
                self.player_message = await message.reply(f'Now playing: {info["title"]}')
                try:
                    await self.player_message.pin()
                except discord.errors.Forbidden:
                    print("can't pin")
            else:
                try:
                    await self.player_message.clear_reactions()
                except discord.errors.Forbidden:
                    print("can't clear reactions")
                    self.player_message = await message.reply(f'Now playing: {info["title"]}')
                else:
                    await self.player_message.edit(content=f'Now playing: {info["title"]}')
            await self.player_message.add_reaction('⏪')
            await self.player_message.add_reaction('⏸')
            await self.player_message.add_reaction('⏩')
            self.voice_client.play(discord.FFmpegPCMAudio(source=url, **self.ffmpeg_options))

            while self.voice_client.is_playing():
                if self.is_next:
                    print('[Player.play()] change to next track because of button')
                    self.voice_client.stop()
                    self.is_next = False
                    self.current += 1
                    break
                elif self.is_previous:
                    print('[Player.play()] change to previous track because of button')
                    self.voice_client.stop()
                    self.is_paused = False
                    self.current -= 1
                    break
                elif self.is_paused:
                    print('[Player.play()] paused because of button')
                    self.voice_client.pause()
                elif not self.voice_client.is_paused():
                    await sleep(3)
            else:
                self.current += 1
        await self.voice_client.disconnect()
        try:
            await self.player_message.unpin()
        except discord.errors.Forbidden:
            print("can't unpin")
        await self.player_message.delete()
        self.voice_client = None

    async def add_to_queue(self, music, message):
        info = search(music)
        self.music_list.append(info)
        await message.reply(f'{info["title"]} is {len(self.music_list) - self.current} in queue')
