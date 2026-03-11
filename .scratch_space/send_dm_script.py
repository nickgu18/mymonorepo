import sys
import asyncio
import os

# Ensure the g3lobster package path is set up correctly
sys.path.insert(0, '/usr/local/google/home/guyu/Desktop/mymonorepo/projects/g3lobster')

# Activate the venv for g3lobster
venv_path = '/usr/local/google/home/guyu/Desktop/mymonorepo/projects/g3lobster/.venv/bin/activate_this.py'
if os.path.exists(venv_path):
    with open(venv_path) as f:
        exec(f.read(), {'__file__': venv_path})

from g3lobster.chat.auth import get_authenticated_service

async def send_dm_to_space():
    service = get_authenticated_service()
    
    with open("/usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/payload.txt", "r") as f:
        payload = f.read()

    msg = await asyncio.to_thread(
        service.spaces().messages().create(
            parent="spaces/AAQA9iI2rjA",
            body={"text": payload}
        ).execute
    )
    print("Sent message to spaces/AAQA9iI2rjA")

if __name__ == "__main__":
    asyncio.run(send_dm_to_space())
