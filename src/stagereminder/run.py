import asyncio
from dotenv import load_dotenv
from stagereminder.main.update_stage import update_stages
from stagereminder.main.notify_stage import notify_stage


load_dotenv()

def run():
    asyncio.run(update_stages())
    notify_stage()

if __name__ == "__main__":
    run()