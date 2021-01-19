import asyncio
import functools
import logging
import sys
from io import BytesIO
from typing import Optional, Union, cast

import aiohttp
import discord
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from redbot.core import Config, commands
from redbot.core.data_manager import bundled_data_path
from redbot.core.i18n import Translator, cog_i18n

from .funbadge_entry import FunBadge
from .barcode import ImageWriter, generate
from .templates import blank_template

_ = Translator("FunBadges", __file__)
log = logging.getLogger("red.StuxCogs.funbadges")


@cog_i18n(_)
class FunBadges(commands.Cog):
    """
    Create fun fake badges based on your discord profile
    """

    __author__ = ["StuxieDev"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 1545487348434)
        default_guild = {"funbadges": []}
        default_global = {"funbadges": blank_template}
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    def remove_white_barcode(self, img: Image) -> Image:
        """https://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent"""
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        return img

    def invert_barcode(self, img: Image) -> Image:
        """https://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent"""
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((255, 255, 255))
            else:
                newData.append(item)

        img.putdata(newData)
        return img

    async def dl_image(self, url: str) -> BytesIO:
        """Download bytes like object of user avatar"""
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as resp:
                test = await resp.read()
                return BytesIO(test)

    def make_template(
        self, user: Union[discord.User, discord.Member], funbadge: FunBadge, template: Image
    ) -> Image:
        """Build the base template before determining animated or not"""
        if hasattr(user, "roles"):
            department = (
                _("GENERAL SUPPORT")
                if user.top_role.name == "@everyone"
                else user.top_role.name.upper()
            )
            status = user.status
            level = str(len(user.roles))
        else:
            department = _("GENERAL SUPPORT")
            status = "online"
            level = "1"
        if str(status) == "online":
            status = _("ACTIVE")
        if str(status) == "offline":
            status = _("COMPLETING TASK")
        if str(status) == "idle":
            status = _("AWAITING INSTRUCTIONS")
        if str(status) == "dnd":
            status = _("MIA")
        barcode = BytesIO()
        log.debug(type(barcode))
        generate("code39", str(user.id), writer=ImageWriter(self), output=barcode)
        barcode = Image.open(barcode)
        barcode = self.remove_white_barcode(barcode)
        fill = (0, 0, 0)  # text colour fill
        if funbadge.is_inverted:
            fill = (255, 255, 255)
            barcode = self.invert_barcode(barcode)
        template = Image.open(template)
        template = template.convert("RGBA")
        barcode = barcode.convert("RGBA")
        barcode = barcode.resize((555, 125), Image.ANTIALIAS)
        template.paste(barcode, (400, 520), barcode)
        # font for user information
        font_loc = str(bundled_data_path(self) / "arial.ttf")
        try:
            font1 = ImageFont.truetype(font_loc, 30)
            font2 = ImageFont.truetype(font_loc, 24)
        except Exception as e:
            print(e)
            font1 = None
            font2 = None
        # font for extra information

        draw = ImageDraw.Draw(template)
        # adds username
        draw.text((225, 330), str(user.display_name), fill=fill, font=font1)
        # adds ID Class
        draw.text((225, 400), funbadge.code + "-" + str(user).split("#")[1], fill=fill, font=font1)
        # adds user id
        draw.text((250, 115), str(user.id), fill=fill, font=font2)
        # adds user status
        draw.text((250, 175), status, fill=fill, font=font2)
        # adds department from top role
        draw.text((250, 235), department, fill=fill, font=font2)
        # adds user level
        draw.text((420, 475), _("LEVEL ") + level, fill="red", font=font1)
        # adds user level
        if funbadge.badge_name != "discord" and user is discord.Member:
            draw.text((60, 585), str(user.joined_at), fill=fill, font=font2)
        else:
            draw.text((60, 585), str(user.created_at), fill=fill, font=font2)
        barcode.close()
        return template

    def make_animated_gif(self, template: Image, avatar: BytesIO) -> BytesIO:
        """Create animated fun badge from gif avatar"""
        gif_list = [frame.copy() for frame in ImageSequence.Iterator(avatar)]
        img_list = []
        num = 0
        for frame in gif_list:
            temp2 = template.copy()
            watermark = frame.copy()
            watermark = watermark.convert("RGBA")
            watermark = watermark.resize((100, 100))
            watermark.putalpha(128)
            id_image = frame.resize((165, 165))
            temp2.paste(watermark, (845, 45, 945, 145), watermark)
            temp2.paste(id_image, (60, 95, 225, 260))
            temp2.thumbnail((500, 339), Image.ANTIALIAS)
            img_list.append(temp2)
            num += 1
            temp = BytesIO()

            temp2.save(
                temp, format="GIF", save_all=True, append_images=img_list, duration=0, loop=0
            )
            temp.name = "temp.gif"
            if sys.getsizeof(temp) > 7000000 and sys.getsizeof(temp) < 8000000:
                break
        return temp

    def make_funbadge(self, template: Image, avatar: Image):
        """Create basic fun badge from regular avatar"""
        watermark = avatar.convert("RGBA")
        watermark.putalpha(128)
        watermark = watermark.resize((100, 100))
        id_image = avatar.resize((165, 165))
        template.paste(watermark, (845, 45, 945, 145), watermark)
        template.paste(id_image, (60, 95, 225, 260))
        temp = BytesIO()
        template.save(temp, format="PNG")
        temp.name = "temp.gif"
        return temp

    async def create_funbadge(self, user, funbadge, is_gif: bool):
        """Async create fun badges handler"""
        template_img = await self.dl_image(funbadge.file_name)
        task = functools.partial(self.make_template, user=user, funbadge=funbadge, template=template_img)
        task = self.bot.loop.run_in_executor(None, task)
        try:
            template = await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            return
        if user.is_avatar_animated() and is_gif:
            url = user.avatar_url_as(format="gif")
            avatar = Image.open(await self.dl_image(url))
            task = functools.partial(self.make_animated_gif, template=template, avatar=avatar)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return

        else:
            url = user.avatar_url_as(format="png")
            avatar = Image.open(await self.dl_image(url))
            task = functools.partial(self.make_funbadge, template=template, avatar=avatar)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return

        temp.seek(0)
        return temp

    async def get_funbadge(self, badge_name: str, guild: Optional[discord.Guild] = None) -> FunBadge:
        if guild is None:
            guild_funbadges = []
        else:
            guild_funbadges = await self.config.guild(guild).funbadges()
        all_funbadges = await self.config.funbadges() + guild_funbadges
        to_return = None
        for funbadge in all_funbadges:
            if badge_name.lower() in funbadge["badge_name"].lower():
                to_return = await FunBadge.from_json(funbadge)
        return to_return

    @commands.command(aliases=["funbadge"])
    async def funbadges(self, ctx: commands.Context, *, funbadge: str) -> None:
        """
        Create your own fun badge with your discord info

        `funbadge` is the name of the fun badges
        do `[p]listfunbadges` to see available fun badges
        """
        guild = ctx.message.guild
        user = ctx.message.author
        if funbadge.lower() == "list":
            await ctx.invoke(self.listfunbadges)
            return
        funbadge_obj = await self.get_funbadge(funbadge, guild)
        if not funbadge_obj:
            await ctx.send(_("`{}` is not an available fun badge.").format(funbadge))
            return
        async with ctx.channel.typing():
            funbadge_img = await self.create_funbadge(user, funbadge_obj, False)
            if funbadge_img is None:
                await ctx.send(_("Something went wrong sorry!"))
                return
            image = discord.File(funbadge_img, "funbadge.png")
            embed = discord.Embed(color=ctx.author.color)
            embed.set_image(url="attachment://funbadge.png")
            funbadge_img.close()
            await ctx.send(files=[image])

    @commands.command(aliases=["gfunbadge"])
    async def gfunbadges(self, ctx: commands.Context, *, funbadge: str) -> None:
        """
        Create your own fun gif badge with your discord info
        this only works if you have a gif avatar

        `funbadge` is the name of the fun badges
        do `[p]listfunbadges` to see available fun badges
        """
        guild = ctx.message.guild
        user = ctx.message.author
        if funbadge.lower() == "list":
            await ctx.invoke(self.listfunbadges)
            return
        funbadge_obj = await self.get_funbadge(funbadge, guild)
        if not funbadge_obj:
            await ctx.send(_("`{}` is not an available fun badge.").format(funbadge))
            return
        async with ctx.channel.typing():
            funbadge_img = await self.create_funbadge(user, funbadge_obj, True)
            if funbadge_img is None:
                await ctx.send(_("Something went wrong sorry!"))
                return
            image = discord.File(funbadge_img)
            funbadge_img.close()
            await ctx.send(file=image)

    @commands.command()
    async def listfunbadges(self, ctx: commands.Context) -> None:
        """
        List the available fun badges that can be created
        """
        # guild = ctx.message.guild
        global_funbadges = await self.config.funbadges()
        # guild_funbadges = await self.config.guild(guild).funbadges()
        msg = _("__Global Fun Badges__\n")
        msg += ", ".join(funbadge["badge_name"] for funbadge in global_funbadges)

        # for funbadge in await self.config.funbadges():
        # if guild_funbadges != []:
        # funbadges = ", ".join(funbadge["badge_name"] for funbadge in guild_funbadges)
        # em.add_field(name=_("Global Fun Badges"), value=badges)
        await ctx.maybe_send_embed(msg)
