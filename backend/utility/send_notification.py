# Notification service integration
from datetime import datetime

import aiohttp

from backend.utility.logger import logger


async def send_notification(task_data: dict):
    """Send task assignment notification to Node.js service"""
    try:
        async with aiohttp.ClientSession() as session:
            notification_payload = {
                "type": "task_assigned",
                "task": task_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            async with session.post(
                    "http://localhost:3001/notify",
                    json=notification_payload,
                    timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    logger.info(f"Notification sent successfully for task: {task_data['title']}")
                else:
                    logger.error(f"Notification service returned {response.status}")
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")

