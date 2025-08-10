# -*- coding: utf-8 -*-
# @Author  : Ree
# @Date    : 2025-01-08
# @Description: 小米汽车订单状态监控脚本 - 多任务多邮箱配置版（内存存储）

import requests
import json
import time
import smtplib
import schedule
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from typing import Dict, Any, Optional, List
import threading
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xiaomi_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MemoryStorage:
    """内存存储类"""
    
    def __init__(self):
        """初始化内存存储"""
        self.status_history = defaultdict(list)  # 按任务ID存储状态历史
        self.max_history_size = 1000  # 每个任务最大历史记录数
    
    def save_status(self, task_id: str, status: Dict[str, Any], change_detected: bool = False):
        """
        保存状态到内存
        
        Args:
            task_id: 任务ID
            status: 状态信息
            change_detected: 是否检测到变化
        """
        try:
            status_record = {
                'order_id': status['order_id'],
                'order_status': status['order_status'],
                'order_status_name': status['order_status_name'],
                'check_time': datetime.now().isoformat(),
                'change_detected': change_detected
            }
            
            self.status_history[task_id].append(status_record)
            
            # 限制历史记录数量
            if len(self.status_history[task_id]) > self.max_history_size:
                self.status_history[task_id] = self.status_history[task_id][-self.max_history_size:]
            
            logger.debug(f"任务 '{task_id}' 状态已保存到内存")
            
        except Exception as e:
            logger.error(f"保存状态到内存失败: {str(e)}")
    
    def get_latest_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取最新的状态记录
        
        Args:
            task_id: 任务ID
            
        Returns:
            最新的状态记录，如果没有则返回None
        """
        history = self.status_history.get(task_id, [])
        if history:
            return history[-1]
        return None
    
    def get_status_history(self, task_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取状态历史记录
        
        Args:
            task_id: 任务ID
            limit: 返回记录数量限制
            
        Returns:
            状态历史记录列表
        """
        history = self.status_history.get(task_id, [])
        return history[-limit:] if history else []
    
    def clear_history(self, task_id: str = None):
        """
        清除历史记录
        
        Args:
            task_id: 任务ID，如果为None则清除所有历史
        """
        if task_id:
            self.status_history[task_id].clear()
            logger.info(f"已清除任务 '{task_id}' 的历史记录")
        else:
            self.status_history.clear()
            logger.info("已清除所有历史记录")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'total_tasks': len(self.status_history),
            'total_records': sum(len(history) for history in self.status_history.values()),
            'task_details': {}
        }
        
        for task_id, history in self.status_history.items():
            stats['task_details'][task_id] = {
                'record_count': len(history),
                'latest_status': history[-1] if history else None
            }
        
        return stats


