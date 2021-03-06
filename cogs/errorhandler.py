import discord
from discord.ext import commands
import re, difflib


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(title="Fatal Error:", colour=discord.Color.from_rgb(81, 0, 124))
        embed.set_footer(text=self.bot.KAEBOT_VERSION)
        embed.set_thumbnail(url="https://i.ibb.co/dBVGPwC/Icon.png")

        async with self.bot.kaedb.acquire() as conn:
            async with conn.transaction():
                if await conn.fetchrow("SELECT * FROM exiled_users WHERE user_id = $1", str(ctx.author.id)):
                    return

        if hasattr(ctx.command, "on_error"):
            return

        elif isinstance(error, commands.CheckFailure):
            return

        elif isinstance(error, commands.CommandNotFound):
            try:
                invalidcommand = re.findall(r"\"([^\"]*)\"", error.args[0])[0]
            except IndexError:
                invalidcommand = None
            similar = difflib.get_close_matches(
                invalidcommand, [x.name for x in self.bot.commands], n=5, cutoff=0.6
            )  # Get similar words

            similarstr = ""
            if not similar:
                similarstr = "No matches found."
            else:
                for simstr in similar:
                    similarstr += f"{simstr}\n"

            embed.add_field(name="Invalid command. Did you mean:", value=similarstr, inline=False)

        elif isinstance(error, commands.MissingRequiredArgument):
            embedstr = f"{error.param.name} (of type {str(error.param).split(': ')[1]})."  # hacky way to get arg type
            embed.add_field(name="Missing required argument:", value=embedstr, inline=False)

        else:
            embed.add_field(name="An unhandled exception occurred.", value=str(error), inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
