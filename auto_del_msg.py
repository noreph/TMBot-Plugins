from client.utils import OnScheduler
from client.config import DATADIR, logger
from client.app import client as app
from pyrogram import enums

import os, json
import asyncio
from datetime import datetime 

config = f"{DATADIR}/autodelmsg.json"
if not os.path.exists(config):
    conf = '{"cron": "*/30 * * * *","intervals": 1,"types": ["BOT","GROUP","SUPERGROUP","Discussion"]}'
    with open(config,"w") as f:
        json.dump(json.loads(conf), f, indent=4)

with open(config,"r") as f:
    conf = json.load(f)

cron = conf["cron"]
intervals = conf["intervals"]
types = conf["types"]
ChatType = []

for i in types:
    if i == "BOT":
        ChatType.append(enums.ChatType.BOT)
    elif i == "GROUP":
        ChatType.append(enums.ChatType.GROUP)
    elif i == "SUPERGROUP":
        ChatType.append(enums.ChatType.SUPERGROUP)
    elif i == "CHANNEL":
        ChatType.append(enums.ChatType.CHANNEL)
    elif i == "PRIVATE":
        ChatType.append(enums.ChatType.PRIVATE)
    elif i == "Discussion":
        ChatType.append('Discussion')

doc = f"""默认每 30 分钟进行检查一次 1 天以上在机器人、群组发过的消息并删除。
如需更改默认设定，请修改配置文件： `{config}`

配置文件参数说明：
cron：定时检查
intervals：消息间隔时间，单位为天
types：对话框类型，机器人为 BOT、群组为 GROUP、超级群组为 SUPERGROUP、频道为 CHANNEL、私聊为 PRIVATE、频道评论区为 Discussion
"""

@OnScheduler(cron=cron, help="定时删除信息", doc=doc)
async def handler():
    async def delmsg(chat_id):
        async for message in app.search_messages(chat_id, from_user="me"):
            if (datetime.now() - message.date).days > 1:
                if not message.service:
                    try:
                        if message.text or message.caption:
                            await message.edit_text('ㅤ')
                    except:
                        pass
                    await message.delete()
                    logger.info(f"delete message: {message.id}")
            await asyncio.sleep(3)

    async for dialog in app.get_dialogs():
        try:
            if 'Discussion' in ChatType:
                if dialog.chat.type == enums.ChatType.CHANNEL:
                    chat = await app.get_chat(dialog.chat.id)
                    if chat.linked_chat:
                        await delmsg(chat.linked_chat.id)
        except:
            pass

        if dialog.chat.type in ChatType:
            await delmsg(dialog.chat.id)
        await asyncio.sleep(3)
