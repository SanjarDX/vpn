import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import hashlib
import random
import string

from marzban_client import MarzbanClient
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD

class VPNService:
    def __init__(self):
        self.marzban_url = MARZBAN_URL
        self.marzban_username = MARZBAN_USERNAME
        self.marzban_password = MARZBAN_PASSWORD
        
    def generate_username(self, user_id: int, country_id: str) -> str:
        """Generate unique username for VPN user"""
        # Use shorter format to stay within 32 character limit
        timestamp = int(datetime.now().timestamp()) % 1000000  # Last 6 digits
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        username = f"u{user_id}_{country_id[:3]}{timestamp}{random_suffix}"
        
        # Ensure username is within 3-32 character limit and only contains valid characters
        username = username.lower().replace('-', '_')  # Replace hyphens with underscores
        username = ''.join(c for c in username if c.isalnum() or c == '_')
        
        # Ensure it starts with a letter and is not too long
        if not username[0].isalpha():
            username = 'u' + username
        if len(username) > 32:
            username = username[:32]
        if len(username) < 3:
            username = username + 'aa'
            
        return username
    
    def get_data_limit_gb(self, country_id: str) -> int:
        """Get data limit in GB based on country/tariff"""
        data_limits = {
            "russia": 100,      # 100GB for Russia tariff
            "multi": 1000,      # 1TB for Multi tariff
            "netherlands": 500, # 500GB for Netherlands
            "germany": 500,     # 500GB for Germany
            "france": 500,      # 500GB for France
            "usa": 500          # 500GB for USA
        }
        return data_limits.get(country_id, 100)
    
    def get_proxies_for_country(self, country_id: str) -> list:
        """Get appropriate proxy types for each country"""
        # Based on your Marzban configuration, only VLESS is enabled
        # You can add more protocols later when you configure them in Marzban
        return ["vless"]
    
    async def create_vpn_user(self, user_id: int, country_id: str, period_months: int) -> Dict:
        """Create a new VPN user and return subscription details"""
        try:
            username = self.generate_username(user_id, country_id)
            data_limit_gb = self.get_data_limit_gb(country_id)
            proxies = self.get_proxies_for_country(country_id)
            expire_days = period_months * 30  # Convert months to days
            
            async with MarzbanClient(self.marzban_url, self.marzban_username, self.marzban_password) as client:
                # Create user in Marzban
                user_data = await client.create_user(
                    username=username,
                    data_limit=data_limit_gb,
                    expire_days=expire_days,
                    proxies=proxies
                )
                
                # Get subscription URL
                subscription_url = await client.get_user_subscription(username)
                
                return {
                    "success": True,
                    "username": username,
                    "subscription_url": subscription_url,
                    "data_limit_gb": data_limit_gb,
                    "expire_days": expire_days,
                    "proxies": proxies,
                    "country": country_id,
                    "user_data": user_data
                }
                
        except Exception as e:
            logging.error(f"Failed to create VPN user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def extend_user_subscription(self, username: str, extend_months: int) -> Dict:
        """Extend existing user subscription"""
        try:
            extend_days = extend_months * 30
            
            async with MarzbanClient(self.marzban_url, self.marzban_username, self.marzban_password) as client:
                user_data = await client.extend_user(username, extend_days)
                
                return {
                    "success": True,
                    "username": username,
                    "extended_days": extend_days,
                    "user_data": user_data
                }
                
        except Exception as e:
            logging.error(f"Failed to extend user subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_info(self, username: str) -> Dict:
        """Get user information and usage statistics"""
        try:
            async with MarzbanClient(self.marzban_url, self.marzban_username, self.marzban_password) as client:
                user_data = await client.get_user(username)
                subscription_url = await client.get_user_subscription(username)
                
                return {
                    "success": True,
                    "username": username,
                    "subscription_url": subscription_url,
                    "user_data": user_data
                }
                
        except Exception as e:
            logging.error(f"Failed to get user info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_user(self, username: str) -> Dict:
        """Delete a VPN user"""
        try:
            async with MarzbanClient(self.marzban_url, self.marzban_username, self.marzban_password) as client:
                await client.delete_user(username)
                
                return {
                    "success": True,
                    "username": username
                }
                
        except Exception as e:
            logging.error(f"Failed to delete user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_stats(self) -> Dict:
        """Get system statistics"""
        try:
            async with MarzbanClient(self.marzban_url, self.marzban_username, self.marzban_password) as client:
                stats = await client.get_system_stats()
                
                return {
                    "success": True,
                    "stats": stats
                }
                
        except Exception as e:
            logging.error(f"Failed to get system stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def format_user_key_message(self, vpn_result: Dict, tariff_name: str, period: str) -> str:
        """Format VPN key message for user"""
        if not vpn_result.get("success"):
            return "❌ Произошла ошибка при создании VPN ключа. Обратитесь в поддержку."
        
        subscription_url = vpn_result.get("subscription_url", "")
        data_limit = vpn_result.get("data_limit_gb", 0)
        expire_days = vpn_result.get("expire_days", 0)
        
        return f"""🎉 <b>Ваш VPN ключ готов!</b>

🌐 <b>Тариф:</b> {tariff_name}
⏱ <b>Период:</b> {period}
📊 <b>Лимит трафика:</b> {data_limit} ГБ
📅 <b>Действует:</b> {expire_days} дней

🔑 <b>Ключ подписки:</b>
<code>{subscription_url}</code>

📱 <b>Инструкция по подключению:</b>
1. Скопируйте ключ выше
2. Откройте приложение VPN
3. Добавьте подписку из буфера обмена

✅ Ключ активирован и готов к использованию!"""
