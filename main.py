# encoding:utf-8
import json
import os
import re

import langid
import requests

from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from config import conf
import plugins
from plugins import *
from common.log import logger

from common.expired_dict import ExpiredDict
from plugins.plugin_midjourney.receiver import Receiver


@plugins.register(name="Midjourney", desc="Midjourney来画图", version="1.0", author="winston")
class Midjourney(Plugin):
    def __init__(self):
        super().__init__()
        curdir = os.path.dirname(__file__)
        config_path = os.path.join(curdir, "config.json")
        logger.info(f"Midj config_path is {config_path}")
        self.params_cache = ExpiredDict(60 * 60)
        if not os.path.exists(config_path):
            logger.info('[RP] 配置文件不存在，将使用config-template.json模板')
            config_path = os.path.join(curdir, "../plugin_replicate/config.json.template")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.base_url = config["base_url"]
                self.receiver_url = config["receiver_url"]
                self.proxy = config.get("proxy", "")
                self.channelid = config['channelid']
                self.application_id = config['application_id']
                self.guild_id = config['guild_id']
                self.session_id = config['session_id']
                self.version = config['version']
                self.id = config['id']
                self.flags = config['flags']
                self.authorization = config['authorization']
                self.headers = {'authorization': self.authorization}
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.client = self.butt_discord
            logger.info("[RP] inited")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                logger.warn(f"[RP] init failed, config.json not found.")
            else:
                logger.warn("[RP] init failed." + str(e))
            raise e

    def butt_discord(self, prompt):
        prompt = prompt.replace('_', ' ')
        prompt = " ".join(prompt.split())
        prompt = prompt.lower()

        payload = {'type': 2,
                   'application_id': self.application_id,
                   'guild_id': self.guild_id,
                   'channel_id': self.channelid,
                   'session_id': self.session_id,
                   'data': {
                       'version': self.version,
                       'id': self.id,
                       'name': 'imagine',
                       'type': 1,
                       'options': [{'type': 3, 'name': 'prompt', 'value': str(prompt) + ' ' + self.flags}],
                       'attachments': []}
                   }
        if self.proxy['http'] != "" or self.proxy['https'] != "":
            r = requests.post(f"{self.base_url}api/v9/interactions", json=payload, headers=self.headers, proxies=self.proxy)
            while r.status_code != 204:
                r = requests.post(url=self.base_url, json=payload, headers=self.headers)
        else:
            r = requests.post(f"{self.base_url}api/v9/interactions", json=payload, headers=self.headers)
            print(r.status_code)
            while r.status_code != 204:
                r = requests.post(url=self.base_url, json=payload, headers=self.headers)
        logger.info('prompt [{}] successfully sent!'.format(prompt))
        receiver = Receiver()
        result = receiver.main()
        return result

    def on_handle_context(self, e_context: EventContext):

        if e_context['context'].type not in [ContextType.IMAGE_CREATE, ContextType.IMAGE]:
            return

        logger.debug("[RP] on_handle_context. content: %s" % e_context['context'].content)

        logger.info("[RP] image_query={}".format(e_context['context'].content))
        reply = Reply()
        try:
            # user_id = e_context['context']["session_id"]
            content = e_context['context'].content[:]
            print(f"[MJ] Draw prompt is {content}")
            if e_context['context'].type == ContextType.IMAGE_CREATE:
                print(f"[MJ] start image")
                old_result = self.butt_discord(content)
                result = old_result.replace("https://cdn.discordapp.com", self.receiver_url)
                reply.type = ReplyType.IMAGE_URL
                reply.content = result
                logger.info("[MJ] result={}".format(result))
            e_context.action = EventAction.BREAK_PASS  # 事件结束后，跳过处理context的默认逻辑
            e_context['reply'] = reply

        except Exception as e:
            reply.type = ReplyType.ERROR
            reply.content = "[MJ] " + str(e)
            e_context['reply'] = reply
            logger.exception("[MJ] exception: %s" % e)
            e_context.action = EventAction.CONTINUE  # 事件继续，交付给下个插件或默认逻辑

    def get_help_text(self, verbose=False, **kwargs):
        if not conf().get('image_create_prefix'):
            return "画图功能未启用"
        else:
            trigger = conf()['image_create_prefix'][0]
        help_text = "利用Midjourney来画图。\n"
        if not verbose:
            return help_text

        help_text += f"使用方法:\n使用\"{trigger}[prompt]来触发机器人使用Midjourney画图\n"
        for rule in self.rules:
            keywords = [f"[{keyword}]" for keyword in rule['keywords']]
            help_text += f"{','.join(keywords)}"
            if "desc" in rule:
                help_text += f"-{rule['desc']}\n"
            else:
                help_text += "\n"
        return help_text
