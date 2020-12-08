#!/usr/bin/python3
# coding:utf-8
import os
import traceback

import discord
from discord.ext import commands
from os.path import dirname, join
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)  # 環境変数を読み込む
TOKEN = os.getenv("TOKEN")


class Bot(commands.Bot):
    def __init__(self, prefix):
        intents = discord.Intents.all()
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        super().__init__(command_prefix=prefix, allowed_mentions=allowed_mentions, intents=intents, help_command=None)

        self.load_extension('jishaku')
        path = "./cogs" if os.name == "nt" else "./cogs"  # 実行環境によってpathを変える
        for file in os.listdir(path):
            if file.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{file[:-3]}")
                except Exception:
                    traceback.print_exc()

        @self.command()
        async def hello(ctx):
            await ctx.send(f"Hello! {ctx.author.name}")

    async def on_ready(self):
        print(f"{self.user.name}({self.user.id}) has started.")


if __name__ == "__main__":
    bot = Bot("/")
    bot.run(TOKEN)
