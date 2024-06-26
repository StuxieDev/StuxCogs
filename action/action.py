from redbot.core import Config, commands, checks
from urllib.request import urlopen
import mimetypes
import discord
import asyncio
import random
import requests
import json

class Action(commands.GroupCog):
    """Send an action to other members of the server with hugs, kisses, etc."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Utility Commands

    def purrbotApi(self, topic, mincount:int, maxcount:int, gifImg, filetype):
        url = "https://purrbot.site/img/sfw/{2}/{0}/{2}_{1}.{3}".format(gifImg, format(random.randint(mincount, maxcount), '03'), topic, filetype)

        # Immediately return generated url whether the link is a real image or not
        return url

        # Check for file integrity, fallback to online API
        # Removing bc load times take too long

        # status_code = self.checkAlive(url)

        # if status_code == False:
        #     reqdata = requests.get("https://purrbot.site/api/img/sfw/{0}/{1}".format(topic,gifImg)).json()
        #     return reqdata["link"]
        # else:
        #     return status_code

    def checkAlive(self, url):
        meta = urlopen(url).info()
        if "image" in meta["content-type"]:
            return url
        else:
            return url

    async def buildEmbed(self, ctx, descriptor, imgUrl, text=None, custom=None):
        if text == None:
            desc = ""
        else:
            desc = "**{0}** gives **{1}** a {2}".format(ctx.author.mention, text, descriptor)
        if custom != None:
            desc = custom
        botcolor = await ctx.embed_colour()
        e = discord.Embed(color=botcolor, description=desc)
        e.set_image(url=imgUrl)
        # e.set_footer(text="Made with Purrbot API\u2002💌")
        return e


    # Bot Commands
 
    @commands.command(name="action", aliases=["loveplay", "lp"])
    async def action(self, ctx, action, description, *, user):
        """Send a custom lovely reaction to someone!

        Type  **`[p]help Action`**  to see built-in reactions.

        **`action`**  :  A sfw gif action from [Purrbot Image API](https://docs.purrbot.site/api/)
        **`description`**  :  @you gives @user a *"description"* (quotes if multi-word)"""
        src = self.purrbotApi(action, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, description, src, user)
        await ctx.send(embed=e)
 
    @commands.hybrid_command(name="angry")
    async def angry(self, ctx, *, user):
        """Send a angry face"""
        imgtype = "angry"
        desc = "angry face <a:AnimeAngry:1181309512448217098>"
        src = self.purrbotApi(imgtype, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)

    @commands.hybrid_command(name="blush")
    async def blush(self, ctx, *, user):
        """Send a blush"""
        imgtype = "blush"
        desc = "blush <a:AnimeBlush:1181309413034819665>"
        src = self.purrbotApi(imgtype, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)

    @commands.hybrid_command(name="comfy")
    async def comfy(self, ctx):
        """Get comfy"""
        imgtype = "comfy"
        desc = "**{0}** is comfy".format(ctx.author.mention)
        src = self.purrbotApi(imgtype, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, "", src, None, desc)
        await ctx.send(embed=e)
    
    @commands.hybrid_command(name="cry", aliases=["sob"])
    async def cry(self, ctx):
        """Have a little cry"""
        imgtype = "cry"
        desc = "**{0}** is crying".format(ctx.author.mention)
        req = requests.get("https://nekos.best/api/v2/cry?amount=1").json()
        src = req["results"][0]["url"]
        e = await self.buildEmbed(ctx, "", src, None, desc)
        await ctx.send(embed=e)

    @commands.hybrid_command(name="cuddle", aliases=["snuggle"])
    async def cuddle(self, ctx, *, user):
        """Send a cuddle"""
        imgtype = "cuddle"
        desc = "cuddle <a:AnimeCuddle:1181307102560534659>"
        src = self.purrbotApi(imgtype, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)

    @commands.hybrid_command(name="dance")
    async def dance(self, ctx, *, user):
        """Send a dance"""
        imgtype = "dance"
        desc = "dance <a:AnimeDance:1181309079948361888>"
        src = self.purrbotApi(imgtype, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="feed", aliases=["cookie"])
    async def feed(self, ctx, *, user):
        """Send some food/cookie"""
        imgtype = "feed"
        desc = "yummy cookie"
        src = self.purrbotApi(imgtype, 1, 18, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)

    @commands.hybrid_command(name="happy")
    async def happy(self, ctx):
        """Don't worry, be happy"""
        imgtype = "happy"
        desc = "**{0}** is happy".format(ctx.author.mention)
        req = requests.get("https://nekos.best/api/v2/happy?amount=1").json()
        src = req["results"][0]["url"]
        e = await self.buildEmbed(ctx, "", src, None, desc)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="hugs", aliases=["hug"])
    async def hug(self, ctx, *, user):
        """Send a hug"""
        desc = "hug"
        src = self.purrbotApi(desc, 1, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="kiss")
    async def kiss(self, ctx, *, user):
        """Send a kiss"""
        desc = "kiss"
        src = self.purrbotApi(desc, 1, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="lick")
    async def lick(self, ctx, *, user):
        """Send a lick"""
        desc = "lick"
        src = self.purrbotApi(desc, 1, 16, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="nom", aliases=["bite"])
    async def nom(self, ctx, *, user):
        """Send a nom
        
        The old command for feeding a user has moved to `[p]feed`"""
        desc = "bite"
        src = self.purrbotApi(desc, 1, 24, "gif", "gif")
        e = await self.buildEmbed(ctx, "yummy nom <a:vampynom:1181294862599987360>", src, user)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="pat")
    async def pat(self, ctx, *, user):
        """Send a pat"""
        desc = "pat"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="poke")
    async def poke(self, ctx, *, user):
        """Send a poke"""
        desc = "poke"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.hybrid_command(name="slap")
    async def slap(self, ctx, *, user):
        """Send a slap"""
        desc = "slap"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)

    # @commands.hybrid_command(name="neko")
    # async def neko(self, ctx, *, user):
    #     """Send a neko"""
    #     desc = "neko"
    #     src = self.purrbotApi(desc, 1, 20, "gif", "gif")
    #     e = await self.buildEmbed(ctx, desc, src, user)
    #     await ctx.send(embed=e)
        
    # @commands.hybrid_command(name="yuri")
    # @commands.is_nsfw()
    # async def yuri(self, ctx, *, user):
    #     """Send a yuri"""
    #     desc = "yuri"
    #     req = requests.get("https://purrbot.site/api/img/nsfw/yuri/gif").json()
    #     src = req["link"]
    #     e = await self.buildEmbed(ctx, desc, src, user)
    #     await ctx.send(embed=e)