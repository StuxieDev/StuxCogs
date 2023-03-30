from discord import Member, AuditLogAction, Role, Object
from typing import Set, List, Union
from redbot.core import Config, commands, checks
from redbot.core.utils import AsyncIter
import logging


log = logging.getLogger("red.stuxiedev.rolepersist")


class RolePersist(commands.Cog):
    """Makes roles persist when a user joins & leaves a server.
    Currently, when users leave servers, they wont regain their roles when rejoining. 
    This cog will store the users roles when they leave the server.
    It will then readd them when the user rejoins the server"""

    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.presence_task.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """
        Called when a Member joins or leaves a Guild
        Will add roles that were never added or removed
        :param member: the member who joined
        """
        roles_not_removed = set()

        top_role = member.guild.me.top_role

        async for entry in member.guild.audit_logs(action=AuditLogAction.member_role_update, oldest_first=True):
            if entry.target == member:
                before_roles = self.filter_roles(top_role, entry.changes.before.roles)
                after_roles = self.filter_roles(top_role, entry.changes.after.roles)

                roles_added = after_roles - before_roles
                roles_removed = before_roles - after_roles

                roles_not_removed.update(roles_added)
                roles_not_removed.difference_update(roles_removed)

        await member.add_roles(*roles_not_removed, reason='Persisted roles')

    @staticmethod
    def filter_roles(top_role: Role, roles: List[Union[Role, Object]]) -> Set[Role]:
        """
        Filters a list of possible roles on whether they still exist
        and whether they are not above a top role
        Will return a set
        :param top_role: the top role
        :param roles: list of possible roles, each element is either a Role or Object
        :return: the filtered set of roles
        """
        filtered_roles = set()

        for role in roles:
            if isinstance(role, Role) and role < top_role:
                filtered_roles.add(role)

        return filtered_roles

