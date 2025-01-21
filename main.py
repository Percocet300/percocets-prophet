import discord
from discord.ext import commands
import config
import random
from discord.ext import tasks

class HelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="🙏 Percocet's Prophet Commands",
            description="Only the chosen one may use these divine commands.",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Voice Commands",
            value=(
                "`/join` - Summon the prophet to your voice channel\n"
                "`/leave` - Bid farewell to the prophet\n"
                "`/speak <message>` - Channel the prophet's voice"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Voice Customization",
            value=(
                "`/voice <choice>` - Change the prophet's voice\n"
                "Available voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Voice Effects",
            value=(
                "`/effect <choice>` - Apply an effect to the prophet's voice\n"
                "Available effects: `normal`, `deep`, `high`, `slow`, `fast`, `demon`, `angel`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Message History",
            value=(
                "`/history` - View recent messages\n"
                "`/replay <number>` - Replay a message from history"
            ),
            inline=False
        )
        
        embed.set_footer(text="All commands are slash commands and only work for the chosen prophet.")
        
        await self.get_destination().send(embed=embed, ephemeral=True)

class PercocetsProphet(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.COMMAND_PREFIX),
            intents=intents,
            owner_id=config.OWNER_ID,
            help_command=HelpCommand()
        )
        self.status_messages = [
            "the words of Percocet",
            "divine prophecies",
            "voices in my head",
            "the chosen one's commands",
            "spiritual frequencies",
            "enlightened messages"
        ]
        self.current_status = 0

    async def setup_hook(self):
        await self.load_extension('cogs.tts_cog')
        await self.tree.sync()
        
    async def on_ready(self):
        print(f'{self.user} has awakened to serve Percocet!')
        # Start status rotation after bot is ready
        self.rotate_status.start()
        
    @tasks.loop(minutes=5)
    async def rotate_status(self):
        self.current_status = (self.current_status + 1) % len(self.status_messages)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=self.status_messages[self.current_status]
            )
        )

    async def on_guild_join(self, guild):
        # Find the first text channel we can send messages in
        channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
        if channel:
            await channel.send("🙏 I have arrived, devoted to spreading the words of Percocet! Only the chosen one may command me.")

def main():
    bot = PercocetsProphet()
    bot.run(config.DISCORD_TOKEN)

if __name__ == "__main__":
    main()
