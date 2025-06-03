from __future__ import annotations
import discord
from discord.ext import commands
from logger import logger
from typing import Any
from math import ceil
import globals
import re
import json
import os
import emoji

class Soundboard(commands.Cog):
    def __init__ (self, bot: commands.Bot):
        self.bot = bot
        globals.sounds = Soundboard.load_sounds()

    #soundboard = discord.app_commands.Group(name="soundboard", description="Команды управления звуковой панелью")

    @discord.app_commands.command(name="soundboard-add-sound", description="Добавление звука в звуковую панель")
    @discord.app_commands.describe(file="Аудиофайл .mp3, .wav, .ogg")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def add_sound (self, interaction: discord.Interaction, file: discord.Attachment):
        if not file.filename.endswith((".mp3", ".wav", ".ogg")):
            await interaction.response.send_message("Поддерживаются только файлы .mp3, .wav или .ogg", ephemeral=True)
            logger.warning (f"#SOUNDBOARD: Неверный формат файла ('{file.filename}')")
            return
        MAX_FILE_SIZE_MB = 5
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
             await interaction.response.send_message(f"Размер файла превышает {MAX_FILE_SIZE_MB}МБ.", ephemeral=True)
             logger.warning(f"#SOUNDBOARD: Неверный размер файла ({file.size/(1024*1024):.2f}MB)")
             return

        modal = InputSoundModal(file)
        await interaction.response.send_modal(modal)

    @discord.app_commands.command(name="soundboard-delete-sound", description="Удаление звука из звуковой панели")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def delete_sound(self, interaction: discord.Interaction):
        if not globals.sounds:
            await interaction.response.send_message("⚠️ Звуковая панель пуста — удалять нечего.", ephemeral=True)
            return

        soundboard = SoundboardView(globals.sounds,
                                    style=discord.ButtonStyle.danger)
        embed = discord.Embed(
            title="🗑️ Удаление звука",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Нажмите на звук, который желаете удалить.")
        await interaction.response.send_message(embed=embed, view=soundboard)
        soundboard.message = await interaction.original_response()

    @discord.app_commands.command(name="soundboard", description="Вызов звуковой панели")
    async def soundboard(self, interaction: discord.Interaction):
        if not globals.sounds:
            await interaction.response.send_message("⚠️ Звуковая панель пуста.", ephemeral=True)
            return
        embed = discord.Embed(
        title="🎛️ Звуковая панель",
        color=discord.Color.blurple()
    )
        embed.set_footer(text="Нажмите 🔄 для обновления панели в случае добавления/удаления звуков или ❌ для ее закрытия. Для переключения страниц используйте ⬅️ ➡️.")

        soundboard = SoundboardView(globals.sounds)
        await interaction.response.send_message(embed=embed, view=soundboard)
        soundboard.message = await interaction.original_response()

    @staticmethod
    def save_sounds(sounds: list[dict[str, Any]], data_filename: str = globals.SOUND_DATA_FILE ) -> None:
        with open(data_filename, "w", encoding="utf-8") as file:
            json.dump(sounds, file, indent=4, ensure_ascii=False)
    @staticmethod
    def load_sounds(data_filename: str = globals.SOUND_DATA_FILE) -> list[dict[str, Any]]:
        with open(data_filename, "r", encoding="utf-8") as file:
                return json.load(file)
    @staticmethod
    def register_sound (name: str,
                        emoji: str,
                        sound_filename: str,
                        sounds: list[dict[str, Any]],
                        data_filename=globals.SOUND_DATA_FILE) -> None:
    
        data = {
            "name": name,
            "emoji": emoji,
            "filename": sound_filename
        }
        sounds.append(data)
        Soundboard.save_sounds(sounds=sounds, data_filename=data_filename)
        
async def setup (bot: commands.Bot):
    await bot.add_cog(Soundboard(bot))
    logger.info ("Модуль звуковой панели загружен.")
        
class InputSoundModal(discord.ui.Modal):
    def __init__(self, file: discord.Attachment):
        super().__init__(title="Добавление звука",
                        custom_id="InputSoundModal")
        self.file = file
        self.sound_name = discord.ui.TextInput(
            label="Название звука",
            placeholder="Например: смешной звук",
            max_length=9,
            min_length=1,
            style=discord.TextStyle.short,
            required=True
        )
        self.sound_emoji = discord.ui.TextInput(
            label="Эмодзи звука",
            placeholder="Например: 🤖",
            max_length=2,
            min_length=1,
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.sound_name)
        self.add_item(self.sound_emoji)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        name = self.sound_name.value
        emoji = self.sound_emoji.value

        safe_name = re.sub(r'[\\/*?:"<>|]', "_", name)
        
        if any(sound["name"].lower() == safe_name.lower() for sound in globals.sounds):
            logger.warning(f"#SOUNDBOARD: Звук с названием {safe_name} уже существует.")
            message = await interaction.followup.send(content=f"Звук с названием **{safe_name}** уже существует. Пожалуйста, выберите другое имя.")
            await message.delete(delay=15)
            return

        if not self.is_valid_emoji(emoji):
            message = await interaction.followup.send("Неверный эмодзи. Введите другой.", ephemeral=True)
            await message.delete(delay=15)
            return
        
        extension = self.file.filename.rsplit('.', 1)[-1].lower()

        filename = f"{globals.SOUNDBOARD_DIR}/{safe_name}.{extension}"
        
        await self.file.save(fp=filename)
        sound_filename = f"{safe_name}.{extension}"
        Soundboard.register_sound(name=safe_name,
                       emoji=emoji, 
                       sound_filename=sound_filename, 
                       sounds=globals.sounds,
                       data_filename=globals.SOUND_DATA_FILE)

        logger.debug (f"#SOUNDBOARD: Файл '{filename}' сохранен.")
        embed = discord.Embed (
            title=f"Звук **{name}** успешно добавлен в звуковую панель!",
            color=discord.Color.blurple()
        )

        avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_author(name=interaction.user.display_name, icon_url=avatar_url)
        embed.set_footer(text="Панель управления звуками")
        
        logger.info (f"#SOUNDBOARD: Пользователь {interaction.user.display_name} добавил звук '{safe_name}'.")
        message = await interaction.followup.send("Mercher AI думает...")
        await message.delete(delay=0.1)
        await interaction.channel.send(embed=embed)
        self.stop()

    def is_valid_emoji(self, emoji_str: str) -> bool:
        return emoji.is_emoji(emoji_str)

    async def on_error (self, interaction: discord.Interaction, error: Exception):
        message = "Произошла ошибка в процессе добавления звука."
        logger.error (f"Soundboard InputSoundModal error: {error}")
        try:
            message = await interaction.followup.send(message, ephemeral=True)
            await message.delete(delay=15)
        except discord.InteractionResponded:
            await interaction.edit_original_response(content=message)
        self.stop()
    
def _pad_str (text: str, length: int, fillchar: str = ' ') -> str:
    if len(text) < length:
        return fillchar * (length-len(text)) + text
    return text
    
class ConfirmView (discord.ui.View):
        def __init__ (self,
                      sounds: list[dict[str, Any]],
                      sound_id: int, 
                      message: discord.Message | None = None
            ):
            super().__init__(timeout=20)
            self.message = message
            confirm_button = discord.ui.Button (
                style=discord.ButtonStyle.danger,
                label="Удалить",
                custom_id="confirm_deletion_button",
            )
            
            confirm_button.callback = self.confirm_button_callback(sounds, sound_id)
            self.add_item(confirm_button)

            cancel_button = discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Отменить",
                custom_id="cancel_deletion_button"
            )
            cancel_button.callback = self.cancel_button_callback()
            self.add_item(cancel_button)
        
        def confirm_button_callback(self, sounds: list[dict[str, Any]], sound_id: int):
            async def callback (interaction: discord.Interaction):
                sound = sounds.pop(sound_id)
                delete_path = f"{globals.SOUNDBOARD_DIR}/{sound['filename']}"
                if os.path.exists(delete_path):
                    os.remove(delete_path)
                    logger.debug(f"#SOUNDBOARD: Файл '{delete_path}' успешно удален.")

                Soundboard.save_sounds(sounds)
                embed = discord.Embed (
                    title=f"🗑️ Звук **{sound['name']}** успешно удален из звуковой панели!",
                    color=discord.Color.blurple()
                    )
                avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed.set_author(name=interaction.user.display_name, icon_url=avatar_url)

                embed.set_footer(text="Панель управления звуками")

                await interaction.response.edit_message(content=None, embed=embed, view=None)
                logger.info (f"#SOUNDBOARD: Пользователь {interaction.user.display_name} удалил звук '{sound['name']}'.")
                self.stop()
            return callback
        
        def cancel_button_callback (self):
            async def callback(interaction: discord.Interaction):
                self.stop()
                await interaction.message.delete()
            return callback
        
        async def on_error(self, interaction: discord.Interaction, error, item):
            await interaction.response.edit_message(content="Произошла ошибка при взаимодействии с панелью подтверждения удаления звука.", delete_after=60)
            logger.error(f"#SOUNDBOARD: Ошибка при взаимодействии с панелью подтверждения удаления звука: {error}. Item: {str(item)}.")
        
        async def on_timeout(self):
            self.stop()
            await self.message.delete()

