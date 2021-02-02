from Bot import MyBot
from boto.s3.connection import S3Connection
import os

bot = MyBot()
bot.run(S3Connection(os.environ['token']))
