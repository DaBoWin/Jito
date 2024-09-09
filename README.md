# VPS库存监控，她的名字叫Jito，谐音 鸡托

这是一个简单的VPS库存监控，通过读取页面关键字信息来达到监控目的，并且使用TG频道发送监控信息。

## 准备工作
1. 创建一个tg机器人以及一个tg频道
2. 一个独立的vps（自己完全控制，并注意避免泄露自己的机器人token）

## 安装

## 安装python3
1.大多数 Linux 发行版都预装了 Python。您可以通过以下命令检查版本：
```
python --version
```
2.如果您的系统没有 Python，或者您需要特定版本，则可以使用发行版的包管理器进行安装。例如，在 Ubuntu 上，您可以使用以下命令：
```
sudo apt install python3
```
3.安装pip
```
sudo apt-get install python3-pip
```
4.安装python相关依赖包
```
pip install aiohttp beautifulsoup4 python-telegram-bot
```


## 下载monitor.py和config.json并修改config.json的tg机器人和频道配置

```
    "telegram_token": "你的tg机器人api token",
    "telegram_chat_id": "你的tg频道ID，注意机器人要加入频道并且是管理员"
```

## 使用

1. 启动监控：

    ```bash
    python monitor.py
    ```
    ## 常驻后台运行
    ```bash
    nohup python monitor.py &
    ```


## 监控周期以及冷却周期，以秒为单位
默认是每分钟监控一次页面，如果发现有库存，会进行24小时冷却，需要等待24小时再进行监控，可以自己按需调整
```
    "check_interval": 60,
    "cooldown_period": 86400
```

## 许可证

此项目使用 MIT 许可证。请参阅 [LICENSE](LICENSE) 文件了解更多信息。


