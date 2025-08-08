# -*- coding: utf-8 -*-
# @Author  : Ree
# @Date    : 2025-01-08
# @Description: 快速启动监控脚本 - 支持多任务多邮箱配置

import os
import sys
import json
import subprocess
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List, Optional

def check_dependencies():
    """检查依赖包是否安装"""
    print("检查依赖包...")
    
    required_packages = ['requests', 'schedule']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ 成功安装 {package}")
            except subprocess.CalledProcessError:
                print(f"✗ 安装 {package} 失败")
                return False
    
    return True

def check_config():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    if not os.path.exists('xiaomi_config.json'):
        print("✗ xiaomi_config.json 文件不存在")
        print("请先创建配置文件或运行安装脚本")
        return False, None
    
    try:
        with open('xiaomi_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查新的配置结构
        if 'monitoring_tasks' not in config:
            print("✗ 配置文件格式错误：缺少 monitoring_tasks 字段")
            return False, None
        
        tasks = config['monitoring_tasks']
        if not tasks:
            print("✗ 没有配置任何监控任务")
            return False, None
        
        enabled_tasks = [task for task in tasks if task.get('enabled', False)]
        if not enabled_tasks:
            print("⚠ 没有启用的监控任务")
            return False, None
        
        print(f"✓ 配置文件格式正确，发现 {len(tasks)} 个任务，{len(enabled_tasks)} 个已启用")
        
        # 检查每个任务的配置
        for i, task in enumerate(tasks, 1):
            task_name = task.get('task_name', f'任务{i}')
            enabled = task.get('enabled', False)
            status = "✓ 启用" if enabled else "✗ 禁用"
            print(f"  {i}. {task_name}: {status}")
            
            if enabled:
                # 检查必要字段
                required_fields = ['order_id', 'user_id', 'url', 'headers']
                for field in required_fields:
                    if field not in task:
                        print(f"    ✗ 缺少必要字段: {field}")
                        return False, None
                
                # 检查通知配置
                notifications = task.get('notifications', {})
                enabled_notifications = []
                
                if notifications.get('email', {}).get('enabled', False):
                    email_config = notifications['email']
                    if 'smtp_config' in email_config and 'receivers' in email_config:
                        enabled_receivers = [r for r in email_config['receivers'] if r.get('enabled', False)]
                        if enabled_receivers:
                            enabled_notifications.append(f'邮件通知({len(enabled_receivers)}个接收者)')
                
                if notifications.get('qq', {}).get('enabled', False):
                    qq_config = notifications['qq']
                    if 'qq_emails' in qq_config:
                        enabled_qq = [q for q in qq_config['qq_emails'] if q.get('enabled', False)]
                        if enabled_qq:
                            enabled_notifications.append(f'QQ通知({len(enabled_qq)}个接收者)')
                
                if notifications.get('sms', {}).get('enabled', False):
                    sms_config = notifications['sms']
                    if 'phone_numbers' in sms_config:
                        enabled_sms = [p for p in sms_config['phone_numbers'] if p.get('enabled', False)]
                        if enabled_sms:
                            enabled_notifications.append(f'短信通知({len(enabled_sms)}个接收者)')
                
                if enabled_notifications:
                    print(f"    ✓ 启用的通知方式: {', '.join(enabled_notifications)}")
                else:
                    print("    ⚠ 未启用任何通知方式")
        
        return True, config
        
    except json.JSONDecodeError:
        print("✗ 配置文件格式错误")
        return False, None
    except Exception as e:
        print(f"✗ 检查配置文件失败: {str(e)}")
        return False, None

def test_email_notification_for_task(task: Dict[str, Any]) -> bool:
    """测试指定任务的邮件通知"""
    email_config = task.get('notifications', {}).get('email', {})
    if not email_config.get('enabled', False):
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 邮件通知未启用")
        return False
    
    smtp_config = email_config.get('smtp_config', {})
    receivers = email_config.get('receivers', [])
    
    if not smtp_config or not receivers:
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 邮件配置不完整")
        return False
    
    enabled_receivers = [r for r in receivers if r.get('enabled', False)]
    if not enabled_receivers:
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 没有启用的邮件接收者")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config['sender']
        msg['To'] = ', '.join([r['email'] for r in enabled_receivers])
        msg['Subject'] = f"小米汽车订单监控 - {task.get('task_name', '未知任务')} 测试通知"
        
        body = f"""
        这是一条测试通知！
        
        任务名称: {task.get('task_name', '未知')}
        订单号: {task.get('order_id', '未知')}
        测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        如果您收到这封邮件，说明邮件通知配置正确。
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
        server.starttls()
        server.login(smtp_config['sender'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        
        print(f"✓ 任务 '{task.get('task_name', '未知')}' 邮件测试通知发送成功")
        return True
        
    except Exception as e:
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 邮件测试通知发送失败: {str(e)}")
        return False

def test_qq_notification_for_task(task: Dict[str, Any]) -> bool:
    """测试指定任务的QQ通知"""
    qq_config = task.get('notifications', {}).get('qq', {})
    if not qq_config.get('enabled', False):
        print(f"✗ 任务 '{task.get('task_name', '未知')}' QQ通知未启用")
        return False
    
    email_config = task.get('notifications', {}).get('email', {})
    if not email_config.get('enabled', False):
        print(f"✗ 任务 '{task.get('task_name', '未知')}' QQ通知需要邮件配置")
        return False
    
    qq_emails = qq_config.get('qq_emails', [])
    enabled_qq_emails = [q for q in qq_emails if q.get('enabled', False)]
    
    if not enabled_qq_emails:
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 没有启用的QQ邮箱")
        return False
    
    smtp_config = email_config.get('smtp_config', {})
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config['sender']
        msg['To'] = ', '.join([q['email'] for q in enabled_qq_emails])
        msg['Subject'] = f"小米汽车订单监控 - {task.get('task_name', '未知任务')} QQ测试通知"
        
        body = f"""
        这是一条QQ测试通知！
        
        任务名称: {task.get('task_name', '未知')}
        订单号: {task.get('order_id', '未知')}
        测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        如果您收到这封邮件，说明QQ通知配置正确。
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
        server.starttls()
        server.login(smtp_config['sender'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        
        print(f"✓ 任务 '{task.get('task_name', '未知')}' QQ测试通知发送成功")
        return True
        
    except Exception as e:
        print(f"✗ 任务 '{task.get('task_name', '未知')}' QQ测试通知发送失败: {str(e)}")
        return False

def test_sms_notification_for_task(task: Dict[str, Any]) -> bool:
    """测试指定任务的短信通知"""
    sms_config = task.get('notifications', {}).get('sms', {})
    if not sms_config.get('enabled', False):
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 短信通知未启用")
        return False
    
    phone_numbers = sms_config.get('phone_numbers', [])
    enabled_phones = [p for p in phone_numbers if p.get('enabled', False)]
    
    if not enabled_phones:
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 没有启用的手机号")
        return False
    
    try:
        print(f"⚠ 任务 '{task.get('task_name', '未知')}' 短信测试功能需要配置短信服务")
        print(f"当前短信配置:")
        for key, value in sms_config.items():
            if key not in ['access_key_secret', 'password']:  # 不显示敏感信息
                print(f"  {key}: {value}")
        print(f"启用的手机号: {', '.join([p['phone'] for p in enabled_phones])}")
        return False
        
    except Exception as e:
        print(f"✗ 任务 '{task.get('task_name', '未知')}' 短信测试通知失败: {str(e)}")
        return False

def test_notifications_for_task(task: Dict[str, Any]) -> List[tuple]:
    """测试指定任务的所有通知方式"""
    task_name = task.get('task_name', '未知任务')
    print(f"\n测试任务 '{task_name}' 的通知功能...")
    print("=" * 50)
    
    notifications = task.get('notifications', {})
    test_results = []
    
    # 测试邮件通知
    if notifications.get('email', {}).get('enabled', False):
        print(f"\n测试任务 '{task_name}' 的邮件通知...")
        result = test_email_notification_for_task(task)
        test_results.append(('邮件通知', result))
    
    # 测试QQ通知
    if notifications.get('qq', {}).get('enabled', False):
        print(f"\n测试任务 '{task_name}' 的QQ通知...")
        result = test_qq_notification_for_task(task)
        test_results.append(('QQ通知', result))
    
    # 测试短信通知
    if notifications.get('sms', {}).get('enabled', False):
        print(f"\n测试任务 '{task_name}' 的短信通知...")
        result = test_sms_notification_for_task(task)
        test_results.append(('短信通知', result))
    
    # 显示测试结果
    print(f"\n任务 '{task_name}' 测试结果汇总:")
    print("=" * 30)
    
    success_count = 0
    for notification_type, success in test_results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"{notification_type}: {status}")
        if success:
            success_count += 1
    
    print(f"\n任务 '{task_name}' 总计: {len(test_results)} 种通知方式，{success_count} 个成功")
    
    return test_results

def test_all_notifications(config: Dict[str, Any]):
    """测试所有任务的所有通知方式"""
    print("\n开始测试所有任务的通知功能...")
    print("=" * 60)
    
    tasks = config.get('monitoring_tasks', [])
    enabled_tasks = [task for task in tasks if task.get('enabled', False)]
    
    if not enabled_tasks:
        print("没有启用的任务")
        return
    
    all_results = []
    
    for task in enabled_tasks:
        task_results = test_notifications_for_task(task)
        all_results.extend(task_results)
    
    # 显示总体测试结果
    print("\n所有任务测试结果汇总:")
    print("=" * 60)
    
    success_count = sum(1 for _, success in all_results if success)
    total_count = len(all_results)
    
    print(f"总计: {total_count} 种通知方式，{success_count} 个成功")
    
    if success_count == 0:
        print("\n⚠ 所有通知方式测试失败，请检查配置")
    elif success_count < total_count:
        print("\n⚠ 部分通知方式测试失败，请检查配置")
    else:
        print("\n✓ 所有通知方式测试成功！")

def start_monitor():
    """启动监控脚本"""
    print("\n启动监控脚本...")
    
    try:
        # 启动监控脚本
        process = subprocess.Popen([sys.executable, 'xiaomi_monitor.py'])
        
        print("✓ 监控脚本已启动")
        print("按 Ctrl+C 停止监控")
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n正在停止监控...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("监控已停止")
    except Exception as e:
        print(f"✗ 启动监控失败: {str(e)}")

def show_task_summary(config: Dict[str, Any]):
    """显示任务摘要"""
    tasks = config.get('monitoring_tasks', [])
    enabled_tasks = [task for task in tasks if task.get('enabled', False)]
    
    print(f"\n任务摘要:")
    print("=" * 40)
    print(f"总任务数: {len(tasks)}")
    print(f"启用任务数: {len(enabled_tasks)}")
    
    for i, task in enumerate(enabled_tasks, 1):
        task_name = task.get('task_name', f'任务{i}')
        order_id = task.get('order_id', '未知')
        notifications = task.get('notifications', {})
        
        enabled_notifications = []
        if notifications.get('email', {}).get('enabled', False):
            email_receivers = [r for r in notifications['email'].get('receivers', []) if r.get('enabled', False)]
            if email_receivers:
                enabled_notifications.append(f"邮件({len(email_receivers)}个)")
        
        if notifications.get('qq', {}).get('enabled', False):
            qq_receivers = [q for q in notifications['qq'].get('qq_emails', []) if q.get('enabled', False)]
            if qq_receivers:
                enabled_notifications.append(f"QQ({len(qq_receivers)}个)")
        
        if notifications.get('sms', {}).get('enabled', False):
            sms_receivers = [p for p in notifications['sms'].get('phone_numbers', []) if p.get('enabled', False)]
            if sms_receivers:
                enabled_notifications.append(f"短信({len(sms_receivers)}个)")
        
        notification_summary = ', '.join(enabled_notifications) if enabled_notifications else "无"
        
        print(f"{i}. {task_name}")
        print(f"   订单号: {order_id}")
        print(f"   通知方式: {notification_summary}")

def main():
    """主函数"""
    print("小米汽车订单监控脚本 - 多任务多邮箱配置版")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n依赖检查失败，请手动安装依赖包")
        return
    
    # 检查配置
    config_check, config = check_config()
    if not config_check:
        print("\n配置检查失败，请检查配置文件")
        return
    
    # 显示任务摘要
    show_task_summary(config)
    
    # 主菜单
    while True:
        print("\n请选择操作:")
        print("1. 启动监控脚本")
        print("2. 测试所有任务的通知功能")
        print("3. 测试指定任务的通知功能")
        print("4. 显示任务摘要")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            start_monitor()
            break
        elif choice == '2':
            test_all_notifications(config)
        elif choice == '3':
            tasks = config.get('monitoring_tasks', [])
            enabled_tasks = [task for task in tasks if task.get('enabled', False)]
            
            if not enabled_tasks:
                print("没有启用的任务")
                continue
            
            print("\n请选择要测试的任务:")
            for i, task in enumerate(enabled_tasks, 1):
                print(f"{i}. {task.get('task_name', f'任务{i}')}")
            
            try:
                task_choice = int(input(f"\n请输入任务编号 (1-{len(enabled_tasks)}): ").strip())
                if 1 <= task_choice <= len(enabled_tasks):
                    selected_task = enabled_tasks[task_choice - 1]
                    test_notifications_for_task(selected_task)
                else:
                    print("无效的任务编号")
            except ValueError:
                print("请输入有效的数字")
        elif choice == '4':
            show_task_summary(config)
        elif choice == '5':
            print("已退出")
            break
        else:
            print("无效选项，请重新选择")

if __name__ == "__main__":
    main() 