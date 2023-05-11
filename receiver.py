import os

import requests
import json
import time
import pandas as pd


class Receiver:

    def __init__(self):
        curdir = os.path.dirname(__file__)
        self.config_path = os.path.join(curdir, "config.json")
        print(f"self.params is {self.config_path}")

        self.sender_initializer()

        self.df = pd.DataFrame(columns=['prompt', 'url'])

    def sender_initializer(self):

        with open(self.config_path, "r") as json_file:
            params = json.load(json_file)
        self.url = params['base_url']
        self.channelid = params['channelid']
        self.authorization = params['authorization']
        self.headers = {'authorization': self.authorization}

    def retrieve_messages(self):

        r = requests.get(
            f'{self.url}api/v10/channels/{self.channelid}/messages?limit={1}', headers=self.headers)
        jsonn = json.loads(r.text)
        return jsonn

    def collecting_results(self):
        message_list = self.retrieve_messages()
        self.awaiting_list = pd.DataFrame(columns=['prompt', 'status', 'url'])
        for message in message_list:
            if (message['author']['username'] == 'Midjourney Bot') and ('**' in message['content']):
                if len(message['attachments']) > 0:
                    if (message['attachments'][0]['filename'][-4:] == '.png') or (
                            '(Open on website for full quality)' in message['content']):
                        # prompt = message['content'].split('**')[1].split(' --')[0]
                        url = message['attachments'][0]['url']
                        return url
                    else:
                        print('drawing~')
                        return None
                else:
                    print('Waiting to start~')
                    return None

    def main(self):
        while True:
            result = self.collecting_results()
            if result:
                print(f"URL found: {result}")
                return result
            time.sleep(0.5)
