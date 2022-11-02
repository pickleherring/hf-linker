import logging
import os

import aiohttp
import discord
from discord.ext import commands
import dotenv

import hf
import lit


logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

HF_REQUEST_PARAMS = {'enterAgree': 1}
HF_SUMMARIZERS = {
    'image': hf.summarize_image,
    'story': hf.summarize_story,
}

LIT_REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='/',
    description='HF linker bot',
    intents=intents
)


def format_hf_summary(summary):

    embed = discord.Embed(
        colour=discord.Color.from_str('0xff67a2'),
        title=summary['title'],
		url=summary['url'],
        description=summary['description']
    )

    embed.set_author(
        name=summary['user'],
        url=summary['user_url'],
        icon_url=summary['user_icon']
    )

    embed.set_image(url=summary['image'])
    
    if summary['ratings']:
        embed.add_field(
            name='ratings',
            value='**' + '**, **'.join(summary['ratings']) + '**'
        )
    else:
        embed.add_field(
            name='ratings',
            value='*none*'
        )

    embed.set_footer(
        text='Hentai Foundry',
        icon_url='https://img.hentai-foundry.com/themes/Dark/favicon.ico'
    )

    return embed


def format_lit_summary(summary, url):

    embed = discord.Embed(
        colour=discord.Color.from_str('0x4a89f3'),
        title=summary['title'],
		url='https://' + url,
        description=summary['description']
    )

    embed.set_author(
        name=summary['author'],
        url=summary['author_url'],
        icon_url=summary['author_icon']
    )

    embed.add_field(
        name='words',
        value=summary['words']
    )

    if summary['tags']:
        embed.add_field(
            name='tags',
            value='**' + '**, **'.join(summary['tags']) + '**'
        )
    else:
        embed.add_field(
            name='tags',
            value='*none*'
        )

    embed.set_footer(
        text='Literotica',
        icon_url='https://speedy.literotica.com/authenticate/favicon-9238b3a65e563edb3cf7906ccfdc81bb.ico'
    )

    return embed


@bot.command()
async def HFstatus(ctx):
    """Check whether hentai-foundry.com is currently reachable.
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(hf.BASE_URL, params=HF_REQUEST_PARAMS) as response:
            await ctx.message.reply(f'{response.status} {response.reason}')


@bot.command()
async def Litstatus(ctx):
    """Check whether literotica.com is currently reachable.
    """

    async with aiohttp.ClientSession(headers=LIT_REQUEST_HEADERS) as session:
        async with session.get(lit.BASE_URL) as response:
            await ctx.message.reply(f'{response.status} {response.reason}')


@bot.event
async def on_ready():

    for guild in bot.guilds:
        print(f'connected to \'{guild.name}\'')


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    hf_urls = hf.find_urls(message.content)
    lit_urls = lit.find_urls(message.content)

    if hf_urls:
    
        async with aiohttp.ClientSession() as session:

            for url in hf_urls:

                url_type = hf.classify_url(url)

                if url_type:
                    
                    async with session.get('https://' + url, params=HF_REQUEST_PARAMS) as response:
                        if response.status == 200:
                            page = await response.text()

                    summary = HF_SUMMARIZERS[url_type](page)

                    if summary:
                        embed = format_hf_summary(summary)
                        await message.channel.send(embed=embed)
    
    if lit_urls:
    
        async with aiohttp.ClientSession(headers=LIT_REQUEST_HEADERS) as session:

            for url in lit_urls:

                async with session.get('https://' + url) as response:
                    if response.status == 200:
                        page = await response.text()

                summary = lit.summarize_story(page)

                if summary:
                    embed = format_lit_summary(summary, url)
                    await message.channel.send(embed=embed)
    
    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)
