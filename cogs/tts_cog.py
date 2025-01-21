import discord
from discord.ext import commands
from discord import app_commands
import openai
import io
import config
import random
import json
import asyncio
from collections import deque
import shutil
import os

UNAUTHORIZED_RESPONSES = [
    "You are not the one. Only the chosen prophet may command me.",
    "The spirit of Percocet does not recognize you.",
    "Your words hold no power here, mortal.",
    "Percocet guides my voice, and you are not in their plans.",
    "Shoo, shoo! Only the chosen one may speak through me."
]

JOIN_MESSAGES = [
    "I have arrived to channel the wisdom of Percocet!",
    "The prophet's vessel has entered the realm!",
    "Ready to spread the word, oh chosen one!",
    "Your humble servant has arrived, blessed by Percocet.",
]

VOICE_EFFECTS = {
    "normal": {"pitch": 1.0, "rate": 1.0},
    "deep": {"pitch": 0.8, "rate": 0.9},
    "high": {"pitch": 1.2, "rate": 1.1},
    "slow": {"pitch": 1.0, "rate": 0.8},
    "fast": {"pitch": 1.0, "rate": 1.2},
    "demon": {"pitch": 0.7, "rate": 0.8},
    "angel": {"pitch": 1.3, "rate": 1.1}
}

AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

