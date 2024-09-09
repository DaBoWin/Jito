# VPS库存监控，她的名字叫Jito，谐音 鸡托

这是一个简单的VPS库存监控，通过读取页面缺货关键字信息来达到监控目的，并且使用TG频道发送监控信息。

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

## 商家监控配置JSON的具体说明

### 商家信息

- **名称 (name)**: DMIT
- **标签 (tag)**: `#dmit`
- **商家评论 (review_content)**: 商家评论：大妈

### 库存状态（缺货关键字）

- **缺货状态文本 (out_of_stock_text)**: `Out of Stock` （缺货时显示）

### 产品信息

- **商品列表 (stock_urls)**:
  - **购买链接 (url)**: https://www.dmit.io/cart.php?a=add&pid=197
  - **商品名称 (title)**: HKG.T1.WEE（国际优化线路, 非国内优化）
  - **价格 (price)**: $36.90 USD 每年
  - **硬件配置 (hardware_info)**:
    - 1 vCPU
    - 1.0 GB RAM
    - 20G SSD 存储
    - 每月 1000GB 流量限制（入站和出站）
    - 1 个 IPv4 地址 & 1 个 IPv6 地址（/64 子网段）
  - **购买链接提示 (stock_url_text)**: 点击购买或长按复制

### 优惠券信息

- **月度优惠券 (coupon_monthly)**: 无
- **年度优惠券 (coupon_annual)**: 无



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


