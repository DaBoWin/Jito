import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.constants import ParseMode
import asyncio
from datetime import datetime, timedelta
import os
import json
import re
import sqlite3

conn = sqlite3.connect('instock_notifications.db')  # For in-memory DB, replace with 'notifications.db' for a file-based DB
c = conn.cursor()

# Create a table to store message information
c.execute('''
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_url TEXT,
    message_id INTEGER,
    message TEXT
)
''')
conn.commit()

async def load_config(filename='config.json'):
    # 获取当前工作目录
    current_dir = os.getcwd()
    # 拼接当前目录下的配置文件路径
    config_path = os.path.join(current_dir, filename)

    # 打开并读取 config.json
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def check_stock(url, out_of_stock_text):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_text = await response.text()
                soup = BeautifulSoup(response_text, 'html.parser')
                if out_of_stock_text not in soup.get_text():
                    return True
                else:
                    return False
    except Exception as e:
        print(f"检查库存时出错: {e}")
        return False

# Markdown 需要转义的特殊字符
def escape_markdown(text):
    return re.sub(r'([_*[\]()])', r'\\\1', text)

async def send_notification(config, merchant, stock):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    title = f"{merchant['name']}-{stock['title']}"
    tag = escape_markdown(merchant['tag'])
    review = escape_markdown(merchant['review_content'])
    url = stock['url']
    price = escape_markdown(stock['price'])
    hardware_info = escape_markdown(stock['hardware_info'])
    stock_url_text = stock['stock_url_text']
    # 对 URL 中需要转义的字符进行转义
    escaped_url = f"[{escape_markdown(stock_url_text)}]({url})"
    current_time = escape_markdown(current_time)

    # 构建优惠信息部分
    coupon_info = ""
    if merchant.get('coupon_monthly'):
        coupon_info += f"Monthly - Use coupon code `{merchant['coupon_monthly']}`\n"
    if merchant.get('coupon_annual'):
        coupon_info += f"Annual - Use coupon code `{merchant['coupon_annual']}`\n"


    message = (
        f"{title}\n"
        f"{tag}\n"
        f"{review}\n\n"
        f"{hardware_info}\n"
        f"{coupon_info}\n"
        f"Price: {price}\n"
        "Stock: 有\n"
        f"{escaped_url}\n\n"
        f"{current_time}"
    )

    bot = Bot(token=config['telegram_token'])
    try:
        sent_message = await bot.send_message(
            chat_id=config['telegram_chat_id'],
            text= message,
            parse_mode=ParseMode.MARKDOWN
        )

        message_id = sent_message.message_id
        c.execute('''
        SELECT id FROM notifications WHERE stock_url = ?
        ''', (url,))

        record = c.fetchone()

        if record:
            c.execute('''
            UPDATE notifications
            SET message_id = ?, message = ?
            WHERE stock_url = ?
            ''', (message_id, message, url))
            print(f"Record with stock_url {url} has been updated.")
        else:
            c.execute('''
            INSERT INTO notifications (stock_url, message_id, message)
            VALUES (?, ?, ?)
            ''', (url, message_id, message))
            print(f"New record with stock_url {url} has been inserted.")

        conn.commit()
        print(f"发送成功")
    except Exception as e:
        print(f"Error: {e}")

async def edit_message(config, url):
    bot = Bot(token=config['telegram_token'])
    try:
        c.execute('''
        SELECT message, message_id FROM notifications WHERE stock_url = ?
        ''', (url,))

        # Fetch the result
        record = c.fetchone()

        if record:
            message, message_id = record
            updated_message = message.replace("Stock: 有", "Stock: 无")

            await bot.edit_message_text(
                message_id=message_id,
                text=updated_message,
                parse_mode=ParseMode.MARKDOWN
            )
            print(f"更新成功")
            c.execute('''
            DELETE FROM notifications WHERE stock_url = ?
            ''', (url,))

            conn.commit()
        else:
            print("No message found with this stock_url.")
        
    except Exception as e:
        print(f"Error: {e}")


async def main():
    config = await load_config()
    check_interval = config.get('check_interval', 600)
    cooldown_period = config.get('cooldown_period', 86400)

    merchant_status = {}

    while True:
        for merchant in config['merchants']:
            print(f"开始检查商家: {merchant['name']}")
            out_of_stock_text = merchant.get('out_of_stock_text', '缺货')
            for stock in merchant['stock_urls']:
                url = stock['url']
                print(f"开始检查url: {url}")
                if merchant_status.get(merchant['name'], {}).get(url, {'in_stock': False})['in_stock']:
                    # 继续等待冷却时间
                    if datetime.now() < merchant_status[merchant['name']]['next_check_time']:
                        print(f"冷却中")
                        continue

                in_stock = await check_stock(url, out_of_stock_text)
                print(f"开始检查url: {in_stock}")

                if in_stock and not merchant_status.get(merchant['name'], {}).get(url, {'in_stock': False})['in_stock']:
                    print(f"有库存")
                    await send_notification(config, merchant, stock)
                    merchant_status.setdefault(merchant['name'], {})[url] = {'in_stock': True}
                    merchant_status[merchant['name']]['next_check_time'] = datetime.now() + timedelta(seconds=cooldown_period)
                elif not in_stock:
                    print(f"没有库存")
                    await edit_message(config, url)
                    merchant_status.setdefault(merchant['name'], {})[url] = {'in_stock': False}
                    merchant_status[merchant['name']]['next_check_time'] = datetime.now() + timedelta(seconds=check_interval)
            print(f"结束检查商家: {merchant['name']}")
        await asyncio.sleep(check_interval)  # 使用异步的 sleep

if __name__ == '__main__':
    asyncio.run(main())
