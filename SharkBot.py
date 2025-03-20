import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file!")

# Set up bot with command prefix
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store pinned messages per channel
pinned_messages = {}

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'Logged in as {bot.user}')
    print("Registered Commands:", [cmd.name for cmd in bot.commands])  # Debugging: Show available commands

@bot.command(name="pin")
async def pin(ctx, *, content: str):
    """Pins a message and keeps it at the bottom"""
    if not content:
        await ctx.send("Usage: `!pin <message>`")
        return

    # Remove the previous pinned message if it exists
    if ctx.channel.id in pinned_messages:
        try:
            old_msg = await ctx.channel.fetch_message(pinned_messages[ctx.channel.id])
            await old_msg.delete()
        except discord.NotFound:
            pass  # Message already deleted

    # Send new pinned message
    pinned_msg = await ctx.send(f"📌 {content}")

    # Store the new pinned message ID
    pinned_messages[ctx.channel.id] = pinned_msg.id

@bot.command(name="stop")
async def stop(ctx):
    """Stops the bot from reposting the pinned message"""
    print("!stop command received")  # Debug message

    if ctx.channel.id in pinned_messages:
        del pinned_messages[ctx.channel.id]  # Remove tracking for the channel
        await ctx.send("🛑 The bot will no longer repost the pinned message.", delete_after=3)
    else:
        await ctx.send("❌ No pinned message is being tracked.", delete_after=3)

@bot.event
async def on_message(message):
    """Ensures the pinned message stays at the bottom"""
    if message.author == bot.user:
        return

    await bot.process_commands(message)  # Ensures commands work properly

    if message.channel.id in pinned_messages:
        try:
            pinned_msg = await message.channel.fetch_message(pinned_messages[message.channel.id])
            new_pinned_msg = await message.channel.send(pinned_msg.content)
            await pinned_msg.delete()
            pinned_messages[message.channel.id] = new_pinned_msg.id
        except discord.NotFound:
            pass  # Pinned message no longer exists

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)
