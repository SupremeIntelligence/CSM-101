import discord

def check_send_permission(member: discord.member, channel: discord.abc.GuildChannel):
    perms = channel.permissions_for(member)
    if perms.view_channel and not member.bot:
        #print(f"{member.display_name} ({member.id})")
        return True
    else:
        return False

def get_channel_members(guild: discord.Guild, channel: discord.abc.GuildChannel):
    #print(f"Список участников канала {channel.name}:")
    if channel is None:
        return []
    elif isinstance(channel, discord.TextChannel):
        return [member for member in channel.members if check_send_permission(member, channel)]
    elif isinstance(channel, discord.VoiceChannel):
        return channel.members #доделать
    
def save(data: discord.member):
    pass



class UserStats:
    def __init__():
        pass


    
