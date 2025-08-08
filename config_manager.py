# -*- coding: utf-8 -*-
# @Author  : Ree
# @Date    : 2025-01-08
# @Description: 配置管理工具 - 支持多任务多邮箱配置

import json
import os
import sys
from typing import Dict, Any, List, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = 'xiaomi_config.json'):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✓ 成功加载配置文件: {self.config_file}")
                return config
            except Exception as e:
                print(f"✗ 加载配置文件失败: {str(e)}")
                return self.get_default_config()
        else:
            print(f"⚠ 配置文件不存在: {self.config_file}")
            return self.get_default_config()
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✓ 配置文件已保存: {self.config_file}")
            return True
        except Exception as e:
            print(f"✗ 保存配置文件失败: {str(e)}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "global_settings": {
                "check_interval": 15,
                "log_level": "INFO"
            },
            "monitoring_tasks": []
        }
    
    def show_task_summary(self):
        """显示任务摘要"""
        tasks = self.config.get('monitoring_tasks', [])
        enabled_tasks = [task for task in tasks if task.get('enabled', False)]
        
        print(f"\n配置摘要:")
        print("=" * 50)
        print(f"总任务数: {len(tasks)}")
        print(f"启用任务数: {len(enabled_tasks)}")
        
        if not tasks:
            print("没有配置任何任务")
            return
        
        for i, task in enumerate(tasks, 1):
            task_name = task.get('task_name', f'任务{i}')
            enabled = task.get('enabled', False)
            order_id = task.get('order_id', '未知')
            status = "✓ 启用" if enabled else "✗ 禁用"
            
            print(f"\n{i}. {task_name} ({status})")
            print(f"   订单号: {order_id}")
            
            # 显示通知配置
            notifications = task.get('notifications', {})
            notification_summary = []
            
            if notifications.get('email', {}).get('enabled', False):
                email_receivers = [r for r in notifications['email'].get('receivers', []) if r.get('enabled', False)]
                if email_receivers:
                    notification_summary.append(f"邮件({len(email_receivers)}个)")
            
            if notifications.get('qq', {}).get('enabled', False):
                qq_receivers = [q for q in notifications['qq'].get('qq_emails', []) if q.get('enabled', False)]
                if qq_receivers:
                    notification_summary.append(f"QQ({len(qq_receivers)}个)")
            
            if notifications.get('sms', {}).get('enabled', False):
                sms_receivers = [p for p in notifications['sms'].get('phone_numbers', []) if p.get('enabled', False)]
                if sms_receivers:
                    notification_summary.append(f"短信({len(sms_receivers)}个)")
            
            notification_text = ', '.join(notification_summary) if notification_summary else "无"
            print(f"   通知方式: {notification_text}")
    
    def add_task(self):
        """添加新任务"""
        print("\n添加新任务")
        print("=" * 30)
        
        # 获取任务基本信息
        task_id = input("请输入任务ID (如: task_001): ").strip()
        if not task_id:
            print("✗ 任务ID不能为空")
            return
        
        # 检查任务ID是否已存在
        existing_tasks = self.config.get('monitoring_tasks', [])
        if any(task.get('task_id') == task_id for task in existing_tasks):
            print(f"✗ 任务ID '{task_id}' 已存在")
            return
        
        task_name = input("请输入任务名称: ").strip()
        if not task_name:
            task_name = f"任务{task_id}"
        
        order_id = input("请输入订单号: ").strip()
        if not order_id:
            print("✗ 订单号不能为空")
            return
        
        user_id = input("请输入用户ID: ").strip()
        if not user_id:
            print("✗ 用户ID不能为空")
            return
        
        try:
            user_id = int(user_id)
        except ValueError:
            print("✗ 用户ID必须是数字")
            return
        
        url = input("请输入API地址 (直接回车使用默认): ").strip()
        if not url:
            url = "https://api.retail.xiaomiev.com/mtop/car-order/order/detail"
        
        # 创建新任务配置
        new_task = {
            "task_id": task_id,
            "task_name": task_name,
            "enabled": True,
            "order_id": order_id,
            "user_id": user_id,
            "url": url,
            "headers": {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.61(0x18003d34) NetType/4G Language/zh_CN",
                "Accept-Encoding": "gzip,compress,br,deflate",
                "Content-Type": "application/json",
                "configSelectorVersion": "2",
                "content-type": "application/json; charset=utf-8",
                "deviceappversion": "1.16.0",
                "x-user-agent": "channel/car platform/car.wxlite",
                "Referer": "https://servicewechat.com/wx183d85f5e5e273c6/101/page-frame.html",
                "Cookie": "serviceTokenCar=0;"
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_config": {
                        "smtp_server": "smtp.qq.com",
                        "smtp_port": 587,
                        "sender": "",
                        "password": ""
                    },
                    "receivers": []
                },
                "qq": {
                    "enabled": False,
                    "qq_emails": []
                },
                "sms": {
                    "enabled": False,
                    "provider": "aliyun",
                    "access_key_id": "",
                    "access_key_secret": "",
                    "sign_name": "",
                    "template_code": "",
                    "phone_numbers": []
                }
            }
        }
        
        # 添加到配置中
        if 'monitoring_tasks' not in self.config:
            self.config['monitoring_tasks'] = []
        
        self.config['monitoring_tasks'].append(new_task)
        
        print(f"✓ 任务 '{task_name}' 添加成功")
        
        # 询问是否配置通知
        if input("\n是否现在配置通知方式? (y/n): ").lower() == 'y':
            self.configure_notifications(task_id)
    
    def configure_notifications(self, task_id: str):
        """配置任务的通知方式"""
        tasks = self.config.get('monitoring_tasks', [])
        task = next((t for t in tasks if t.get('task_id') == task_id), None)
        
        if not task:
            print(f"✗ 找不到任务: {task_id}")
            return
        
        print(f"\n配置任务 '{task.get('task_name')}' 的通知方式")
        print("=" * 50)
        
        while True:
            print("\n请选择要配置的通知方式:")
            print("1. 邮件通知")
            print("2. QQ通知")
            print("3. 短信通知")
            print("4. 完成配置")
            
            choice = input("\n请输入选项 (1-4): ").strip()
            
            if choice == '1':
                self.configure_email_notification(task)
            elif choice == '2':
                self.configure_qq_notification(task)
            elif choice == '3':
                self.configure_sms_notification(task)
            elif choice == '4':
                break
            else:
                print("无效选项，请重新选择")
    
    def configure_email_notification(self, task: Dict[str, Any]):
        """配置邮件通知"""
        print("\n配置邮件通知")
        print("-" * 30)
        
        notifications = task.get('notifications', {})
        email_config = notifications.get('email', {})
        
        # 配置SMTP设置
        print("配置SMTP服务器:")
        smtp_server = input("SMTP服务器 (如: smtp.qq.com): ").strip()
        if smtp_server:
            if 'smtp_config' not in email_config:
                email_config['smtp_config'] = {}
            email_config['smtp_config']['smtp_server'] = smtp_server
        
        smtp_port = input("SMTP端口 (如: 587): ").strip()
        if smtp_port:
            try:
                if 'smtp_config' not in email_config:
                    email_config['smtp_config'] = {}
                email_config['smtp_config']['smtp_port'] = int(smtp_port)
            except ValueError:
                print("✗ 端口必须是数字")
                return
        
        sender = input("发件人邮箱: ").strip()
        if sender:
            if 'smtp_config' not in email_config:
                email_config['smtp_config'] = {}
            email_config['smtp_config']['sender'] = sender
        
        password = input("邮箱密码/授权码: ").strip()
        if password:
            if 'smtp_config' not in email_config:
                email_config['smtp_config'] = {}
            email_config['smtp_config']['password'] = password
        
        # 配置接收者
        print("\n配置邮件接收者:")
        receivers = email_config.get('receivers', [])
        
        while True:
            print(f"\n当前接收者 ({len(receivers)} 个):")
            for i, receiver in enumerate(receivers, 1):
                status = "✓ 启用" if receiver.get('enabled', False) else "✗ 禁用"
                print(f"  {i}. {receiver.get('name', '未命名')} ({receiver.get('email', '未知')}) - {status}")
            
            print("\n操作选项:")
            print("1. 添加接收者")
            print("2. 编辑接收者")
            print("3. 删除接收者")
            print("4. 完成配置")
            
            choice = input("\n请输入选项 (1-4): ").strip()
            
            if choice == '1':
                name = input("接收者名称: ").strip()
                email = input("接收者邮箱: ").strip()
                if name and email:
                    receivers.append({
                        "email": email,
                        "name": name,
                        "enabled": True
                    })
                    print("✓ 接收者添加成功")
            
            elif choice == '2':
                if not receivers:
                    print("没有接收者可以编辑")
                    continue
                
                try:
                    index = int(input(f"请输入接收者编号 (1-{len(receivers)}): ").strip()) - 1
                    if 0 <= index < len(receivers):
                        receiver = receivers[index]
                        name = input(f"新名称 (当前: {receiver.get('name', '')}): ").strip()
                        if name:
                            receiver['name'] = name
                        
                        email = input(f"新邮箱 (当前: {receiver.get('email', '')}): ").strip()
                        if email:
                            receiver['email'] = email
                        
                        enabled = input(f"是否启用 (y/n, 当前: {'是' if receiver.get('enabled', False) else '否'}): ").strip().lower()
                        if enabled in ['y', 'n']:
                            receiver['enabled'] = (enabled == 'y')
                        
                        print("✓ 接收者更新成功")
                    else:
                        print("无效的编号")
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '3':
                if not receivers:
                    print("没有接收者可以删除")
                    continue
                
                try:
                    index = int(input(f"请输入接收者编号 (1-{len(receivers)}): ").strip()) - 1
                    if 0 <= index < len(receivers):
                        removed = receivers.pop(index)
                        print(f"✓ 已删除接收者: {removed.get('name', '未命名')}")
                    else:
                        print("无效的编号")
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '4':
                break
        
        # 启用邮件通知
        enabled_receivers = [r for r in receivers if r.get('enabled', False)]
        if enabled_receivers and email_config.get('smtp_config', {}).get('sender'):
            email_config['enabled'] = True
            print("✓ 邮件通知已启用")
        else:
            email_config['enabled'] = False
            print("⚠ 邮件通知未启用 (缺少必要配置)")
    
    def configure_qq_notification(self, task: Dict[str, Any]):
        """配置QQ通知"""
        print("\n配置QQ通知")
        print("-" * 30)
        
        notifications = task.get('notifications', {})
        qq_config = notifications.get('qq', {})
        
        # 检查邮件配置
        email_config = notifications.get('email', {})
        if not email_config.get('enabled', False):
            print("⚠ QQ通知需要先配置邮件通知")
            return
        
        # 配置QQ邮箱
        qq_emails = qq_config.get('qq_emails', [])
        
        while True:
            print(f"\n当前QQ邮箱 ({len(qq_emails)} 个):")
            for i, qq_email in enumerate(qq_emails, 1):
                status = "✓ 启用" if qq_email.get('enabled', False) else "✗ 禁用"
                print(f"  {i}. {qq_email.get('name', '未命名')} ({qq_email.get('email', '未知')}) - {status}")
            
            print("\n操作选项:")
            print("1. 添加QQ邮箱")
            print("2. 编辑QQ邮箱")
            print("3. 删除QQ邮箱")
            print("4. 完成配置")
            
            choice = input("\n请输入选项 (1-4): ").strip()
            
            if choice == '1':
                name = input("QQ邮箱名称: ").strip()
                email = input("QQ邮箱地址: ").strip()
                if name and email:
                    qq_emails.append({
                        "email": email,
                        "name": name,
                        "enabled": True
                    })
                    print("✓ QQ邮箱添加成功")
            
            elif choice == '2':
                if not qq_emails:
                    print("没有QQ邮箱可以编辑")
                    continue
                
                try:
                    index = int(input(f"请输入QQ邮箱编号 (1-{len(qq_emails)}): ").strip()) - 1
                    if 0 <= index < len(qq_emails):
                        qq_email = qq_emails[index]
                        name = input(f"新名称 (当前: {qq_email.get('name', '')}): ").strip()
                        if name:
                            qq_email['name'] = name
                        
                        email = input(f"新邮箱 (当前: {qq_email.get('email', '')}): ").strip()
                        if email:
                            qq_email['email'] = email
                        
                        enabled = input(f"是否启用 (y/n, 当前: {'是' if qq_email.get('enabled', False) else '否'}): ").strip().lower()
                        if enabled in ['y', 'n']:
                            qq_email['enabled'] = (enabled == 'y')
                        
                        print("✓ QQ邮箱更新成功")
                    else:
                        print("无效的编号")
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '3':
                if not qq_emails:
                    print("没有QQ邮箱可以删除")
                    continue
                
                try:
                    index = int(input(f"请输入QQ邮箱编号 (1-{len(qq_emails)}): ").strip()) - 1
                    if 0 <= index < len(qq_emails):
                        removed = qq_emails.pop(index)
                        print(f"✓ 已删除QQ邮箱: {removed.get('name', '未命名')}")
                    else:
                        print("无效的编号")
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '4':
                break
        
        # 启用QQ通知
        enabled_qq_emails = [q for q in qq_emails if q.get('enabled', False)]
        if enabled_qq_emails:
            qq_config['enabled'] = True
            print("✓ QQ通知已启用")
        else:
            qq_config['enabled'] = False
            print("⚠ QQ通知未启用 (没有启用的QQ邮箱)")
    
    def configure_sms_notification(self, task: Dict[str, Any]):
        """配置短信通知"""
        print("\n配置短信通知")
        print("-" * 30)
        
        notifications = task.get('notifications', {})
        sms_config = notifications.get('sms', {})
        
        # 配置短信服务
        print("配置短信服务:")
        provider = input("短信服务提供商 (如: aliyun): ").strip()
        if provider:
            sms_config['provider'] = provider
        
        access_key_id = input("Access Key ID: ").strip()
        if access_key_id:
            sms_config['access_key_id'] = access_key_id
        
        access_key_secret = input("Access Key Secret: ").strip()
        if access_key_secret:
            sms_config['access_key_secret'] = access_key_secret
        
        sign_name = input("短信签名: ").strip()
        if sign_name:
            sms_config['sign_name'] = sign_name
        
        template_code = input("短信模板代码: ").strip()
        if template_code:
            sms_config['template_code'] = template_code
        
        # 配置手机号
        phone_numbers = sms_config.get('phone_numbers', [])
        
        while True:
            print(f"\n当前手机号 ({len(phone_numbers)} 个):")
            for i, phone in enumerate(phone_numbers, 1):
                status = "✓ 启用" if phone.get('enabled', False) else "✗ 禁用"
                print(f"  {i}. {phone.get('name', '未命名')} ({phone.get('phone', '未知')}) - {status}")
            
            print("\n操作选项:")
            print("1. 添加手机号")
            print("2. 编辑手机号")
            print("3. 删除手机号")
            print("4. 完成配置")
            
            choice = input("\n请输入选项 (1-4): ").strip()
            
            if choice == '1':
                name = input("手机号名称: ").strip()
                phone = input("手机号码: ").strip()
                if name and phone:
                    phone_numbers.append({
                        "phone": phone,
                        "name": name,
                        "enabled": True
                    })
                    print("✓ 手机号添加成功")
            
            elif choice == '2':
                if not phone_numbers:
                    print("没有手机号可以编辑")
                    continue
                
                try:
                    index = int(input(f"请输入手机号编号 (1-{len(phone_numbers)}): ").strip()) - 1
                    if 0 <= index < len(phone_numbers):
                        phone_obj = phone_numbers[index]
                        name = input(f"新名称 (当前: {phone_obj.get('name', '')}): ").strip()
                        if name:
                            phone_obj['name'] = name
                        
                        phone = input(f"新手机号 (当前: {phone_obj.get('phone', '')}): ").strip()
                        if phone:
                            phone_obj['phone'] = phone
                        
                        enabled = input(f"是否启用 (y/n, 当前: {'是' if phone_obj.get('enabled', False) else '否'}): ").strip().lower()
                        if enabled in ['y', 'n']:
                            phone_obj['enabled'] = (enabled == 'y')
                        
                        print("✓ 手机号更新成功")
                    else:
                        print("无效的编号")
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '3':
                if not phone_numbers:
                    print("没有手机号可以删除")
                    continue
                
                try:
                    index = int(input(f"请输入手机号编号 (1-{len(phone_numbers)}): ").strip()) - 1
                    if 0 <= index < len(phone_numbers):
                        removed = phone_numbers.pop(index)
                        print(f"✓ 已删除手机号: {removed.get('name', '未命名')}")
                    else:
                        print("无效的编号")
                except ValueError:
                    print("请输入有效的数字")
            
            elif choice == '4':
                break
        
        # 启用短信通知
        enabled_phones = [p for p in phone_numbers if p.get('enabled', False)]
        required_fields = ['provider', 'access_key_id', 'access_key_secret', 'sign_name', 'template_code']
        has_required_config = all(sms_config.get(field) for field in required_fields)
        
        if enabled_phones and has_required_config:
            sms_config['enabled'] = True
            print("✓ 短信通知已启用")
        else:
            sms_config['enabled'] = False
            print("⚠ 短信通知未启用 (缺少必要配置)")
    
    def edit_task(self):
        """编辑任务"""
        tasks = self.config.get('monitoring_tasks', [])
        if not tasks:
            print("没有配置任何任务")
            return
        
        print("\n选择要编辑的任务:")
        for i, task in enumerate(tasks, 1):
            task_name = task.get('task_name', f'任务{i}')
            enabled = task.get('enabled', False)
            status = "✓ 启用" if enabled else "✗ 禁用"
            print(f"{i}. {task_name} ({status})")
        
        try:
            choice = int(input(f"\n请输入任务编号 (1-{len(tasks)}): ").strip())
            if 1 <= choice <= len(tasks):
                task = tasks[choice - 1]
                self.edit_task_details(task)
            else:
                print("无效的任务编号")
        except ValueError:
            print("请输入有效的数字")
    
    def edit_task_details(self, task: Dict[str, Any]):
        """编辑任务详情"""
        task_name = task.get('task_name', '未知任务')
        print(f"\n编辑任务: {task_name}")
        print("=" * 40)
        
        while True:
            print("\n请选择要编辑的内容:")
            print("1. 基本信息")
            print("2. 通知配置")
            print("3. 启用/禁用任务")
            print("4. 返回")
            
            choice = input("\n请输入选项 (1-4): ").strip()
            
            if choice == '1':
                self.edit_task_basic_info(task)
            elif choice == '2':
                self.configure_notifications(task.get('task_id', ''))
            elif choice == '3':
                current_status = "启用" if task.get('enabled', False) else "禁用"
                new_status = input(f"当前状态: {current_status}，是否切换? (y/n): ").strip().lower()
                if new_status == 'y':
                    task['enabled'] = not task.get('enabled', False)
                    status = "启用" if task['enabled'] else "禁用"
                    print(f"✓ 任务已{status}")
            elif choice == '4':
                break
            else:
                print("无效选项，请重新选择")
    
    def edit_task_basic_info(self, task: Dict[str, Any]):
        """编辑任务基本信息"""
        print("\n编辑基本信息:")
        print("-" * 20)
        
        # 任务名称
        current_name = task.get('task_name', '')
        new_name = input(f"任务名称 (当前: {current_name}): ").strip()
        if new_name:
            task['task_name'] = new_name
        
        # 订单号
        current_order_id = task.get('order_id', '')
        new_order_id = input(f"订单号 (当前: {current_order_id}): ").strip()
        if new_order_id:
            task['order_id'] = new_order_id
        
        # 用户ID
        current_user_id = task.get('user_id', '')
        new_user_id = input(f"用户ID (当前: {current_user_id}): ").strip()
        if new_user_id:
            try:
                task['user_id'] = int(new_user_id)
            except ValueError:
                print("✗ 用户ID必须是数字")
        
        # API地址
        current_url = task.get('url', '')
        new_url = input(f"API地址 (当前: {current_url}): ").strip()
        if new_url:
            task['url'] = new_url
        
        print("✓ 基本信息更新完成")
    
    def delete_task(self):
        """删除任务"""
        tasks = self.config.get('monitoring_tasks', [])
        if not tasks:
            print("没有配置任何任务")
            return
        
        print("\n选择要删除的任务:")
        for i, task in enumerate(tasks, 1):
            task_name = task.get('task_name', f'任务{i}')
            enabled = task.get('enabled', False)
            status = "✓ 启用" if enabled else "✗ 禁用"
            print(f"{i}. {task_name} ({status})")
        
        try:
            choice = int(input(f"\n请输入任务编号 (1-{len(tasks)}): ").strip())
            if 1 <= choice <= len(tasks):
                task = tasks[choice - 1]
                task_name = task.get('task_name', f'任务{choice}')
                
                confirm = input(f"\n确认删除任务 '{task_name}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    removed = tasks.pop(choice - 1)
                    print(f"✓ 任务 '{removed.get('task_name', '未知')}' 已删除")
                else:
                    print("取消删除")
            else:
                print("无效的任务编号")
        except ValueError:
            print("请输入有效的数字")
    
    def run(self):
        """运行配置管理器"""
        print("小米汽车订单监控 - 配置管理器")
        print("=" * 50)
        
        while True:
            self.show_task_summary()
            
            print("\n请选择操作:")
            print("1. 添加新任务")
            print("2. 编辑任务")
            print("3. 删除任务")
            print("4. 保存配置")
            print("5. 退出")
            
            choice = input("\n请输入选项 (1-5): ").strip()
            
            if choice == '1':
                self.add_task()
            elif choice == '2':
                self.edit_task()
            elif choice == '3':
                self.delete_task()
            elif choice == '4':
                self.save_config()
            elif choice == '5':
                if input("\n是否保存配置? (y/n): ").strip().lower() == 'y':
                    self.save_config()
                print("已退出")
                break
            else:
                print("无效选项，请重新选择")


def main():
    """主函数"""
    config_manager = ConfigManager()
    config_manager.run()


if __name__ == "__main__":
    main() 