import asyncio
import discord
import json
import re
import random


class Poke(discord.Client):
    def __init__(self, config_path: str, *args, **kwargs):
        self.config_path = config_path
        self.p = re.compile('([A-Z])\w+')
        with open(self.config_path) as f:
            self.configs = json.load(f)

        super().__init__()

    def run(self):
        super().run(self.configs['token'], bot=False)

    async def on_message(self, message):
        if self.configs['whitelist_channels'] and message.channel.id not in self.configs['whitelist_channels']:
            return
        if self.configs['blacklist_channels'] and message.channel.id in self.configs['blacklist_channels']:
            return
        if message.author.id == 365975655608745985 and message.embeds:
            emb = message.embeds[0]
            if emb.title.startswith('A wild'):
                name = self.p.search(emb.image.url.split('/')[-1:][0]).group()
                proc = random.randint(1, 100)
                if name in self.configs['priority'] or proc <= self.configs['catch_rate']:
                    if name in self.configs['priority']:
                        self.configs['priority'].pop(name)
                    pref = emb.description.split()[5]
                    print(f'Caught "{name}" in {message.guild.name} in #{message.channel.name}')
                    if self.configs['delay_on_priority']:
                        await asyncio.sleep(self.configs['delay'])
                    await message.channel.send(f"{pref} {name}")
    
    async def on_ready(self):
        print("Logged in.\n---PokecordCatcher----\n"
              f"Priority: {', '.join(self.configs['priority'])}\n"
              f"Catch Rate: {self.configs['catch_rate']}%\n"
              f"Catch Delay: {self.configs['delay']} seconds\n"
              f"Delay On Priority: {'On' if self.configs['delay_on_priority'] == True else 'Off'}")
        if self.configs['whitelist_channels'] and self.configs['blacklist_channels']:
            print('------\nCan only have either blacklist__channels active or whitelist_channels active\n'
                  'Please clear one of the two lists to use the bot\n-----\nLogging out.')
            await self.logout()

