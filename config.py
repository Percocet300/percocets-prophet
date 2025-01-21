import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OWNER_ID = int(os.getenv('OWNER_ID', '219982556446195713'))  # Fallback to your ID if env var is missing
COMMAND_PREFIX = '!'
