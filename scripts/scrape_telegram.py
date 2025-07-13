import os
import asyncio
import json
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv
import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
# PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER') # Optional, if you want to use phone number for login

# Ensure API_ID and API_HASH are available
if not API_ID or not API_HASH:
    logger.error("TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env file. Please set them.")
    exit(1)

# --- Data Lake Configuration ---
RAW_DATA_PATH = os.path.join(os.getcwd(), 'data', 'raw')
RAW_MESSAGES_PATH = os.path.join(RAW_DATA_PATH, 'telegram_messages')
RAW_IMAGES_PATH = os.path.join(RAW_DATA_PATH, 'telegram_images')

os.makedirs(RAW_MESSAGES_PATH, exist_ok=True)
os.makedirs(RAW_IMAGES_PATH, exist_ok=True)

# --- Telegram Channels to Scrape ---
# You can add more channels from https://et.tgstat.com/medicine
TELEGRAM_CHANNELS = [
    'https://t.me/chemed_chem_med', # Example: Chemed Telegram Channel
    'https://t.me/lobelia4cosmetics',
    'https://t.me/tikvahpharma',
    # Add more channels here as needed for your analysis
]

# --- Async Main Function ---
async def scrape_channel(client, channel_entity):
    channel_name = channel_entity.username if channel_entity.username else str(channel_entity.id)
    logger.info(f"Starting scraping for channel: {channel_name} (ID: {channel_entity.id})")

    messages_data = []
    image_count = 0
    message_count = 0

    async for message in client.iter_messages(channel_entity, limit=None): # Use limit=None to get all messages
        message_count += 1
        msg_date_str = message.date.strftime('%Y-%m-%d')

        # --- Store Raw Message as JSON ---
        message_dict = {
            'id': message.id,
            'peer_id': message.peer_id.to_dict() if message.peer_id else None,
            'date': message.date.isoformat(),
            'message': message.message,
            'out': message.out,
            'mentioned': message.mentioned,
            'media_unread': message.media_unread,
            'silent': message.silent,
            'post': message.post,
            'from_scheduled': message.from_scheduled,
            'legacy': message.legacy,
            'edit_hide': message.edit_hide,
            'pinned': message.pinned,
            'noforwards': message.noforwards,
            'replies': message.replies.to_dict() if message.replies else None,
            'fwd_from': message.fwd_from.to_dict() if message.fwd_from else None,
            'via_bot_id': message.via_bot_id,
            'reply_to': message.reply_to.to_dict() if message.reply_to else None,
            'media': None, # Will populate if media exists
            'photo_id': None, # Store photo ID for linking
            'document_id': None, # Store document ID for linking
        }

        # --- Handle Media (Images and Documents) ---
        if message.media:
            media_path = os.path.join(RAW_IMAGES_PATH, msg_date_str, channel_name)
            os.makedirs(media_path, exist_ok=True)

            if isinstance(message.media, MessageMediaPhoto):
                file_name = f"{message.id}.jpg"
                local_file_path = os.path.join(media_path, file_name)
                try:
                    await client.download_media(message.media.photo, file=local_file_path)
                    message_dict['media'] = 'photo'
                    message_dict['photo_id'] = message.media.photo.id
                    message_dict['media_local_path'] = local_file_path
                    image_count += 1
                    logger.info(f"Downloaded image: {local_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to download photo for message {message.id} in {channel_name}: {e}")
                    message_dict['media'] = 'photo_download_failed'
            elif isinstance(message.media, MessageMediaDocument):
                # You might want to filter document types, e.g., only images
                if message.media.document.mime_type and 'image/' in message.media.document.mime_type:
                    file_ext = message.media.document.mime_type.split('/')[-1]
                    file_name = f"{message.id}.{file_ext}"
                    local_file_path = os.path.join(media_path, file_name)
                    try:
                        await client.download_media(message.media.document, file=local_file_path)
                        message_dict['media'] = 'document_image'
                        message_dict['document_id'] = message.media.document.id
                        message_dict['media_local_path'] = local_file_path
                        image_count += 1
                        logger.info(f"Downloaded document image: {local_file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to download document image for message {message.id} in {channel_name}: {e}")
                        message_dict['media'] = 'document_image_download_failed'
                else:
                    message_dict['media'] = 'document_other' # Not downloading other document types
            else:
                message_dict['media'] = 'other' # Handle other media types like video, voice etc. if needed

        messages_data.append(message_dict)

    # --- Save Messages to JSON File ---
    if messages_data:
        messages_dir = os.path.join(RAW_MESSAGES_PATH, msg_date_str) # Save all messages for a day in one file
        os.makedirs(messages_dir, exist_ok=True)
        output_file = os.path.join(messages_dir, f"{channel_name}_{msg_date_str}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved {len(messages_data)} messages from {channel_name} to {output_file}")
    else:
        logger.info(f"No messages found for channel: {channel_name}")

    logger.info(f"Finished scraping channel: {channel_name}. Total messages: {message_count}, Images downloaded: {image_count}")
    return message_count, image_count # Return for summary

async def main():
    session_name = 'telegram_scraper_session' # Session file name
    client = TelegramClient(session_name, API_ID, API_HASH)

    try:
        logger.info("Connecting to Telegram...")
        # This part handles authentication. It might ask for phone number/code/password the first time.
        # Make sure you run this script interactively the first time to authenticate.
        await client.start()
        logger.info("Connected to Telegram successfully.")

        total_messages_scraped = 0
        total_images_downloaded = 0

        for channel_url in TELEGRAM_CHANNELS:
            try:
                # Resolve channel entity (gets channel info from URL/username)
                channel_entity = await client.get_entity(channel_url)

                messages_count, images_count = await scrape_channel(client, channel_entity)
                total_messages_scraped += messages_count
                total_images_downloaded += images_count
            except Exception as e:
                logger.error(f"Error processing channel {channel_url}: {e}", exc_info=True)

        logger.info(f"--- Scraping Summary ---")
        logger.info(f"Total messages scraped: {total_messages_scraped}")
        logger.info(f"Total images downloaded: {total_images_downloaded}")

    except Exception as e:
        logger.critical(f"Fatal error during Telegram client connection or operation: {e}", exc_info=True)
    finally:
        if client.is_connected():
            await client.disconnect()
            logger.info("Disconnected from Telegram.")

if __name__ == '__main__':
    # IMPORTANT: Run this script directly from the terminal for the first time
    # to handle the authentication flow (entering phone number, code, password).
    # You'll see prompts in your terminal.
    asyncio.run(main())