## 插件描述

***本插件用于将画图请求转发给discord api来调用Midjourney Bot。***

## 使用说明

📌 在 [`Discord`](https://articles.zsxq.com/id_galu3lqwcog9.html)创建 Midjourney Bot，

📌 构建完机器人后 [`获取Midjourney Bot API相关信息`](https://articles.zsxq.com/id_5isuec94bk6m.html) 

📌[`搭建反向代理`](https://wx.zsxq.com/dweb2/index/footprint/585252181521214)，请注意在保证与service - discord - wechat 交互无障碍的时候需要构建代理。



将`config.json.template`复制为`config.json`，修改相关信息。

```json
{
  "base_url": "",
  "receiver_url": "",
  "proxy": {
    "http": "",
    "https": ""
  },
  "channelid": "",
  "authorization": "",
  "application_id": "",
  "guild_id": "",
  "session_id": "",
  "version": "",
  "id": "",
  "flags": ""
}
```

> 

### 画图请求格式

> 用户的画图请求格式为:

```
    <画图触发词> <prompt> 
```

- 本插件会对画图触发词后的的内容匹配为***prompt***,建议用英文或者chatgpt生成Midjoury Bot的指令效果会更好
- 关键词中包含`help`或`帮助`，会打印出帮助文档。

例如: 画 A frog at the bottom of a well

prompt为"A frog at the bottom of a well"

### 版本

| 版本   | 功能                                                         |
| ------ | ------------------------------------------------------------ |
| v1.0   | 微信调用mj text-image                                        |
| v1.1   | 优化调用机制                                                 |
| Future | 微调功能、图生图、能够与任何数量的Midjourney账户并行工作，以获得更好的可扩展性能 |

### 

### 咨询讨论

https://t.zsxq.com/0d2rnw2hW 有完整的部署教程，也可提供二开支持