class SoundboardView (discord.ui.View):
    def __init__ (self, sounds: list[dict[str, Any]],
                 style: discord.ButtonStyle = discord.ButtonStyle.secondary,
                 message: discord.Message | None = None,
                 ):
        self.sounds = sounds
        self.message = message
        self.style = style
        self.callback_factory = None
        if style == discord.ButtonStyle.secondary:
            timeout = 300
            self.callback_factory = self.sound_callback
        else:
            timeout = 40
            self.callback_factory = self.delete_callback(self.sounds)
        super().__init__(timeout=timeout)
        
        self.page = 0
        self.BUTTONS_PER_PAGE = globals.SOUNDBOARD_BUTTONS_PER_PAGE
        self.max_pages = ceil(len(self.sounds) / self.BUTTONS_PER_PAGE)
        self.voice_channel = None
        self._set_buttons()

    def _set_buttons(self):
        start = self.page * self.BUTTONS_PER_PAGE
        end = start + self.BUTTONS_PER_PAGE
        for i in range(start, min(end, len(self.sounds))):
            sound = self.sounds[i]
            label = _pad_str(text=sound["name"], length=8, fillchar=" ")
            index = self.sounds.index(sound)
            button = discord.ui.Button(style=self.style,
                                            label=label,
                                            custom_id=f"{index}",
                                            emoji=sound["emoji"])
            
            button.callback = self.callback_factory(button.custom_id)
            self.add_item(button)

        if self.style == discord.ButtonStyle.secondary:
            update_button = discord.ui.Button(
                style=self.style,
                custom_id="update_button",
                emoji="🔄",
                row=4
            )
            update_button.callback = self.update_button_callback()
            self.add_item(update_button)
            
        close_button = discord.ui.Button(
            style = discord.ButtonStyle.secondary,
            custom_id="close_button",
            emoji="❌",
            row=4
        )

        close_button.callback = self.close_button_callback()
        self.add_item(close_button)

        if self.page > 0:
                prev_button = discord.ui.Button(
                    style = discord.ButtonStyle.secondary,
                    custom_id=f"prev_button{self.page}",
                    emoji="⬅️",
                    row=4
                )
                prev_button.callback = self.prev_button_callback()
                self.add_item(prev_button)

        if self.page + 1 < self.max_pages:
            next_button = discord.ui.Button(
                style = discord.ButtonStyle.secondary,
                custom_id=f"next_button{self.page}",
                emoji="➡️",
                row=4
            )
            next_button.callback = self.next_button_callback()
            self.add_item(next_button)

    def update_button_callback(self):
        async def callback (interaction: discord.Interaction):
            await interaction.response.defer()
            self.clear_items()
            self.sounds = globals.sounds
            self.max_pages = ceil(len(self.sounds) / self.BUTTONS_PER_PAGE)
            self._set_buttons()
            await interaction.edit_original_response(view=self)
            logger.debug(f"#SOUNDBOARD: Пользователь {interaction.user.display_name} обновил звуковую панель.")
        return callback

    def close_button_callback(self):
        async def callback(interaction: discord.Interaction):
            self.stop()
            await interaction.message.delete()
            logger.debug(f"#SOUNDBOARD: Пользователь {interaction.user.display_name} закрыл звуковую панель.")
        return callback

    def next_button_callback(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            self.clear_items()
            self.page += 1
            self._set_buttons()
            await interaction.edit_original_response(view=self)
            logger.debug(f"#SOUNDBOARD: Пользователь {interaction.user.display_name} переключился на страницу '{self.page}' звуковой панели.")

        return callback

    def prev_button_callback(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            self.clear_items()
            self.page -= 1
            self._set_buttons()
            await interaction.edit_original_response(view=self)
            logger.debug(f"#SOUNDBOARD: Пользователь {interaction.user.display_name} переключился на страницу '{self.page}' звуковой панели.")
            
        return callback

    def sound_callback(self, id: str):
        async def callback (interaction: discord.Interaction):
            await interaction.response.defer()
            voice_state = interaction.user.voice
            if not voice_state:
                await interaction.followup.send(content="❗ Вы не находитесь в голосовом канале!", ephemeral=True)
                return
            voice_channel = voice_state.channel
            voice_client = interaction.guild.voice_client
            if not voice_client or not voice_client.is_connected():
                voice_client = await voice_channel.connect()
            elif voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)

            sound = globals.sounds[int(id)]
            sound_path = os.path.join(globals.SOUNDBOARD_DIR, sound["filename"])
            if not os.path.exists(sound_path):
                await interaction.followup.send(content="Произошла ошибка при воспроизведении звука. Файл звука не существует.", ephemeral=True)
                logger.error (f"Файл звука {sound_path} не существует.")
                return
            
            if voice_client.is_playing():
                voice_client.stop()
            
            audio = discord.FFmpegPCMAudio(sound_path)
            voice_client.play(audio)

            self.voice_channel = voice_channel
            logger.debug(f"#SOUNDBOARD: Пользователь {interaction.user.display_name} задействовал звук {sound['name']}(ID: {id}) в звуковой панели.")
        return callback
    
    def delete_callback(self, sounds: list[dict[str, Any]]):
        def factory(id: str):
            async def callback (interaction: discord.Interaction):
                sound_id = int(id)
                sound = sounds[sound_id]
                embed = discord.Embed (
                    title=f"🗑️ Подтвердите удаление звука **{sound['name']}**."
                )
                embed.set_footer(text="Панель управления звуками")

                confirm_view = ConfirmView(sounds=sounds, sound_id=sound_id)
                await interaction.response.edit_message(embed=embed, view=confirm_view)
                confirm_view.message = await interaction.original_response()
                self.stop()
            return callback
        return factory
    
    async def on_error(self, interaction: discord.Interaction, error, item):
            await interaction.followup.send(content="Произошла ошибка при взаимодействии с звуковой панелью.", ephemeral=True)
            logger.error(f"#SOUNDBOARD: Ошибка при взаимодействии с звуковой панелью: {error}. Item: {str(item)}.")
    
    async def check_voice_channel (self) -> bool:
        if self.voice_channel is not None:
            members = [m for m in self.voice_channel.members
                        if not m.bot and m.voice and m.voice.channel == self.voice_channel
                        ]
            if members:
                return True
            else:
                return False
        else: 
            return False
          
    async def on_timeout(self):
        if self.style == discord.ButtonStyle.secondary and await self.check_voice_channel():
            embed = discord.Embed(
                title="🎛️ Звуковая панель",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="Нажмите 🔄 для обновления панели в случае добавления/удаления звуков или ❌ для ее закрытия. Для переключения страниц используйте ⬅️ ➡️.")

            new_soundboard = SoundboardView(self.sounds)
            new_soundboard.page = self.page
            new_soundboard.voice_channel = self.voice_channel
            new_soundboard.message = await self.message.channel.send(embed=embed, view=new_soundboard, silent=True)
        self.stop()
        await self.message.delete()
    
    