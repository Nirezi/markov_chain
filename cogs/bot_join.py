import asyncio
import json

import discord
from discord.ext import commands
import MeCab
import markovify


class BotJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.tagger = MeCab.Tagger("-Owakati")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        text = self.tagger.parse("今日はいい天気ですね。")
        model = markovify.Text(text, state_size=2)

        async with self.lock:  # 同時アクセスを防ぐ
            with open(f"models/{guild.id}.json", "w") as f:
                model = model.to_json()
                json.dump(model, f)


def setup(bot):
    bot.add_cog(BotJoin(bot))
