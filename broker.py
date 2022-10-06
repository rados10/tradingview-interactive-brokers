import redis, json
from ib_insync import *
import asyncio, time, random
from discord_webhook import DiscordWebhook

# connect to Interactive Brokers 
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# connect to Redis and subscribe to tradingview messages
r = redis.Redis(host='localhost', port=6379, db=0)
p = r.pubsub()
p.subscribe('tradingview')

async def check_messages():
    print(f"{time.time()} - checking for tradingview webhook messages")
    try:
        message = p.get_message()
        if message is not None and message['type'] == 'message':
            print(message)

            message_data = json.loads(message['data'])

            stock = Stock(message_data['ticker'], 'SMART', 'USD')
            # order = MarketOrder(message_data['strategy']['order_action'], message_data['strategy']['order_contracts'])
            order = LimitOrder(message_data['strategy']['order_action'], message_data['strategy']['order_contracts'], message_data['strategy']['order_price'])
            trade = ib.placeOrder(stock, order)
            #send message to discord
            webhook = DiscordWebhook(url='https://discordapp.com/api/webhooks/1027545477601824859/Oo2Tq3WfD0OFzJPpNqLN7LzP3-kGxg9ejAn2VNkH7c7RbK-kVBJDUTUQZ0cPxWW1BnYF', content=f"Order placed: {trade}")
            response = webhook.execute()

    except Exception as e:
        print(f"{time.time()} - error: {e}")
        #send a message to discord
        webhook = DiscordWebhook(url='https://discordapp.com/api/webhooks/1027544514384121906/-JcURvMg64pGMQOWRuHovYM1ybqY_0QhwOBluDxxeVjjseeXQD65gRu46m08sG9oV_4F', content=f"TRADE FAILED with Error: {e} for message {message}")
        response = webhook.execute()
        pass

async def run_periodically(interval, periodic_function):
    while True:
        await asyncio.gather(asyncio.sleep(interval), periodic_function())

asyncio.run(run_periodically(1, check_messages))

ib.run()