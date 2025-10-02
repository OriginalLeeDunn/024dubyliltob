#!/usr/bin/env python3
"""
Main entry point for the Lilybud420 bot.
This module handles bot initialization and startup.
"""

import asyncio
import os
import sys
import logging
from lilybud420 import RadioBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot."""
    try:
        # Get bot credentials from environment variables
        bot_token = os.getenv('HIGHRISE_BOT_TOKEN')
        room_id = os.getenv('HIGHRISE_ROOM_ID')
        api_key = os.getenv('HIGHRISE_API_KEY')
        
        if not bot_token:
            logger.error("HIGHRISE_BOT_TOKEN environment variable is required")
            sys.exit(1)
            
        if not room_id:
            logger.error("HIGHRISE_ROOM_ID environment variable is required")
            sys.exit(1)
            
        logger.info("Starting Lilybud420 bot...")
        logger.info(f"Room ID: {room_id}")
        
        # Set API key if provided (will be used by the bot when it starts)
        if api_key:
            logger.info("API key configured for web API features")
        
        # Start the bot using the Highrise SDK command
        # The bot class is RadioBot in lilybud420.py
        import subprocess
        cmd = ['highrise', 'lilybud420:RadioBot', room_id, bot_token]
        logger.info(f"Executing: {' '.join(cmd)}")
        
        # Run the bot
        result = subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
