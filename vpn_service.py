import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import aiohttp
import json
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD

class VPNService:
    """Service for managing VPN users through Marzban API"""
    
    def __init__(self):
        self.base_url = MARZBAN_URL.rstrip('/')
        self.username = MARZBAN_USERNAME
        self.password = MARZBAN_PASSWORD
        self.access_token = None
        self.token_expires_at = None
        
    async def _get_access_token(self) -> Optional[str]:
        """Get or refresh access token for Marzban API"""
        # Check if token is still valid
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare authentication data
                auth_data = aiohttp.FormData()
                auth_data.add_field('username', self.username)
                auth_data.add_field('password', self.password)
                
                # Make token request
                async with session.post(
                    f"{self.base_url}/api/admin/token",
                    data=auth_data
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get("access_token")
                        
                        # Set token expiration (assume 1 hour if not provided)
                        expires_in = token_data.get("expires_in", 3600)
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 minute early
                        
                        logging.info("Successfully obtained Marzban access token")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logging.error(f"Failed to get access token: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logging.error(f"Error getting access token: {e}")
            return None
    
    async def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated API request to Marzban"""
        token = await self._get_access_token()
        if not token:
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{endpoint}"
                
                if method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logging.error(f"API request failed: {response.status} - {error_text}")
                            return None
                            
                elif method.upper() == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status in [200, 201]:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logging.error(f"API request failed: {response.status} - {error_text}")
                            return None
                            
                elif method.upper() == "PUT":
                    async with session.put(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logging.error(f"API request failed: {response.status} - {error_text}")
                            return None
                            
        except Exception as e:
            logging.error(f"Error making API request: {e}")
            return None
    
    def _generate_username(self, user_id: int, country_id: str) -> str:
        """Generate unique username for VPN user"""
        return f"tg_{user_id}_{country_id}_{int(datetime.now().timestamp())}"
    
    def _get_country_inbounds(self, country_id: str) -> list:
        """Get inbound tags based on country selection"""
        # Based on your Marzban config, you only have VLESS TCP REALITY
        # All countries will use the same inbound for now
        return ["VLESS TCP REALITY"]
    
    async def create_vpn_user(self, user_id: int, country_id: str, period_months: int) -> Dict[str, Any]:
        """Create a new VPN user in Marzban"""
        try:
            # Generate unique username
            username = self._generate_username(user_id, country_id)
            
            # Calculate expiry date
            expire_days = period_months * 30  # Approximate days per month
            expire_timestamp = int((datetime.now() + timedelta(days=expire_days)).timestamp())
            
            # Get inbounds for the selected country
            inbounds = self._get_country_inbounds(country_id)
            
            # Prepare user data - only enable VLESS since that's what your server supports
            user_data = {
                "username": username,
                "proxies": {
                    "vless": {}  # Only VLESS is enabled on your server
                },
                "inbounds": {
                    "VLESS TCP REALITY": ["VLESS TCP REALITY"]  # Use your actual inbound tag
                },
                "expire": expire_timestamp,
                "data_limit": 0,  # Unlimited data
                "data_limit_reset_strategy": "no_reset",
                "status": "active",
                "note": f"Telegram User {user_id} - {country_id.title()} - {period_months}m",
                "on_hold_timeout": "2023-11-03T20:30:00",
                "on_hold_expire_duration": 0
            }
            
            # Create user via API
            response = await self._make_api_request("POST", "/api/user", user_data)
            
            if response:
                # Get user details to retrieve subscription URL
                user_details = await self._make_api_request("GET", f"/api/user/{username}")
                
                if user_details:
                    subscription_url = user_details.get("subscription_url", "")
                    
                    logging.info(f"Created VPN user: {username} for Telegram user {user_id}")
                    
                    return {
                        "success": True,
                        "username": username,
                        "subscription_url": subscription_url,
                        "expire_days": expire_days,
                        "country": country_id,
                        "period_months": period_months,
                        "user_details": user_details
                    }
                else:
                    logging.error(f"Failed to get user details after creation: {username}")
                    return {
                        "success": False,
                        "error": "Failed to retrieve user details after creation"
                    }
            else:
                logging.error(f"Failed to create VPN user: {username}")
                return {
                    "success": False,
                    "error": "Failed to create user in Marzban"
                }
                
        except Exception as e:
            logging.error(f"Error creating VPN user: {e}")
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}"
            }
    
    async def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information from Marzban"""
        try:
            response = await self._make_api_request("GET", f"/api/user/{username}")
            return response
        except Exception as e:
            logging.error(f"Error getting user info: {e}")
            return None
    
    async def update_user(self, username: str, user_data: Dict) -> Optional[Dict]:
        """Update user in Marzban"""
        try:
            response = await self._make_api_request("PUT", f"/api/user/{username}", user_data)
            return response
        except Exception as e:
            logging.error(f"Error updating user: {e}")
            return None
    
    async def delete_user(self, username: str) -> bool:
        """Delete user from Marzban"""
        try:
            token = await self._get_access_token()
            if not token:
                return False
                
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/user/{username}"
                async with session.delete(url, headers=headers) as response:
                    if response.status in [200, 204, 404]:  # 404 means already deleted
                        logging.info(f"Successfully deleted user: {username}")
                        return True
                    else:
                        error_text = await response.text()
                        logging.warning(f"Delete user failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logging.error(f"Error deleting user: {e}")
            return False
    
    async def get_user_usage(self, username: str) -> Optional[Dict]:
        """Get user usage statistics"""
        try:
            user_info = await self.get_user_info(username)
            if user_info:
                return {
                    "used_traffic": user_info.get("used_traffic", 0),
                    "data_limit": user_info.get("data_limit", 0),
                    "expire": user_info.get("expire"),
                    "status": user_info.get("status", "unknown")
                }
            return None
        except Exception as e:
            logging.error(f"Error getting user usage: {e}")
            return None
    
    def format_user_key_message(self, vpn_result: Dict, tariff_name: str, period_text: str) -> str:
        """Format the VPN key message for the user"""
        if not vpn_result.get("success"):
            return "❌ Ошибка при создании VPN ключа"
            
        subscription_url = vpn_result.get("subscription_url", "")
        username = vpn_result.get("username", "")
        expire_days = vpn_result.get("expire_days", 30)
        
        # Calculate expiry date string
        expiry_date = datetime.now() + timedelta(days=expire_days)
        expiry_str = expiry_date.strftime("%d.%m.%Y")
        
        message = f"""✅ <b>VPN ключ успешно создан!</b>

<b>Тариф:</b> {tariff_name}
<b>Период:</b> {period_text}
<b>Активен до:</b> {expiry_str}

<b>🔑 Ваш ключ подписки:</b>
<code>{subscription_url}</code>

<i>Нажмите на ключ, чтобы скопировать его</i>

📱 Используйте инструкции для подключения к VPN"""
        
        return message
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Marzban API"""
        try:
            token = await self._get_access_token()
            if not token:
                return {
                    "success": False,
                    "error": "Failed to obtain access token"
                }
            
            # Try to get system stats to test connection
            response = await self._make_api_request("GET", "/api/system")
            
            if response:
                return {
                    "success": True,
                    "message": "Successfully connected to Marzban API",
                    "system_info": response
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to get system information"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }
