from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from datetime import datetime, timedelta
import pytz
from timezonefinder import TimezoneFinder

import database as db
import keyboards as kb  

router = Router()
tf = TimezoneFinder()


class TaskStates(StatesGroup):
    waiting_for_task_input = State() 


def parse_task_input(text):
    parts = text.rsplit(' ', 1)
    if len(parts) != 2:
        return None
    
    task_text, time_str = parts
    try:

        datetime.strptime(time_str, "%H:%M")
        return task_text, time_str
    except ValueError:
        return None


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    tz = db.get_user_timezone(message.chat.id)
    text = "Привет! Я бот-планировщик.\nИспользуйте меню ниже"
    
    if tz == 'UTC':
        text += "\n\n**Важно:** Настройте часовой пояс, нажав кнопку \"Настройки времени\"."
        
    await message.answer(text, reply_markup=kb.get_main_menu())


@router.message(F.text == "⚙️ Настройки времени")
async def btn_timezone(message: types.Message):
    await message.answer(
        "Нажмите кнопку ниже, чтобы отправить геопозицию и настроить время.", 
        reply_markup=kb.get_geo_kb()
    )


@router.message(F.location)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    timezone_name = tf.timezone_at(lng=lon, lat=lat)
    
    if timezone_name:
        db.set_user_timezone(message.chat.id, timezone_name)
        await message.answer(
            f"Часовой пояс {timezone_name} установлен!",
            reply_markup=kb.get_main_menu()
        )
    else:
        await message.answer("Не удалось определить зону.", reply_markup=kb.get_main_menu())


@router.message(F.text == "Добавить задачу")
async def btn_add_task(message: types.Message, state: FSMContext):
    if db.get_user_timezone(message.chat.id) == 'UTC':
        await message.answer("Сначала настрой время через Настройки!")
        return

    await message.answer(
        "Напишите задачу и время через пробел.\n"
        "Пример: Купить молоко 18:30",
        parse_mode="Markdown"
    )
    await state.set_state(TaskStates.waiting_for_task_input)


@router.message(TaskStates.waiting_for_task_input)
async def process_task_input(message: types.Message, state: FSMContext):
    parsed = parse_task_input(message.text)
    
    if not parsed:
        await message.answer("Ошибка формата. Формат: \"Текст задачи ЧЧ:ММ\"\nПопробуй еще раз.", parse_mode="Markdown")
        return

    task_text, time_input = parsed
    
    try:
        tz_name = db.get_user_timezone(message.chat.id)
        user_tz = pytz.timezone(tz_name)
        
        dt_naive = datetime.strptime(time_input, "%H:%M")
        now_user = datetime.now(user_tz)
        
        user_dt = user_tz.localize(datetime(
            year=now_user.year, month=now_user.month, day=now_user.day, 
            hour=dt_naive.hour, minute=dt_naive.minute
        ))
        

        if user_dt < now_user:
             user_dt += timedelta(days=1)
             warning_tomorrow = " (на завтра)"
        else:
             warning_tomorrow = ""


        server_dt = user_dt.astimezone(datetime.now().astimezone().tzinfo)
        full_date_str = server_dt.strftime('%Y-%m-%d %H:%M')
        

        db.add_task(message.chat.id, task_text, full_date_str)
        
        await message.answer(
            f"Задача {task_text} добавлена на {time_input} {warning_tomorrow}!",
            parse_mode="Markdown",
            reply_markup=kb.get_main_menu()
        )
        await state.clear()
        
    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при обработке времени.")


@router.message(F.text == "Список задач")
async def btn_list_tasks(message: types.Message):
    tasks = db.get_tasks(message.chat.id)
    if not tasks:
        await message.answer("Список задач пуст.")
        return


    delete_keyboard = kb.get_tasks_delete_keyboard(tasks)
    
    await message.answer(
        "  Ваши задачи:  \n\n"
        "Нажми на задачу, чтобы удалить её",
        reply_markup=delete_keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("del_"))
async def callback_delete_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    
    if db.delete_task(task_id, callback.message.chat.id):
        await callback.answer("Задача удалена") 
        

        tasks = db.get_tasks(callback.message.chat.id)
        if not tasks:
            await callback.message.edit_text("Список задач пуст.")
        else:
            new_kb = kb.get_tasks_delete_keyboard(tasks)
            await callback.message.edit_reply_markup(reply_markup=new_kb)
    else:
        await callback.answer("Задача уже удалена", show_alert=True)