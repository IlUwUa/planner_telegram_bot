import asyncio
import database as db
from datetime import datetime
from aiogram import Bot

async def start_scheduler(bot: Bot):
    while True:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        due_tasks = db.get_due_tasks(now_str)
        
        for task in due_tasks:
            task_id, user_id, text = task
            try:
                await bot.send_message(chat_id=user_id, text=f"НАПОМИНАНИЕ!!!\n\n{text}", parse_mode="Markdown")
                db.delete_task_by_id(task_id)
            except Exception as e:
                print(f"Ошибка отправки {user_id}: {e}!!!")


        await asyncio.sleep(60)