import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

class MarzbanClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Authenticate and get access token"""
        auth_data = {
            "username": self.username,
            "password": self.password
        }
        
        async with self.session.post(
            f"{self.base_url}/api/admin/token",
            data=auth_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                self.token = result["access_token"]
                logging.info("Successfully authenticated with Marzban")
            else:
                raise Exception(f"Authentication failed: {response.status}")
    
    def _get_headers(self):
        """Get headers with authorization token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def create_user(self, username: str, data_limit: int, expire_days: int, 
                         proxies: List[str] = None) -> Dict:
        """Create a new VPN user"""
        if proxies is None:
            proxies = ["vless", "vmess", "trojan", "shadowsocks"]
            
        expire_date = datetime.now() + timedelta(days=expire_days)
        
        user_data = {
            "username": username,
            "proxies": {proxy: {} for proxy in proxies},
            "data_limit": data_limit * 1024 * 1024 * 1024,  # Convert GB to bytes
            "expire": int(expire_date.timestamp()),
            "data_limit_reset_strategy": "no_reset",
            "status": "active"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/user",
            json=user_data,
            headers=self._get_headers()
        ) as response:
            if response.status == 200:
                result = await response.json()
                logging.info(f"User {username} created successfully")
                return result
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create user: {response.status} - {error_text}")
    
    async def get_user(self, username: str) -> Dict:
        """Get user information"""
        async with self.session.get(
            f"{self.base_url}/api/user/{username}",
            headers=self._get_headers()
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get user: {response.status}")
    
    async def get_user_subscription(self, username: str) -> str:
        """Get user subscription URL"""
        # For Marzban, subscription URLs are typically constructed as:
        # https://domain.com/sub/username
        # We don't need to verify the endpoint exists, just construct the URL
        subscription_url = f"{self.base_url}/sub/{username}"
        
        # Optional: Verify the subscription endpoint is accessible
        try:
            async with self.session.get(
                subscription_url,
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return subscription_url
                else:
                    # If endpoint doesn't exist, still return the URL (it might work for clients)
                    logging.warning(f"Subscription endpoint returned {response.status}, but returning URL anyway")
                    return subscription_url
        except Exception as e:
            # If we can't verify, still return the constructed URL
            logging.warning(f"Could not verify subscription endpoint: {e}")
            return subscription_url
    
    async def extend_user(self, username: str, extend_days: int) -> Dict:
        """Extend user subscription"""
        user = await self.get_user(username)
        current_expire = user.get("expire", 0)
        
        if current_expire:
            new_expire = current_expire + (extend_days * 24 * 60 * 60)
        else:
            new_expire = int((datetime.now() + timedelta(days=extend_days)).timestamp())
        
        update_data = {
            "expire": new_expire
        }
        
        async with self.session.put(
            f"{self.base_url}/api/user/{username}",
            json=update_data,
            headers=self._get_headers()
        ) as response:
            if response.status == 200:
                result = await response.json()
                logging.info(f"User {username} extended by {extend_days} days")
                return result
            else:
                raise Exception(f"Failed to extend user: {response.status}")
    
    async def delete_user(self, username: str) -> bool:
        """Delete a user"""
        async with self.session.delete(
            f"{self.base_url}/api/user/{username}",
            headers=self._get_headers()
        ) as response:
            if response.status == 200:
                logging.info(f"User {username} deleted successfully")
                return True
            else:
                raise Exception(f"Failed to delete user: {response.status}")
    
    async def get_system_stats(self) -> Dict:
        """Get system statistics"""
        async with self.session.get(
            f"{self.base_url}/api/system",
            headers=self._get_headers()
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get system stats: {response.status}")
