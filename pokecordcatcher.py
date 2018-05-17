import asyncio
import aiohttp
import discord
import json
import random
import hashlib

from distutils.version import LooseVersion

__version__ = '1.0.2'


class Poke(discord.Client):
    def __init__(self, config_path: str, *args, **kwargs):
        self.config_path = config_path
        
        # Set update check to false on init
        self.update_check = False

        # Load config
        with open(self.config_path) as f:
            self.configs = json.load(f)

        # Casefold/lowercase all names in either priority or avoid list (TODO: Maybe think of a neater solution)
        if self.configs['priority']:
            for num, name in enumerate(self.configs['priority']):
                self.configs['priority'][num] = name.casefold()
        if self.configs['avoid_list']:
            for num, name in enumerate(self.configs['avoid_list']):
                self.configs['avoid_list'][num] = name.casefold()

        # Load pokemon hash -> name dict.
        with open('poke.json') as f:
            self.poke = json.load(f)
        super().__init__()

    async def match(self, url):
        # GET the image from url, read into dat, md5 hash then hexdigest into m and return corresponding name from dict
        async with await self.ses.get(url) as resp:
            dat = await resp.content.read()
        m = hashlib.md5(dat).hexdigest()
        return self.poke[m]

    def run(self):
        super().run(self.configs['token'], bot=False)

    # Too much extra code for aesthetic purposes, though this is kinda eye catching
    # TODO: Simplify update check
    @staticmethod
    def bordered(text):
        lines = text.splitlines()
        width = max(len(s) for s in lines)
        res = ['┌' + '─' * width + '┐']
        for s in lines:
            res.append('│' + (s + ' ' * width)[:width] + '│')
        res.append('└' + '─' * width + '┘')
        return '\n'.join(res)

    async def on_message(self, message):
        # Next two ifs are facilitated by the check in on_ready, tldr; both can not co-exist.
        # Terminate if current message's channel id is not in whitelist.
        if self.configs['whitelist_channels'] and message.channel.id not in self.configs['whitelist_channels']:
            return
        # Terminate if current message's channel id is in blacklist.
        if self.configs['blacklist_channels'] and message.channel.id in self.configs['blacklist_channels']:
            return
        # Check if the message is from pokecord and if it has an embed.
        if message.author.id == 365975655608745985 and message.embeds:
            emb = message.embeds[0]
            title = emb.title
            # Terminate if bogus embed.
            if type(title) is not str:
                return
            # Check if it is a pokemon spawn embed
            if title.startswith('A wild'):
                name = await self.match(emb.image.url.split('?')[0])
                # Proc a random number from 1 to 100, basically a 60% chance for anything to happen is any number below and including 60.
                proc = random.randint(1, 100)
                if self.configs['priority_only'] and name not in self.configs['priority']:
                    return
                if name in self.configs['priority'] or (proc <= self.configs['catch_rate'] and
                                                        name not in self.configs['avoid_list']):
                    if name in self.configs['priority']:
                        self.configs['priority'].remove(name)
                    if name in self.configs['priority'] and not self.configs['delay_on_priority']:
                        pass
                    else:
                        await asyncio.sleep(self.configs['delay'])
                    pref = emb.description.split()[5]

                    await message.channel.send(f"{pref} {name}")
                    msgs = await message.channel.history(after=message, limit=10).flatten()
                    for msg in msgs:
                        if msg.content.lower() == f"{pref} {name}".lower():
                            
                            if msg.author == self.user:
                                return print('Caught {}{}'.format(name, f' in {message.guild.name} in #{message.channel.name}.' if
                                             self.configs["verbose"] else "."))
                            
                            else:
                                return print('Failed to catch {}{}'.format(name, f' in {message.guild.name}'
                                                                                f' in #{message.channel.name}.'
                                                                                if self.configs["verbose"] else "."))
                elif self.configs['verbose']:
                    print(f"Skipped a {name}")
    
    async def on_ready(self):
        # aiohttp session for downloading images
        self.ses = aiohttp.ClientSession()
        # github API latest release check, LooseVersion makes version comparison with multiple '.' easier ex. 2.2.3
        if not self.update_check:
            async with aiohttp.ClientSession(loop=self.loop) as session:
                async with session.get('http://api.github.com/repos/xKynn/PokecordCatcher/releases') as resp:
                    ver = await resp.json()
            ver_tag = ver[0]['tag_name']
            if LooseVersion(ver_tag) > LooseVersion(__version__):
                print(self.bordered(f'A new version is available! Please update ASAP.\n{ver[0]["name"]}\n{ver[0]["body"]}\n'
                                     'Visit http://www.github.com/xKynn/PokecordCatcher/releases/latest'))
            self.update_check = True
        print("Logged in.\n---PokecordCatcher----\n"
              f"Priority: {', '.join(self.configs['priority'])}\n"
              f"Catch Rate: {self.configs['catch_rate']}%\n"
              f"Catch Delay: {self.configs['delay']} seconds\n"
              f"Delay On Priority: {'On' if self.configs['delay_on_priority'] == True else 'Off'}")
        if self.configs['whitelist_channels'] and self.configs['blacklist_channels']:
            print('------\nCan only have either blacklist__channels active or whitelist_channels active\n'
                  'Please clear one of the two lists to use the bot\n-----\nLogging out.')
            await self.logout()