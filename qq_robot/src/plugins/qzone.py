from nonebot.adapters import Bot, Event
from nonebot.plugin import on_message
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import time
import re
import os
import uuid
import json
import requests
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import redis
r = redis.Readis(host='localhost', port=6379, db=0)

reply = on_message(priority=100)
options = Options()
options.page_load_strategy = 'eager'
bs=webdriver.Chrome(options=options)
bs.get("https://qzone.qq.com/")
sleep(2)
bs.find_element(By.CLASS_NAME, "login_wrap").click()
sleep(1)
print("登录成功")
sleep(1)
bs.find_element(By.CLASS_NAME, "nav-list-inner").click()
sleep(3)
variables = {}
@reply.handle()
async def reply_handle(bot: Bot, event: Event):
    print("*"*20)
    print(event.get_event_name())
    print("*"*20)
    user_msg = str(event.get_message()).strip()
    if str(event.get_event_name()) == "message.private.friend":
        try:
            variables[event.get_user_id()+'_img']
        except:
            variables[event.get_user_id()+'_img'] = []
        try:
            variables[event.get_user_id()+'_state']
        except:
            variables[event.get_user_id()+'_state'] = False
        if user_msg=='投稿':
            variables[event.get_user_id()+'_state']=True
        try:
            variables[event.get_user_id()]
        except:
            variables[event.get_user_id()] = []
        # 使用正则表达式提取图片链接
        

        if variables[event.get_user_id()+'_state']:
            pattern = re.compile(r'\[CQ:image,file=[\w.-]+,url=(.+?)\]')
            matches = pattern.findall(user_msg)
            if matches:
                image_url = matches[0]  # 获取第一个匹配到的图片链接
                image_name = str(uuid.uuid4()) + '.jpg'  # 生成随机文件名

                # 发起请求下载图片
                response = requests.get(image_url)
                # 检查请求是否成功
                if response.status_code == 200:
                    # 创建img目录
                    if not os.path.exists('img'):
                        os.mkdir('img')

                    # 保存图片到本地
                    with open(os.path.join('img', image_name), 'wb') as f:
                        f.write(response.content)
                    print("图片下载成功")
                    variables[event.get_user_id()+'_img'].append(image_name)
                else:
                    print("请求图片失败")
            else:
                print("未匹配到图片链接")
                variables[event.get_user_id()].append(user_msg)
        if user_msg=='投稿取消':
            variables[event.get_user_id()] = []
        if user_msg=='投稿结束':
            messages = variables[event.get_user_id()]  # 获取该用户的历史消息列表
            joined_messages = '\n'.join(messages) 
            # for i in variables[event.get_user_id()]:
            #     print(i)
            print(joined_messages)
            current_dir = os.getcwd()
            parent_dir = os.path.dirname(current_dir)
            parent_dir = os.path.dirname(parent_dir)
            flag=True
            while flag:
                try:
                    print(variables[event.get_user_id()+'_img'])
                    if len(variables[event.get_user_id()+'_img'])!=0:
                        for a in variables[event.get_user_id()+'_img']:
                            sleep(4)
                            abv=bs.find_element(By.XPATH,'//*[@id="qz_poster_v4_editor_container_1"]/div[2]/div[1]/div[1]/a')
                            sleep(1)
                            ActionChains(bs).move_to_element(abv).perform()
                            sleep(3)
                            bs.find_element(By.XPATH,'//*[@id="qz_app_imageReader_1"]').send_keys(os.path.join(current_dir,'img',a))
                            print(os.path.join(current_dir,'img',a))
                            # sleep(2)
                            # bs.find_element(By.ID,'$1_substitutor_content').click()
                            sleep(5)
                            # bs.find_element(By.ID,'$1_content_content').send_keys(f"{user_msg}")

                    bs.find_element(By.ID,'$1_substitutor_content').click()
                    time.sleep(1)
                    bs.find_element(By.ID,'$1_content_content').send_keys(f"{joined_messages}")
                    time.sleep(1)
                    # bs.find_element(By.XPATH,'//*[@id="QM_Mood_Poster_Inner"]/div/div[4]/div[4]/a[2]/span').click()
                    time.sleep(1)
                    bs.find_element(By.XPATH,'//*[@id="QM_Mood_Poster_Inner"]/div/div[4]/div[4]/a[2]/span').click()
                    flag=False
                except:
                    flag=True
            variables[event.get_user_id()] = []
            variables[event.get_user_id()+'_state'] = False
            variables[event.get_user_id()+'_img'] = []
        if variables[event.get_user_id()+'_state']:
            reply_msg="1"
            # 获取用户发送的信息
            await reply.finish(reply_msg)
    elif str(event.get_event_name()) == "message.group.normal":
        reply_msg = f"这是群消息：{user_msg}"
        await reply.finish(reply_msg)
    elif str(event.get_event_name()) == "request.friend":
        num = event.json()
        num = json.loads(num)
        await bot.call_api('set_friend_add_request', flag=num['flag'], approve=True)  # 同意好友请求
        # user_id = event.get_user_id()  # 获取用户 ID
        sleep(2)
        message = '欢迎新朋友！'  # 欢迎消息内容
        await bot.call_api('send_private_msg', user_id=num['user_id'], message=message)
        sleep(2)
        message = '使用说明 投稿 输入内容 投稿结束'  # 欢迎消息内容
        await bot.call_api('send_private_msg', user_id=num['user_id'], message=message)
