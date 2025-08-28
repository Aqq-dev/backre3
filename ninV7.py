import discord
import time
import asyncio
from ninFlaskV7 import start
import os
from asyncEAGM import EAGM
import db   # ← 追加

client = discord.Client(intents = discord.Intents.default())
tree = discord.app_commands.CommandTree(client)

BOTTOKEN=os.getenv("BOTTOKEN")
authurl=os.getenv("AUTH_URL")
eagm=EAGM(bot_token=BOTTOKEN)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="認証ボタン"))
    print(f"Thankyou for running! {client.user}")
    await tree.sync()

@tree.command(name="button", description="認証ボタンの表示")
async def panel_au(interaction: discord.Interaction, ロール:discord.Role, タイトル:str="こんにちは！", 説明:str="リンクボタンから登録して認証完了"):
    if not interaction.guild:
        return await interaction.response.send_message("DMでは使えません", ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("管理者しか使えません", ephemeral=True)
    
    button = discord.ui.Button(label="登録リンク", style=discord.ButtonStyle.primary, url=authurl+f"&state={(hex(interaction.guild_id)).upper()[2:]}")
    view = discord.ui.View()
    view.add_item(button)
    await interaction.response.send_message("made by ```.taka.``` thankyou for running!", ephemeral=True)
    
    db.upsert_server(str(interaction.guild.id), str(ロール.id))  # Supabase保存
    
    await interaction.channel.send(view=view,embed=discord.Embed(title=タイトル,description=説明,color=discord.Colour.blue()))
