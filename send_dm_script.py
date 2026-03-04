import sys
sys.path.insert(0, '/usr/local/google/home/guyu/Desktop/mymonorepo/projects/g3lobster/g3lobster')
from chat.services import ChatService
from chat.models import Message
from config import config
import asyncio

async def send_dm():
    chat_service = ChatService(config=config)
    message = Message(
        room_id="dm/5Hql04AAAAE",
        user_id="gemini-cli",
        content="reload your skills"
    )
    await chat_service.send_message(message)

if __name__ == "__main__":
    asyncio.run(send_dm())