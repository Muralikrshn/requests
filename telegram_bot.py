import asyncio
import csv
from telegram import Bot

# Your bot token from BotFather
BOT_TOKEN = '8331772051:AAG5KbiP05GIBsxs98yYG851rkN7Tz3aOc4'

# Your channel ID (private channels start with -100)
CHANNEL_ID = '-1002797016897'

async def main():
    bot = Bot(token=BOT_TOKEN)
    
    message = "🔥 New Products Alert!\n\n"
    
    # Open the CSV and read first 5 products
    with open('dummy_products.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # Assumes header row exists: Name,Price,Image
        for i, row in enumerate(reader):
          if i < 20:  # skip first 20 products
                continue
          if i >= 30:  # stop after 30 products
              break
          message += f"{i+1}. {row['Name']} - {row['Price']}\nImage: {row['Image']}\n\n"
    
    # Send the message to Telegram
    await bot.send_message(chat_id=CHANNEL_ID, text=message)
    
    # Close bot session
    # await bot.close()

# Run the async function
asyncio.run(main())