class SingleTaskMonitor:
    """单个任务监控器"""
    
    def __init__(self, task_config: Dict[str, Any], storage: MemoryStorage):
        """
        初始化单个任务监控器
        
        Args:
            task_config: 单个任务的配置字典
            storage: 内存存储实例
        """
        self.task_config = task_config
        self.task_id = task_config['task_id']
        self.task_name = task_config.get('task_name', f'任务{self.task_id}')
        self.order_id = task_config['order_id']
        self.user_id = task_config['user_id']
        self.headers = task_config['headers']
        self.url = task_config['url']
        self.check_interval = task_config.get('check_interval', 30)  # 默认30分钟检查一次
        self.notifications = task_config.get('notifications', {})
        self.storage = storage
        
        # 获取初始状态
        self.last_status = self.get_current_status()
        if self.last_status:
            logger.info(f"任务 '{self.task_name}' 初始订单状态: VID={self.last_status['order_status']}")
    
    def get_current_status(self) -> Optional[Dict[str, Any]]:
        """
        获取当前订单状态
        
        Returns:
            订单状态信息字典，如果获取失败返回None
        """
        try:
            payload = [
                {
                    "orderId": self.order_id,
                    "userId": self.user_id
                }
            ]
            
            response = requests.post(
                self.url, 
                data=json.dumps(payload), 
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and 'data' in data:
                    buy_car_info = data['data'].get('buyCarInfo', {})
                    return {
                        'order_status': buy_car_info.get('vid'),
                        'order_status_name': buy_car_info.get('vid'),
                        'order_id': self.order_id,
                        'task_id': self.task_id,
                        'task_name': self.task_name
                    }
                else:
                    logger.warning(f"任务 '{self.task_name}' API返回错误: {data}")
                    return None
            else:
                logger.error(f"任务 '{self.task_name}' HTTP请求失败: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"任务 '{self.task_name}' 网络请求异常: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"任务 '{self.task_name}' 获取订单状态失败: {str(e)}")
            return None
    
    def check_status_change(self) -> bool:
        """检查状态变化"""
        current_status = self.get_current_status()
        
        if not current_status:
            logger.warning(f"任务 '{self.task_name}' 无法获取当前状态")
            return False
        
        # 保存当前状态到内存
        self.storage.save_status(self.task_id, current_status, False)
        
        # 检查是否有变化
        if not self.last_status:
            self.last_status = current_status
            logger.info(f"任务 '{self.task_name}' 首次获取状态: {current_status['order_status_name']}")
            return False
        
        if (current_status['order_status'] != self.last_status['order_status'] or
            current_status['order_status_name'] != self.last_status['order_status_name']):
            
            logger.info(f"任务 '{self.task_name}' 状态变化: {self.last_status['order_status_name']} -> {current_status['order_status_name']}")
            
            # 保存变化状态到内存
            self.storage.save_status(self.task_id, current_status, True)
            
            # 发送通知
            self.notify_status_change(self.last_status, current_status)
            
            self.last_status = current_status
            return True
        
        logger.debug(f"任务 '{self.task_name}' 状态无变化: {current_status['order_status_name']}")
        return False
    
    def send_email_notification(self, old_status: Dict[str, Any], new_status: Dict[str, Any]):
        """发送邮件通知"""
        email_config = self.notifications.get('email', {})
        if not email_config.get('enabled', False):
            return
        
        smtp_config = email_config.get('smtp_config', {})
        receivers = email_config.get('receivers', [])
        
        if not smtp_config or not receivers:
            logger.warning(f"任务 '{self.task_name}' 邮件配置不完整")
            return
        
        enabled_receivers = [r for r in receivers if r.get('enabled', False)]
        if not enabled_receivers:
            logger.warning(f"任务 '{self.task_name}' 没有启用的邮件接收者")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['sender']
            msg['To'] = ', '.join([r['email'] for r in enabled_receivers])
            msg['Subject'] = f"小米汽车订单状态变化通知 - {self.task_name}"
            
            body = f"""
            订单状态发生变化！
            
            任务名称: {self.task_name}
            订单号: {self.order_id}
            变化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            状态变化:
            从: {old_status['order_status_name']} (状态码: {old_status['order_status']})
            到: {new_status['order_status_name']} (状态码: {new_status['order_status']})
            
            请及时查看订单详情。
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['sender'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"任务 '{self.task_name}' 邮件通知发送成功")
            
        except Exception as e:
            logger.error(f"任务 '{self.task_name}' 邮件通知发送失败: {str(e)}")
    
    def send_qq_notification(self, old_status: Dict[str, Any], new_status: Dict[str, Any]):
        """发送QQ通知"""
        qq_config = self.notifications.get('qq', {})
        if not qq_config.get('enabled', False):
            return
        
        email_config = self.notifications.get('email', {})
        if not email_config.get('enabled', False):
            logger.warning(f"任务 '{self.task_name}' QQ通知需要邮件配置")
            return
        
        qq_emails = qq_config.get('qq_emails', [])
        enabled_qq_emails = [q for q in qq_emails if q.get('enabled', False)]
        
        if not enabled_qq_emails:
            logger.warning(f"任务 '{self.task_name}' 没有启用的QQ邮箱")
            return
        
        smtp_config = email_config.get('smtp_config', {})
        
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['sender']
            msg['To'] = ', '.join([q['email'] for q in enabled_qq_emails])
            msg['Subject'] = f"小米汽车订单状态变化通知 - {self.task_name}"
            
            body = f"""
            订单状态发生变化！
            
            任务名称: {self.task_name}
            订单号: {self.order_id}
            变化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            状态变化:
            从: {old_status['order_status_name']} (状态码: {old_status['order_status']})
            到: {new_status['order_status_name']} (状态码: {new_status['order_status']})
            
            请及时查看订单详情。
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['sender'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"任务 '{self.task_name}' QQ通知发送成功")
            
        except Exception as e:
            logger.error(f"任务 '{self.task_name}' QQ通知发送失败: {str(e)}")
    
    def send_sms_notification(self, old_status: Dict[str, Any], new_status: Dict[str, Any]):
        """发送短信通知"""
        sms_config = self.notifications.get('sms', {})
        if not sms_config.get('enabled', False):
            return
        
        phone_numbers = sms_config.get('phone_numbers', [])
        enabled_phones = [p for p in phone_numbers if p.get('enabled', False)]
        
        if not enabled_phones:
            logger.warning(f"任务 '{self.task_name}' 没有启用的手机号")
            return
        
        try:
            # 这里可以集成短信服务
            logger.info(f"任务 '{self.task_name}' 短信通知功能需要配置短信服务")
            logger.info(f"启用的手机号: {', '.join([p['phone'] for p in enabled_phones])}")
            
        except Exception as e:
            logger.error(f"任务 '{self.task_name}' 短信通知发送失败: {str(e)}")
    
    def notify_status_change(self, old_status: Dict[str, Any], new_status: Dict[str, Any]):
        """通知状态变化"""
        logger.info(f"任务 '{self.task_name}' 开始发送状态变化通知")
        
        # 发送邮件通知
        self.send_email_notification(old_status, new_status)
        
        # 发送QQ通知
        self.send_qq_notification(old_status, new_status)
        
        # 发送短信通知
        self.send_sms_notification(old_status, new_status)
    
    def monitor_task(self):
        """执行监控任务"""
        try:
            logger.info(f"任务 '{self.task_name}' 开始检查订单状态")
            self.check_status_change()
        except Exception as e:
            logger.error(f"任务 '{self.task_name}' 监控任务执行失败: {str(e)}")
    
    def start_monitoring(self):
        """开始监控"""
        logger.info(f"任务 '{self.task_name}' 开始监控，检查间隔: {self.check_interval} 分钟")
        
        # 设置定时任务
        schedule.every(self.check_interval).minutes.do(self.monitor_task)
        
        # 立即执行一次检查
        self.monitor_task()
        
        # 持续运行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次定时任务


class MultiTaskMonitor:
    """多任务监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化多任务监控器
        
        Args:
            config: 包含多个任务配置的字典
        """
        self.config = config
        self.global_settings = config.get('global_settings', {})
        self.tasks = config.get('monitoring_tasks', [])
        self.enabled_tasks = [task for task in self.tasks if task.get('enabled', False)]
        
        # 初始化内存存储
        self.storage = MemoryStorage()
        
        # 创建各个任务的监控器
        self.monitors = {}
        for task in self.enabled_tasks:
            task_id = task['task_id']
            self.monitors[task_id] = SingleTaskMonitor(task, self.storage)
        
        logger.info(f"多任务监控器初始化完成，共 {len(self.enabled_tasks)} 个启用任务")
    
    def start_monitoring(self):
        """开始多任务监控"""
        if not self.monitors:
            logger.warning("没有启用的监控任务")
            return
        
        logger.info("开始多任务监控...")
        
        # 为每个任务创建独立的线程
        threads = []
        for task_id, monitor in self.monitors.items():
            thread = threading.Thread(
                target=monitor.start_monitoring,
                name=f"Monitor-{task_id}",
                daemon=True
            )
            threads.append(thread)
            thread.start()
            logger.info(f"任务 '{monitor.task_name}' 监控线程已启动")
        
        # 等待所有线程
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭监控...")
        finally:
            self.close()
    
    def close(self):
        """关闭所有监控器"""
        logger.info("正在关闭监控器...")
        # 显示统计信息
        stats = self.storage.get_statistics()
        logger.info(f"监控统计: {stats['total_tasks']} 个任务，{stats['total_records']} 条记录")
        logger.info("所有监控器已关闭")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        return self.storage.get_statistics()


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_file = 'xiaomi_config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("成功加载配置文件")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    
    # 如果配置文件不存在或加载失败，使用默认配置
    logger.warning("使用默认配置")
    config = {
        "global_settings": {
            "check_interval": 15,
            "log_level": "INFO"
        },
        "monitoring_tasks": [
            {
                "task_id": "default_task",
                "task_name": "默认任务",
                "enabled": True,
                "order_id": "5256772385302521",
                "user_id": 1014566219,
                "url": "https://api.retail.xiaomiev.com/mtop/car-order/order/detail",
                "headers": {
                    'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.61(0x18003d34) NetType/4G Language/zh_CN",
                    'Accept-Encoding': "gzip,compress,br,deflate",
                    'Content-Type': "application/json",
                    'configSelectorVersion': "2",
                    'content-type': "application/json; charset=utf-8",
                    'deviceappversion': "1.16.0",
                    'x-user-agent': "channel/car platform/car.wxlite",
                    'Referer': "https://servicewechat.com/wx183d85f5e5e273c6/101/page-frame.html",
                    'Cookie': "serviceTokenCar=;"
                },
                "notifications": {
                    "email": {
                        "enabled": False,
                        "smtp_config": {
                            "smtp_server": "smtp.gmail.com",
                            "smtp_port": 587,
                            "sender": "your_email@gmail.com",
                            "password": "your_app_password"
                        },
                        "receivers": [
                            {
                                "email": "your_email@gmail.com",
                                "name": "默认接收者",
                                "enabled": True
                            }
                        ]
                    },
                    "qq": {
                        "enabled": False,
                        "qq_emails": []
                    },
                    "sms": {
                        "enabled": False,
                        "provider": "aliyun",
                        "access_key_id": "your_access_key_id",
                        "access_key_secret": "your_access_key_secret",
                        "sign_name": "your_sign_name",
                        "template_code": "your_template_code",
                        "phone_numbers": []
                    }
                }
            }
        ]
    }
    
    return config


def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 创建多任务监控器
        monitor = MultiTaskMonitor(config)
        
        # 开始监控
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("监控已停止")
    except Exception as e:
        logger.error(f"监控过程中发生错误: {str(e)}")
    finally:
        if 'monitor' in locals():
            monitor.close()


if __name__ == "__main__":
    main() 