from image_studio_bot import ImageStudioBot
from video_studio_bot import VideoCreatorBot
from env import TELEGRAM_BOT_TOKEN, REPLICATE_API_TOKEN


# bot = ImageStudioBot(TELEGRAM_BOT_TOKEN, REPLICATE_API_TOKEN)
# bot.run()

bot = VideoCreatorBot(TELEGRAM_BOT_TOKEN, REPLICATE_API_TOKEN)

bot.run()
