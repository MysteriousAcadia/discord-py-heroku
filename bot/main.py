import discord
import os
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import re
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
def getTokensByDiscordId(discordId="0"):
    url = "https://oneverse-backend.vercel.app/api/admin/" + str(
        discordId);
    resp = requests.get(url)
    return resp.json()


def getUsers(page=1):
    url = "https://oneverse-backend.vercel.app/api/admin/get?page=" + str(page)
    resp = requests.get(url)
    return resp.json()

def createUser(token="", discordId=""):
    data = {"token": token, "discordId": discordId};
    resp = requests.post(
        "https://oneverse-backend.vercel.app/api/admin/addUser",
        json=data);
    status = resp.status_code;
    print(status)
    response = resp.json()

    print(response);
    if (status == 500):
        return False
    elif (status == 200):
        return True


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)


def embedAuth():
    embed = discord.Embed(title="Authentication Requested")
    embed.add_field(name="Description",
                    value="You have requested Discord to Metamask connection for role allotment in ONEVerse Server",
                    inline=False)
    embed.add_field(name="Note",
                    value="Make sure the url you're connecting your wallet with is ours, check announcements to know more",
                    inline=False)
    embed.add_field(name="Authenticate on our website",
                    value="[Click here](https://oneverse-discord.web.app/)")
    return embed


@client.event
async def on_ready():
    print("we have logged in as {0.user}".format(client))


@client.command()
async def auth(ctx):
    user = ctx.message.author
    await user.send(embed=embedAuth())


@client.command()
async def create(ctx, token):
    user = ctx.message.author
    print(token)
    print(user.id)
    result = createUser(str(token), str(user.id))
    if result:
        await user.send("Authenticated")
    else:
        await user.send("Failed, retry or contact Devs to know more")


refreshOn = False


@client.command()
async def refresh(ctx):
    global refreshOn

    OneVRoles = ["First Lieutenant", "Brigadier General", "Lieutenant General",
                 "Senior Commander", "Grand Admiral",
                 "Constellation Commander", "Galactic Emperor"]
    server = ctx.guild
    roles = server.roles
    roleByName = {}
    for role in roles:
        roleByName[role.name] = role
    if not ctx.message.author.guild_permissions.administrator:
        user = ctx.message.author
        print(user)
        try:
            for y in user.roles:
                if y.name in OneVRoles:
                    await user.remove_roles(y)
            tokens = int(getTokensByDiscordId(user.id)[0]['balance'])
            print(tokens)

            if tokens >= 500:
                await user.add_roles(roleByName["Galactic Emperor"])
            elif tokens >= 250:
                await user.add_roles(roleByName["Constellation Commander"])
            elif tokens >= 100:
                await user.add_roles(roleByName["Grand Admiral"])
            elif tokens >= 50:
                await user.add_roles(roleByName["Senior Commander"])
            elif tokens >= 30:
                await user.add_roles(roleByName["Lieutenant General"])
            elif tokens >= 20:
                await user.add_roles(roleByName["Brigadier General"])
            elif tokens >= 10:
                await user.add_roles(roleByName["First Lieutenant"])
        except: pass
        return
    if refreshOn:
        print("Already refreshing")
        return
    refreshOn = True

    print("Starting refresh")
    status = await ctx.send("Starting refresh")
    members = server.members

    for member in members:
        if not member.guild_permissions.administrator and not member.bot:
            for y in member.roles:
                if y.name in OneVRoles:
                    await member.remove_roles(y)

    A = int(getUsers()['totalPages'])
    for i in range(A):
        B = getUsers(i + 1)['docs']
        for entries in B:
            user = server.get_member(int(entries['discordId']))
            try:
                if user is not None:
                    tokens = int(entries['balance'])
                    for y in user.roles:
                        if y.name in OneVRoles:
                            await user.remove_roles(y)
                    if tokens >= 500:
                        await user.add_roles(roleByName["Galactic Emperor"])
                    elif tokens >= 250:
                        await user.add_roles(roleByName["Constellation Commander"])
                    elif tokens >= 100:
                        await user.add_roles(roleByName["Grand Admiral"])
                    elif tokens >= 50:
                        await user.add_roles(roleByName["Senior Commander"])
                    elif tokens >= 30:
                        await user.add_roles(roleByName["Lieutenant General"])
                    elif tokens >= 20:
                        await user.add_roles(roleByName["Brigadier General"])
                    elif tokens >= 10:
                        await user.add_roles(roleByName["First Lieutenant"])
                    await status.edit(content="Refreshing "+user.name)
            except:
                pass

    await status.edit(content="Refreshed")
    refreshOn = False


client.run(TOKEN)
