from .rolepersist import RolePersist

__red_end_user_data_statement__ = "This cog stores the roles of users when they leave the server. These are used to re-assign roles when they return."


def setup(bot):
    bot.add_cog(RolePersist(bot))
