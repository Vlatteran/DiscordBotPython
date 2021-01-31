from discord import Client
import discord
from config import settings
from Player import Player
import discord.guild


class MyBot(Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.player = Player()

    async def on_ready(self):
        print(f'[MyBot.on_ready]We have logged in as {self.user}')

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
            elif self.player.voice_client is None:
                await self.player.connect(message.author.voice.channel)
            else:
                await message.reply(f'{self.user.name}'
                                    f' already connected to '
                                    f'{self.player.voice_client.channel}'
                                    f' voice channel')
        elif command == '!disconnect':
            if self.player.voice_client is None:
                await message.reply(f'{self.user.name} is not connected to any channel')
            elif message.author.voice.channel != self.player.voice_client.channel:
                await message.reply(f"Yoe can't use Player of {self.user.name}, "
                                    f"when it connected to other voice channel")
            else:
                await self.player.disconnect()
        elif command == '!tolist':
            await self.player.add_to_queue(command_text, message)
        elif command == '!play':
            await self.player.play(message)
        elif command == '!showlist':
            amount = len(self.player.music_list) - self.player.current
            amount = 10 if amount > 10 else amount
            text = f'First {amount} tracks in list:\n'
            text += '\n'.join([str(num + 1) + ". " + info['title'] for info, num in
                               zip(self.player.music_list[self.player.current:amount+1], range(amount))])
            await message.reply(text)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user == self.user:
            return
        print(f'[MyBot.on_reaction_add()]{user} added reaction {reaction} to the {reaction.message.content} in'
              f' {reaction.message.guild}.{reaction.message.channel}')
        if reaction.message == self.player.player_message:
            if reaction.emoji == '⏪':
                print('previous')
                self.player.is_previous = True
            elif reaction.emoji == '⏸':
                print('pause')
                self.player.is_paused = True
            elif reaction.emoji == '⏩':
                print('next')
                self.player.is_next = True


if __name__ == '__main__':
    bot = MyBot()
    bot.run(settings['token'])