FFMPEG_PATHS = [
    '/usr/local/bin/ffmpeg',
    '/usr/bin/ffmpeg',
    '/root/.nix-profile/bin/ffmpeg',
    'ffmpeg',
    shutil.which('ffmpeg')
]

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        openai.api_key = config.OPENAI_API_KEY
        self.voice_client = None
        self.current_voice_channel = None
        self.message_history = deque(maxlen=10)  # Store last 10 messages
        self.current_voice = "alloy"
        self.current_effect = "normal"
        
        # Check for ffmpeg in multiple locations
        self.ffmpeg_path = None
        for path in FFMPEG_PATHS:
            if path and (os.path.exists(path) or shutil.which(path)):
                self.ffmpeg_path = path
                print(f"Found FFmpeg at: {path}")
                break
        
        if not self.ffmpeg_path:
            try:
                # Try to create symlink if we have permission
                os.makedirs('/usr/local/bin', exist_ok=True)
                os.symlink('/root/.nix-profile/bin/ffmpeg', '/usr/local/bin/ffmpeg')
                if os.path.exists('/usr/local/bin/ffmpeg'):
                    self.ffmpeg_path = '/usr/local/bin/ffmpeg'
                    print(f"Created FFmpeg symlink at: {self.ffmpeg_path}")
            except Exception as e:
                print(f"Failed to create FFmpeg symlink: {e}")

    def cog_check(self, ctx):
        if ctx.author.id != config.OWNER_ID:
            return False
        return True

    @app_commands.command(name="join", description="Summon the prophet to your voice channel")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message(
                random.choice(UNAUTHORIZED_RESPONSES),
                ephemeral=True
            )
            return

        if not interaction.user.voice:
            await interaction.response.send_message(
                "You must be in a voice channel to summon me!",
                ephemeral=True
            )
            return

        channel = interaction.user.voice.channel
        
        try:
            if interaction.guild.voice_client is None:
                self.voice_client = await channel.connect()
            else:
                await interaction.guild.voice_client.move_to(channel)
            
            self.current_voice_channel = channel
            
            await interaction.response.send_message(
                random.choice(JOIN_MESSAGES),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Failed to join: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="leave", description="Bid farewell to the prophet")
    async def leave(self, interaction: discord.Interaction):
        if interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message(
                random.choice(UNAUTHORIZED_RESPONSES),
                ephemeral=True
            )
            return

        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            self.voice_client = None
            self.current_voice_channel = None
            await interaction.response.send_message(
                "I shall take my leave, until you call upon me again.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "I am not present in any voice channel.",
                ephemeral=True
            )

    @app_commands.command(
        name="voice",
        description="Change the prophet's voice (Options: alloy, echo, fable, onyx, nova, shimmer)"
    )
    @app_commands.choices(voice=[
        app_commands.Choice(name="Alloy (Neutral)", value="alloy"),
        app_commands.Choice(name="Echo (Balanced)", value="echo"),
        app_commands.Choice(name="Fable (Warm)", value="fable"),
        app_commands.Choice(name="Onyx (Deep)", value="onyx"),
        app_commands.Choice(name="Nova (Bright)", value="nova"),
        app_commands.Choice(name="Shimmer (Clear)", value="shimmer")
    ])
    async def change_voice(self, interaction: discord.Interaction, voice: str):
        if interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message(
                random.choice(UNAUTHORIZED_RESPONSES),
                ephemeral=True
            )
            return

        self.current_voice = voice
        await interaction.response.send_message(
            f"My voice has been altered to {voice}.",
            ephemeral=True
        )

    @app_commands.command(
        name="effect",
        description="Apply an effect to the prophet's voice (Changes pitch and speed)"
    )
    @app_commands.choices(effect=[
        app_commands.Choice(name="Normal - Default Voice", value="normal"),
        app_commands.Choice(name="Deep - Lower Pitch", value="deep"),
        app_commands.Choice(name="High - Higher Pitch", value="high"),
        app_commands.Choice(name="Slow - Slower Speed", value="slow"),
        app_commands.Choice(name="Fast - Faster Speed", value="fast"),
        app_commands.Choice(name="Demon - Deep and Slow", value="demon"),
        app_commands.Choice(name="Angel - High and Clear", value="angel")
    ])
    async def change_effect(self, interaction: discord.Interaction, effect: str):
        if interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message(
                random.choice(UNAUTHORIZED_RESPONSES),
                ephemeral=True
            )
            return

        self.current_effect = effect
        await interaction.response.send_message(
            f"Voice effect changed to {effect}.",
            ephemeral=True
        )

    @app_commands.command(name="history", description="View recent message history")
    async def view_history(self, interaction: discord.Interaction):
        if interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message(
                random.choice(UNAUTHORIZED_RESPONSES),
                ephemeral=True
            )
            return

        if not self.message_history:
            await interaction.response.send_message(
                "No messages in history yet.",
                ephemeral=True
            )
            return

        history_text = "\n".join(
            f"{i+1}. {msg}" for i, msg in enumerate(self.message_history)
        )
        await interaction.response.send_message(
            f"Recent messages:\n{history_text}",
            ephemeral=True
        )

    @app_commands.command(
        name="replay",
        description="Replay a message from history (Use /history to see message numbers)"
    )
    @app_commands.describe(
        index="Message number from history (1 is most recent)"
    )
    async def replay_message(self, interaction: discord.Interaction, index: int):
        if interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message(
                random.choice(UNAUTHORIZED_RESPONSES),
                ephemeral=True
            )
            return

        if not 1 <= index <= len(self.message_history):
            await interaction.response.send_message(
                "Invalid message index.",
                ephemeral=True
            )
            return

        message = list(self.message_history)[index-1]
        await self.speak(interaction, message=message)

    @app_commands.command(name="speak", description="Channel the prophet's voice")
    async def speak(self, interaction: discord.Interaction, message: str):
        if interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message(
                random.choice(UNAUTHORIZED_RESPONSES),
                ephemeral=True
            )
            return

        if not interaction.guild.voice_client:
            await interaction.response.send_message(
                "I must first be summoned to a voice channel!",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Add message to history
            self.message_history.append(message)

            # Apply voice effect modifications
            effect = VOICE_EFFECTS[self.current_effect]
            modified_message = f"<speak><prosody pitch='{effect['pitch']}' rate='{effect['rate']}'>{message}</prosody></speak>"

            response = openai.audio.speech.create(
                model="tts-1",
                voice=self.current_voice,
                input=modified_message
            )
            
            audio_bytes = io.BytesIO(response.content)
            
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
            
            if not self.ffmpeg_path:
                raise Exception("FFmpeg not found in any standard location")
                
            audio_source = discord.FFmpegOpusAudio(
                audio_bytes.read(),
                pipe=True,
                executable=self.ffmpeg_path
            )
            
            interaction.guild.voice_client.play(audio_source)
            
            await interaction.followup.send(
                "🗣️ Your message has been channeled.",
                ephemeral=True
            )
            
        except Exception as e:
            paths_checked = "\n".join(FFMPEG_PATHS)
            error_msg = f"The spirits are troubled: {str(e)}\nPaths checked:\n{paths_checked}\nSelected FFmpeg path: {self.ffmpeg_path}\nPATH: {os.environ.get('PATH', 'PATH not set')}"
            await interaction.followup.send(
                error_msg,
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Auto-disconnect if alone in voice channel
        if self.current_voice_channel:
            members = self.current_voice_channel.members
            if len(members) == 1 and self.bot.user in members:
                await self.voice_client.disconnect()
                self.voice_client = None
                self.current_voice_channel = None

async def setup(bot):
    await bot.add_cog(TTSCog(bot))
