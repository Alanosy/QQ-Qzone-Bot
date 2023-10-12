from nonebot.adapters import Bot, Event
from nonebot import on_request
from time import sleep
import json
friend_add_ = on_request(priority=100)
@friend_add_.handle()
async def friend_add_handle(bot: Bot, event: Event):
    if str(event.get_event_name()) == "request.friend":
        num = event.json()
        num = json.loads(num)
        await bot.call_api('set_friend_add_request', flag=num['flag'], approve=True)  
        sleep(3)
        message = '欢迎新朋友！'  
        await bot.call_api('send_private_msg', user_id=num['user_id'], message=message)
        lines = [
            "投稿使用说明",
            "首先发送'投稿'二字开启投稿状态，之后就可以发送您的投稿信息，当你写完投稿信息后，发送‘投稿结束’",

            "以下为投稿案例：",
            "投稿",
            "这是内容消息1",
            "这是内容消息2",
            "这是内容消息3",
            "投稿结束"

            "这样就可以完成投稿"
        ]

        message = '\n'.join(lines)

        await bot.call_api('send_private_msg', user_id=num['user_id'], message=message)
