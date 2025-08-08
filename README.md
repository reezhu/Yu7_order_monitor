# 小米汽车订单监控系统

## 📋 项目简介

这是一个专为小米汽车订单状态监控而设计的Python自动化工具。支持多任务并发监控、多种通知方式（邮件、QQ、短信），采用内存存储，无需数据库配置，开箱即用。

本项目除了这几个字全部由Cursor编写。

## ✨ 主要特性

- 🔄 **多任务监控**：支持同时监控多个订单
- 📧 **多邮箱通知**：支持QQ邮箱、普通邮箱、短信通知
- 💾 **内存存储**：无需数据库，使用内存存储状态历史
- 🎛️ **图形化配置**：提供友好的配置管理工具
- 📊 **实时监控**：定时检查订单状态变化
- 🔔 **智能通知**：状态变化时自动发送通知

## 📁 项目结构

```
xiaomi/
├── README.md                    # 项目说明文档
├── xiaomi_config.json          # 配置文件
├── xiaomi_start_monitor.py     # 启动脚本
├── xiaomi_monitor.py           # 监控核心脚本
├── config_manager.py           # 配置管理工具
├── xiaomi.py                   # 基础测试脚本
├── requirements.txt            # 依赖包列表
└── xiaomi_monitor.log          # 运行日志
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装Python 3.7+，然后安装依赖包：

```bash
pip install -r requirements.txt
```

### 2. 获取订单信息

#### 方法一：使用抓包工具（推荐）

1. **下载抓包工具**：
   - 手机端：Reqable、Packet Capture

2. **抓包步骤**：
   - 打开抓包工具
   - 打开微信小米汽车小程序
   - 进入订单详情页面
   - 查看网络请求，找到 `order/detail` 接口
   - 记录以下信息：
     - 订单号（orderId）
     - 用户ID（userId）
     - Cookie信息
     - 请求头信息

#### 方法二：参考小红书教程

在小红书搜索"小米汽车订单抓包"相关教程，有很多详细的图文教程。

### 3. 配置系统

运行配置管理工具：

```bash
python config_manager.py
```

按照提示配置：
1. 添加监控任务
2. 填入订单信息
3. 配置通知方式

### 4. 启动监控

```bash
python xiaomi_start_monitor.py
```

## ⚙️ 详细配置

### 邮件服务器配置（推荐QQ邮箱）

#### QQ邮箱配置步骤：

1. **开启SMTP服务**：
   - 登录QQ邮箱网页版
   - 进入"设置" → "账户"
   - 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
   - 开启"POP3/SMTP服务"

2. **获取授权码**：
   - 开启服务后，点击"生成授权码"
   - 按提示操作，获取16位授权码
   - 这个授权码就是配置文件中的密码

3. **配置示例**：
```json
{
  "smtp_config": {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 587,
    "sender": "your_email@qq.com",
    "password": "your_authorization_code"
  }
}
```

### 配置文件详解

```json
{
  "global_settings": {
    "check_interval": 15,        // 检查间隔（分钟）
    "log_level": "INFO"          // 日志级别
  },
  "monitoring_tasks": [
    {
      "task_id": "task_001",           // 任务唯一标识
      "task_name": "小米汽车订单监控",    // 任务名称
      "enabled": true,                  // 是否启用
      "order_id": "5256772385302521",   // 订单号
      "user_id": 1014566219,           // 用户ID
      "url": "https://api.retail.xiaomiev.com/mtop/car-order/order/detail",
      "headers": {                      // HTTP请求头
        "User-Agent": "Mozilla/5.0...",
        "Cookie": "your_cookie_here"
      },
      "notifications": {                // 通知配置
        "email": {
          "enabled": true,
          "smtp_config": {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 587,
            "sender": "your_email@qq.com",
            "password": "your_auth_code"
          },
          "receivers": [
            {
              "email": "receiver@example.com",
              "name": "接收者姓名",
              "enabled": true
            }
          ]
        },
        "qq": {
          "enabled": true,
          "qq_emails": [
            {
              "email": "qq_user@qq.com",
              "name": "QQ用户",
              "enabled": true
            }
          ]
        }
      }
    }
  ]
}
```

## 📧 通知配置

### 1. 邮件通知

支持多种邮箱服务商：
- **QQ邮箱**（推荐）：`smtp.qq.com:587`
- **163邮箱**：`smtp.163.com:25`
- **Gmail**：`smtp.gmail.com:587`
- **Outlook**：`smtp-mail.outlook.com:587`

### 2. QQ通知

QQ通知实际上是邮件通知的简化版，专门针对QQ邮箱优化。

### 3. 短信通知

支持阿里云短信服务，需要配置：
- AccessKey ID
- AccessKey Secret
- 短信签名
- 短信模板

## 🎯 使用方法

### 启动监控

```bash
# 使用启动脚本（推荐）
python xiaomi_start_monitor.py

# 或直接启动监控
python xiaomi_monitor.py
```

### 管理配置

```bash
# 打开配置管理工具
python config_manager.py
```

### 测试通知

在配置管理工具中选择"测试通知功能"来验证配置是否正确。

## 📊 监控状态说明

已知的小米汽车订单状态码对应关系：

| 状态码  | 状态名称  | 说明 |
|------|-------|------|
| 25XX | 车辆生产中 | 车辆正在生产 |
| 26XX | 车辆已下线 | 车辆生产完成 |
| 3XXX | 已提车   | 已提车 |

## 🔧 故障排除

### 常见问题

1. **邮件发送失败**
   - 检查SMTP配置是否正确
   - 确认QQ邮箱授权码是否正确
   - 检查网络连接

2. **订单信息获取失败**
   - 确认订单号和用户ID是否正确
   - 检查Cookie是否过期
   - 确认网络连接正常

3. **通知未收到**
   - 检查接收者邮箱是否正确
   - 确认通知功能已启用
   - 查看日志文件获取详细错误信息

### 日志查看

```bash
# 查看实时日志
tail -f xiaomi_monitor.log

# 查看错误日志
grep "ERROR" xiaomi_monitor.log
```

## 📝 注意事项

1. **Cookie有效期**：Cookie通常有有效期，过期需要重新获取
2. **检查频率**：建议设置合理的检查间隔，避免过于频繁
3. **网络环境**：确保网络连接稳定
4. **邮箱限制**：注意邮箱发送频率限制
5. **数据安全**：配置文件包含敏感信息，请妥善保管

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**免责声明**：本项目仅供学习和个人使用，请遵守相关法律法规和平台使用条款。
