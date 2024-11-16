from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
btn = KeyboardButton(text='Рассчитать')
btn0 = KeyboardButton(text='Информация')
btn3 = KeyboardButton(text='Купить')
kb.row(btn, btn0)
kb.add(btn3)

catalog_kb = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
btns = []
for i in range(1, 5):
    btn_ = InlineKeyboardButton(text=f"Product{i}", callback_data="product_buying")
    btns.append(btn_)
catalog_kb.row(btns[0], btns[1], btns[2], btns[3])

kb1 = InlineKeyboardMarkup(resize_keyboard=True)
btn1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
btn2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb1.row(btn1, btn2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    for i in range(1, 5):
        with open(f"Vit{i}.png", "rb") as img:
            await message.answer_photo(img, f"Название: Product{i} | Описание: описание {i} | Цена: {i * 100}")
    await message.answer('Выберите продукт для покупки:', reply_markup=catalog_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb1)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5")
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(ag=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(gr=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_calories(message, state):
    await state.update_data(wg=message.text)
    data = await state.get_data()
    cal = float(data['wg']) * 10 + float(data['gr']) * 6.25 - float(data['ag']) * 5 + 5
    await message.answer(f'Ваша норма каллорий: {cal}')
    await state.finish()


@dp.message_handler()
async def all_message(message):
    await message.answer("Введите команду /start, чтобы начать")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
