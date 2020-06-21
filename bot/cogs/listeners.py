import re
import random
import logging
from typing import Tuple, Mapping
from pkg_resources import resource_filename

from discord import Message
from discord.ext.commands import Cog


NICE_REGEX = re.compile('(?<!\S)n+i+c+e+(?!\S)', re.IGNORECASE)


class Listeners(Cog):

    def __init__(self, bot: 'NiceBot', dp: 'DataProxy', config: Mapping):
        self.bot = bot
        self.dp = dp
        self.config = config

    @Cog.listener()
    async def on_ready(self):
        logging.info('Logged in as {0.user}'.format(self.bot))

    @Cog.listener()
    async def on_message(self, msg):
        # Disregard:
        #   * messages produced by bot.
        #   * messages that mention bot.
        if (msg.author == self.bot.user) or (self.bot.user in msg.mentions):
            return

        content, quote = process_message(msg)

        if NICE_REGEX.search(content):
            data = {
                'srv': msg.guild.id,
                'date': msg.created_at,
                'author': msg.author.id,
                'mentions': [mem.id for mem in msg.mentions],
                'quote': quote
            }
            logging.info('Storing entry: %r', data)
            self.dp.store(**data)
            if random.random() < self.config['spam']:
                await msg.channel.send(f'{msg.author.mention} {get_spam()}')


def get_spam() -> str:
    with open(
            file=resource_filename('bot', 'resources/spam.txt'),
            mode='r'
    ) as f:
        content = [block.strip() for block in f.read().split('---')]
    return random.choice(content)


def process_message(msg: Message) -> Tuple[str, str]:
    quote = ''
    content = ''
    for line in msg.clean_content.split('\n'):
        if line.startswith('>'):
            quote += line
        else:
            content += line
    return content, quote
