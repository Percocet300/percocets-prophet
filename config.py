import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OWNER_ID = int(os.getenv('OWNER_ID'))  # Your Discord User ID
COMMAND_PREFIX = '!'
