import discord
import user
import json
from logger import logger
from globals import USER_DATA_FILE

def check_send_permission(member: discord.member, channel: discord.abc.GuildChannel):
    perms = channel.permissions_for(member)
    if perms.view_channel and not member.bot:
        #print(f"{member.display_name} ({member.id})")
        return True
    else:
        return False

def get_channel_members(bot, guild_id: int, channel_id: int):
    #print(f"Список участников канала {channel.name}:")
    guild = bot.get_guild(guild_id)
    channel = bot.get_channel(channel_id)
    if guild is None:
        logger.critical("Сервер не найден")
        return []
    if channel is None:
        logger.critical("Канал не найден")
        return []
    elif isinstance(channel, discord.TextChannel):
        return [member for member in channel.members if check_send_permission(member, channel)]
    elif isinstance(channel, discord.VoiceChannel):
        return channel.members #доделать
    
def get_users(members=list[discord.Member]):
    users = {}
    for member in members:
        users[member.id] = user.User(member.id, member.display_name, 0)
    return users

def save_users(users: dict[int, user.User], filename=USER_DATA_FILE):
    with open (filename,"w", encoding="utf-8") as file:
        json.dump([user.to_dict() for user in users.values()], file, indent=4, ensure_ascii=False)

def load_users(filename=USER_DATA_FILE):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return {int(obj["id"]): user.User.from_dict(obj) for obj in data}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def sync_users(bot, guild_id: int, channel_id: int, users: dict[int, user.User]):
    guild = bot.get_guild(guild_id)
    channel = bot.get_channel(channel_id)
    if guild is None:
        logger.critical("Сервер не найден")
        return
    if channel is None:
        logger.critical("Канал не найден")
        return
    for member in get_channel_members(bot, guild_id, channel_id):
        if member.id not in users:
            users[member.id] = user.User(member.id, member.display_name)
    save_users(users, USER_DATA_FILE)
    
