# -*- coding: utf-8 -*-
# @Author  : Ree
# @Date    : 2025-01-08
# @Description: 测试通知功能脚本

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_config():
    """加载配置文件"""
    config_file = 'xiaomi_config.json'
    
    if not os.path.exists(config_file):
        print(f"✗ 配置文件 {config_file} 不存在")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError:
        print("✗ 配置文件格式错误")
        return None
    except Exception as e:
        print(f"✗ 读取配置文件失败: {str(e)}")
        return None

def test_email_notification(config):
    """测试邮件通知"""
    print("\n=== 测试邮件通知 ===")
    
    email_config = config.get('notifications', {}).get('email', {})
    if not email_config.get('enabled', False):
        print("✗ 邮件通知未启用")
        return False
    
    print(f"发件人: {email_config['sender']}")
    print(f"收件人: {email_config['receiver']}")
    print(f"SMTP服务器: {email_config['smtp_server']}:{email_config['smtp_port']}")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = email_config['sender']
        msg['To'] = email_config['receiver']
        msg['Subject'] = "小米汽车订单监控 - 测试通知"
        
        body = f"""
这是一条测试通知！

订单号: {config['order_id']}
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明邮件通知配置正确。

---
此邮件由小米汽车订单监控脚本自动发送
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        print("正在连接SMTP服务器...")
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        
        print("正在启动TLS加密...")
        server.starttls()
        
        print("正在登录...")
        server.login(email_config['sender'], email_config['password'])
        
        print("正在发送邮件...")
        server.send_message(msg)
        server.quit()
        
        print("✓ 邮件测试通知发送成功")
        print("请检查您的邮箱是否收到测试邮件")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ 邮箱认证失败，请检查邮箱和密码")
        return False
    except smtplib.SMTPConnectError:
        print("✗ 连接SMTP服务器失败，请检查服务器地址和端口")
        return False
    except Exception as e:
        print(f"✗ 邮件测试通知发送失败: {str(e)}")
        return False

def test_qq_notification(config):
    """测试QQ通知"""
    print("\n=== 测试QQ通知 ===")
    
    qq_config = config.get('notifications', {}).get('qq', {})
    if not qq_config.get('enabled', False):
        print("✗ QQ通知未启用")
        return False
    
    email_config = config.get('notifications', {}).get('email', {})
    if not email_config.get('enabled', False):
        print("✗ QQ通知需要邮件配置")
        return False
    
    print(f"QQ邮箱: {qq_config['qq_email']}")
    print(f"使用邮件服务: {email_config['smtp_server']}")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = email_config['sender']
        msg['To'] = qq_config['qq_email']
        msg['Subject'] = "小米汽车订单监控 - QQ测试通知"
        
        body = f"""
这是一条QQ测试通知！

订单号: {config['order_id']}
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明QQ通知配置正确。
请确保您的QQ邮箱已开启邮件通知功能。

---
此邮件由小米汽车订单监控脚本自动发送
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        print("正在连接SMTP服务器...")
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        
        print("正在启动TLS加密...")
        server.starttls()
        
        print("正在登录...")
        server.login(email_config['sender'], email_config['password'])
        
        print("正在发送QQ通知邮件...")
        server.send_message(msg)
        server.quit()
        
        print("✓ QQ测试通知发送成功")
        print("请检查您的QQ是否收到通知")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ 邮箱认证失败，请检查邮箱和密码")
        return False
    except smtplib.SMTPConnectError:
        print("✗ 连接SMTP服务器失败，请检查服务器地址和端口")
        return False
    except Exception as e:
        print(f"✗ QQ测试通知发送失败: {str(e)}")
        return False

