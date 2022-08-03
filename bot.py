import os

import discord
import dotenv

import hf


dotenv.load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

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

    for url in urls:

        summary = hf.summarize_page(url)

        if summary:
            embed = format_summary(summary)
            await message.channel.send(embed=embed)


client.run(DISCORD_TOKEN)