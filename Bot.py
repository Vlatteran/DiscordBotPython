from discord import Client
from Player import Player
import discord.guild
import sys


class MyBot(Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.players = {}

    async def on_ready(self):
        print(f'[MyBot.on_ready]We have logged in as {self.user}')
        for guild in self.guilds:
            self.players[guild] = Player()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        print(f'[MyBot.on_message]{message.author} in {message.guild}.{message.channel}: {message.content}')
        command = message.content.split(' ')[0]
        command_text = ' '.join(message.content.split(' ')[1:])
        if command == '!hello':
            await message.reply(f'Hello, {message.author.name}!')
        elif command == '!connect':
            if message.author.voice is None:
                await message.reply(f'You must be connected to use Player of {self.user.name}')
            elif self.players[message.guild].voice_client is None:
                await self.players[message.guild].connect(message.author.voice.channel)
            else:
                await message.reply(f'{self.user.name}'
                                    f' already connected to '
                                    f'{self.players[message.guild].voice_client.channel}'
                                    f' voice channel')
        elif command == '!disconnect':
            if self.players[message.guild].voice_client is None:
                await message.reply(f'{self.user.name} is not connected to any channel')
            elif message.author.voice.channel != self.players[message.guild].voice_client.channel:
                await message.reply(f"Yoe can't use Player of {self.user.name}, "
                                    f"when it connected to other voice channel")
            else:
                await self.players[message.guild].disconnect()
        elif command == '!tolist':
            await self.players[message.guild].add_to_queue(command_text, message)
        elif command == '!play':
            await self.players[message.guild].play(message)
        elif command == '!showlist':
            amount = len(self.players[message.guild].music_list) - self.players[message.guild].current
            amount = 10 if amount > 10 else amount
            text = f'First {amount} tracks in list:\n'
            text += '\n'.join([str(num + 1) + ". " + info['title'] for info, num in
                               zip(
                                   self.players[message.guild].music_list[
                                   self.players[message.guild].current:amount + 1],
                                   range(amount)
                               )])
            await message.reply(text)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user == self.user:
            return
        print(f'[MyBot.on_reaction_add()]{user} added reaction {reaction} to the {reaction.message.content} in'
              f' {reaction.message.guild}.{reaction.message.channel}')
        if reaction.message == self.players[reaction.message.guild].player_message:
            if reaction.emoji == '⏪':
                self.players[reaction.message.guild].is_previous = True
            elif reaction.emoji == '⏸':
                self.players[reaction.message.guild].is_paused = True
            elif reaction.emoji == '⏩':
                self.players[reaction.message.guild].is_next = True
            elif reaction.emoji == '▶':
                self.players[reaction.message.guild].is_resumed = True


if __name__ == '__main__':
    bot = MyBot()
    if len(sys.argv) > 0:
        token = sys.argv[0]
    else:
        from config import settings
        token = settings['token']
    bot.run(token)
