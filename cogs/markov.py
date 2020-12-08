import asyncio
import json

import MeCab
import discord
import markovify
from discord.ext import commands


class Markov(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.tagger = MeCab.Tagger("-Owakati")  # 分かち書きした文章だけを出力

    @classmethod
    async def make_model(cls, model: markovify.Text, text: str) -> markovify.Text:
        """
        引数のモデルに引数の文章を学習させ、結果を返す
        :param model: 学習させたいモデル
        :param text: 学習させたい文章 ※要分かち書き
        :return: 学習後のモデル
        """

        new_model = markovify.Text(text, state_size=2, retain_original=False, well_formed=False)
        # well_formedをFalseにして"()"などが含まれていてもエラーがでないように
        merged_model = markovify.combine([model, new_model])
        return merged_model

    async def write_model(self, file_name: str, model: markovify.Text) -> None:
        """
        markovify.Text型のmodelをjson形式で保存する
        :param file_name: 保存したいファイル名
        :param model: 保存したいmodel
        :return: None
        """
        async with self.lock:  # 同時アクセスを防ぐ
            with open(f"models/{file_name}", "w") as f:
                model = model.to_json()
                json.dump(model, f)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if any((message.author.bot, not message.guild, not message.content)):
            return

        file_name = f"{message.guild.id}.json"

        with open(f"models/{file_name}", "r") as f:
            file = json.load(f)
            model = markovify.Text.from_json(file)  # モデルファイルを読み込む

        text = self.tagger.parse(message.clean_content)
        merged_model = await self.make_model(model, text)
        await self.write_model(file_name, merged_model)

        sentence = merged_model.make_sentence().replace(" ", "")
        if not sentence:  # 学習量が足りず、文章が生成できなかった場合
            sentence = merged_model.make_sentence(test_output=False).replace(" ", "")
            # test_outputをFalseにして文章をチェックを無効化する
            sentence += "\n※学習量が不足しているため、元の文章と似通った文章になっています。"

        await message.channel.send(sentence)


def setup(bot):
    bot.add_cog(Markov(bot))