def test_sms_notification(config):
    """测试短信通知"""
    print("\n=== 测试短信通知 ===")
    
    sms_config = config.get('notifications', {}).get('sms', {})
    if not sms_config.get('enabled', False):
        print("✗ 短信通知未启用")
        return False
    
    print("当前短信配置:")
    for key, value in sms_config.items():
        if key not in ['access_key_secret', 'password']:  # 不显示敏感信息
            print(f"  {key}: {value}")
    
    print("\n⚠ 短信测试功能需要配置短信服务")
    print("目前支持阿里云短信服务，需要安装相关SDK:")
    print("pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi")
    
    # 检查是否安装了阿里云SDK
    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest
        print("✓ 阿里云SDK已安装")
        
        # 这里可以添加实际的短信测试代码
        print("短信测试功能待完善...")
        return False
        
    except ImportError:
        print("✗ 未安装阿里云SDK")
        print("请运行: pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi")
        return False
    except Exception as e:
        print(f"✗ 短信测试失败: {str(e)}")
        return False

def show_notification_status(config):
    """显示通知配置状态"""
    print("\n=== 通知配置状态 ===")
    
    notifications = config.get('notifications', {})
    
    # 邮件通知状态
    email_config = notifications.get('email', {})
    email_enabled = email_config.get('enabled', False)
    print(f"邮件通知: {'✓ 已启用' if email_enabled else '✗ 未启用'}")
    if email_enabled:
        print(f"  发件人: {email_config.get('sender', '未配置')}")
        print(f"  收件人: {email_config.get('receiver', '未配置')}")
        print(f"  SMTP服务器: {email_config.get('smtp_server', '未配置')}:{email_config.get('smtp_port', '未配置')}")
    
    # QQ通知状态
    qq_config = notifications.get('qq', {})
    qq_enabled = qq_config.get('enabled', False)
    print(f"QQ通知: {'✓ 已启用' if qq_enabled else '✗ 未启用'}")
    if qq_enabled:
        print(f"  QQ邮箱: {qq_config.get('qq_email', '未配置')}")
    
    # 短信通知状态
    sms_config = notifications.get('sms', {})
    sms_enabled = sms_config.get('enabled', False)
    print(f"短信通知: {'✓ 已启用' if sms_enabled else '✗ 未启用'}")
    if sms_enabled:
        print(f"  服务商: {sms_config.get('provider', '未配置')}")
        print(f"  手机号: {sms_config.get('phone_number', '未配置')}")

def main():
    """主函数"""
    print("小米汽车订单监控 - 通知功能测试")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    if not config:
        return
    
    # 显示配置状态
    show_notification_status(config)
    
    # 测试菜单
    while True:
        print("\n请选择测试项目:")
        print("1. 测试邮件通知")
        print("2. 测试QQ通知")
        print("3. 测试短信通知")
        print("4. 测试所有启用的通知")
        print("5. 显示配置状态")
        print("6. 退出")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == '1':
            test_email_notification(config)
        elif choice == '2':
            test_qq_notification(config)
        elif choice == '3':
            test_sms_notification(config)
        elif choice == '4':
            test_all_notifications(config)
        elif choice == '5':
            show_notification_status(config)
        elif choice == '6':
            print("已退出")
            break
        else:
            print("无效选项，请重新选择")

def test_all_notifications(config):
    """测试所有启用的通知方式"""
    print("\n=== 测试所有启用的通知方式 ===")
    
    notifications = config.get('notifications', {})
    test_results = []
    
    # 测试邮件通知
    if notifications.get('email', {}).get('enabled', False):
        result = test_email_notification(config)
        test_results.append(('邮件通知', result))
    
    # 测试QQ通知
    if notifications.get('qq', {}).get('enabled', False):
        result = test_qq_notification(config)
        test_results.append(('QQ通知', result))
    
    # 测试短信通知
    if notifications.get('sms', {}).get('enabled', False):
        result = test_sms_notification(config)
        test_results.append(('短信通知', result))
    
    # 显示测试结果汇总
    print("\n=== 测试结果汇总 ===")
    print("=" * 30)
    
    success_count = 0
    for notification_type, success in test_results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"{notification_type}: {status}")
        if success:
            success_count += 1
    
    print(f"\n总计: {len(test_results)} 种通知方式，{success_count} 个成功")
    
    if success_count == 0:
        print("\n⚠ 所有通知方式测试失败，请检查配置")
    elif success_count < len(test_results):
        print("\n⚠ 部分通知方式测试失败，请检查配置")
    else:
        print("\n✓ 所有通知方式测试成功！")

if __name__ == "__main__":
    main() 