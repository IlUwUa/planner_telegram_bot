from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить задачу"), KeyboardButton(text="Список задач")],
            [KeyboardButton(text="Настройки времени")]
        ],
        resize_keyboard=True, 
        persistent=True       
    )
    return kb


def get_geo_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить геопозицию", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_tasks_delete_keyboard(tasks):
    builder = InlineKeyboardBuilder()
    
    for t in tasks:
        short_text = t[1][:15] + "..." if len(t[1]) > 15 else t[1]
        display_time = t[2].split(' ')[1] 
        
        button_text = f"⏰ {display_time} | {short_text} ❌"
        

        builder.button(text=button_text, callback_data=f"del_{t[0]}")
    

    builder.adjust(1)
    return builder.as_markup()