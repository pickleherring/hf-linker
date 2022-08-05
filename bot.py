import logging
import os

import aiohttp
import discord
import dotenv

import hf


logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

REQUEST_PARAMS = {'enterAgree': 1}


summarizers = {
    'image': hf.summarize_image,
    'story': hf.summarize_story,
}

client = discord.Client()


def format_summary(summary):

    embed = discord.Embed(
        colour=discord.Colour.magenta(),
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
    
    embed.add_field(
        name='ratings',
        value='**' + '**, **'.join(summary['ratings']) + '**'
    )

    return embed


@client.event
async def on_ready():

    for guild in client.guilds:
        print(f'connected to \'{guild.name}\'')


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    urls = hf.find_urls(message.content)

    if urls:
    
        async with aiohttp.ClientSession() as session:

            for url in urls:

                url_type = hf.classify_url(url)

                if url_type:
                    
                    async with session.get('https://' + url, params=REQUEST_PARAMS) as response:
                        if response.status == 200:
                            page = await response.text()

                    summary = summarizers[url_type](page)

                    if summary:
                        embed = format_summary(summary)
                        await message.channel.send(embed=embed)


client.run(DISCORD_TOKEN)