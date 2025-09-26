from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import threading
import logging
import config
from database import init_db, get_user_balance, add_user_balance, set_user_balance, save_payment, update_payment_status, get_payment_status, create_active_game, get_active_game_by_stake_and_msg, delete_active_game_by_message_id, get_game_creator_by_message_id, get_active_game_by_stake, ensure_user_exists, get_all_users, get_users_count, remove_user_balance
from crypto_api import CryptoBotAPI
from game_logic import start_dice_game, start_dart_game, start_basketball_game, start_bowling_game, start_slot_game, start_cubix_game, start_dice2_game, start_dart2_game, start_bowling2_game, start_dice3_game, start_dart3_game, start_bowling3_game

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
crypto_api = CryptoBotAPI(config.CRYPTO_BOT_TOKEN)

# ——— FSM ———
class DepositState(StatesGroup):
    waiting_for_amount = State()

class WithdrawState(StatesGroup):
    waiting_for_amount = State()

def check_payment_timeout(chat_id, bill_id, expected_amount, bot_instance):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        _check_payment_with_timeout(chat_id, bill_id, expected_amount, bot_instance)
    )

async def _check_payment_with_timeout(chat_id, bill_id, expected_amount, bot_instance):
    for i in range(30):  # 60 секунд / 2 = 30 итераций
        await asyncio.sleep(2)
        invoice_info = crypto_api.get_invoice(bill_id)
        if invoice_info:
            invoice = invoice_info["result"]
            status = invoice.get("status")
            logging.info(f"Проверка счета {bill_id}: статус = {status}")
            if status == "paid":
                logging.info(f"Счет {bill_id} оплачен! Начисляем баланс.")
                update_payment_status(bill_id, True)
                currency_amount = expected_amount  # 1 USD = 1 валюта бота
                add_user_balance(chat_id, currency_amount)
                balance = get_user_balance(chat_id)
                try:
                    await bot_instance.send_message(chat_id, f"✅ Счет пополнен на {currency_amount:.2f} $. Текущий баланс: {balance:.2f}.")
                except Exception:
                    pass  # Пользователь не писал боту
                return
        else:
            logging.warning(f"Не удалось получить информацию о счете {bill_id}")
    # Если время вышло
    logging.info(f"Время истекло для счета {bill_id}")
    try:
        await bot_instance.send_message(chat_id, "⏰ Время для оплаты вышло.")
    except Exception:
        pass

def main_menu_markup():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="💳 Пополнить", callback_data="deposit")],
        [InlineKeyboardButton(text="📤 Вывести", callback_data="withdraw")],
        [InlineKeyboardButton(text="🎮 Игры", callback_data="games")],
        [InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/don_kazik")],
        [InlineKeyboardButton(text="👥 Наша группа", url="https://t.me/+7YO0xmsgeeJkMzg1")]
    ])
    return markup

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    ensure_user_exists(message.from_user.id)
    if message.chat.type != "private":
        return
    text = (
        "🎰Добро пожаловать в казино Дона.🎰\nТут царит неповторимая атмосфера азарта и безупречного сервиса.\nДля нас каждый гость – это почетный посетитель, чье время и комфорт превыше всего. Мы создали это место, чтобы вы могли не просто играть, а наслаждаться каждым моментом, погрузившись в мир высоких ставок\n\n"
        "📢 Наш канал: <a href='https://t.me/don_kazik'>Подписаться</a>\n"
        "👥 Наша группа: <a href='https://t.me/+7YO0xmsgeeJkMzg1'>Присоединиться</a>\n"
        "Разраб величайший @padadede"
    )
    await message.answer(text, reply_markup=main_menu_markup(), parse_mode="HTML")

# ... (остальные обработчики как есть) ...
@dp.callback_query(lambda call: call.data in ["balance", "deposit", "withdraw", "games"])
async def handle_callback(call: types.CallbackQuery, state: FSMContext):
    ensure_user_exists(call.from_user.id)
    user_id = call.from_user.id
    if call.data == "balance":
        balance = get_user_balance(user_id)
        await call.answer("Ваш баланс загружается...", show_alert=False)
        await call.message.answer(f"Ваш баланс: {balance} $.")
    elif call.data == "deposit":
        await call.answer("Введите сумму для пополнения (в USD):", show_alert=False)
        await call.message.answer("Введите сумму для пополнения (в USD):")
        await state.set_state(DepositState.waiting_for_amount)
    elif call.data == "withdraw":
        await call.answer("Введите сумму для вывода $:", show_alert=False)
        await call.message.answer("Введите сумму для вывода в $:")
        await state.set_state(WithdrawState.waiting_for_amount)
    elif call.data == "games":
        await call.answer("Команды игр:", show_alert=False)
        await call.message.answer(
            "/cub <ставка> — игра в кубики (Dice)\n"
            "/dart <ставка> — дартс\n"
            "/bask <ставка> — баскетбол\n"
            "/boul <ставка> — боулинг\n"
            "/slot <ставка> — слоты\n"
            "/cubix <ставка> — кастомная игра с 3 кубами\n"
            "/cub2, /dart2 — 2 броска\n"
            "/cub3, /dart3 — 3 броска"
        )

@dp.message(DepositState.waiting_for_amount)
async def process_deposit_amount(message: types.Message, state: FSMContext):
    ensure_user_exists(message.from_user.id)
    if message.chat.type != "private":
        return
    try:
        amount = float(message.text)  # Убедимся, что принимаем дробные числа
    except ValueError:
        await message.answer("Неверная сумма.")
        await state.clear()
        return

    invoice = crypto_api.create_invoice(amount, description=f"Пополнение {amount} USD = {amount} $")
    if invoice:
        bill_info = invoice["result"]
        bill_id = bill_info["invoice_id"]
        amount = float(bill_info["amount"])

        save_payment(bill_id, message.from_user.id, amount, amount)

        await message.answer(f"Создан счёт на {amount}$:\n"
                             f"Ссылка: {bill_info['bot_invoice_url']}\n\n"
                             f"Оплата должна быть произведена в течение 1 минуты.")

        # Запускаем проверку в отдельном потоке
        thread = threading.Thread(
            target=check_payment_timeout,
            args=(message.from_user.id, bill_id, amount, bot)
        )
        thread.start()
    else:
        await message.answer("Ошибка при создании счёта.")
    await state.clear()

@dp.message(WithdrawState.waiting_for_amount)
async def process_withdraw_amount(message: types.Message, state: FSMContext):
    try:
        amount_bot_currency = float(message.text)  # Принимаем дробные числа
    except ValueError:
        await message.answer("Неверная сумма.")
        await state.clear()
        return

    if amount_bot_currency <= 0:
        await message.answer("Сумма должна быть больше 0.")
        await state.clear()
        return

    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    if balance < amount_bot_currency:
        await message.answer("❌ Недостаточно средств для вывода.")
        await state.clear()
        return

    # Теперь 1 валюта = 1 USD
    amount_usd = amount_bot_currency  # Раньше: amount_bot_currency / 100

    if amount_usd < 0.01:  # Минимальная сумма для чека
        await message.answer("❌ Минимальная сумма вывода: 0.01 USD.")
        await state.clear()
        return

    # Создаем чек
    check = crypto_api.create_check("USDT", amount_usd, description=f"Вывод {amount_bot_currency} $")
    if check:
        check_info = check["result"]
        check_id = check_info["check_id"]
        amount = float(check_info["amount"])

        # Отправляем чек пользователю
        await message.answer(f"Создан чек на {amount}$:\n"
                             f"Ссылка: {check_info['bot_check_url']}")

        # Снимаем средства с баланса
        remove_user_balance(user_id, amount_bot_currency)

    else:
        await message.answer("❌ Ошибка при создании чека.")

    await state.clear()

async def handle_game_command(message: types.Message, game_type: str):
    if message.chat.type == "private":
        await message.answer("Игра доступна только в группах!")
        return

    try:
        stake = float(message.text.split()[1])  # Теперь принимаем дробные ставки
    except (IndexError, ValueError):
        await message.answer(f"Используйте: /{game_type} <ставка>")
        return

    if stake < 0.1:  # Минимальная ставка
        await message.answer("❌ Минимальная ставка: 0.1 $.")
        return

    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    if balance < stake:
        await message.answer("❌ Недостаточно средств для ставки.")
        return

    opponent = get_active_game_by_stake(stake, message.chat.id, user_id)
    if opponent:
        if game_type == "cub":
            await start_dice_game(bot, opponent, user_id, stake, message.chat.id)
        elif game_type == "dart":
            await start_dart_game(bot, opponent, user_id, stake, message.chat.id)
        # ... и так далее
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять игру", callback_data=f"accept_game:{stake}:{game_type}")]
        ])
        sent_msg = await message.answer(f" Игра {game_type} на ставку {stake} создана! Ожидаем соперника...", reply_markup=markup)
        create_active_game(user_id, stake, message.chat.id, sent_msg.message_id)

@dp.message(Command("balbot"))
async def cmd_balbot(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return

    balance_data = crypto_api.get_balance()
    if balance_data:
        text = "💰 Баланс приложения CryptoBot:\n\n"
        for item in balance_data["result"]:
            currency = item["currency_code"]
            available = item["available"]
            onhold = item["onhold"]
            text += f"{currency}: доступно {available}, на удержании {onhold}\n"
        await message.answer(text)
    else:
        await message.answer("❌ Не удалось получить баланс.")

@dp.message(Command("cub"))
async def cmd_cub(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "cub")

@dp.message(Command("dart"))
async def cmd_dart(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "dart")

@dp.message(Command("bask"))
async def cmd_bask(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "bask")

@dp.message(Command("boul"))
async def cmd_boul(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "boul")

@dp.message(Command("slot"))
async def cmd_slot(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "slot")

@dp.message(Command("cubix"))
async def cmd_cubix(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "cubix")

@dp.message(Command("cub2"))
async def cmd_cub2(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "cub2")

@dp.message(Command("dart2"))
async def cmd_dart2(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "dart2")

@dp.message(Command("boul2"))
async def cmd_boul2(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "boul2")

@dp.message(Command("cub3"))
async def cmd_cub3(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "cub3")

@dp.message(Command("dart3"))
async def cmd_dart3(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "dart3")

@dp.message(Command("boul3"))
async def cmd_boul3(message: types.Message):
    ensure_user_exists(message.from_user.id)
    await handle_game_command(message, "boul3")

@dp.message(Command("can"))
async def cmd_cancel_game(message: types.Message):
    if message.chat.type == "private":
        await message.answer("❌ Команда работает только в группах.")
        return

    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение с игрой, чтобы отменить её.")
        return

    replied_msg = message.reply_to_message
    game_creator_id = get_game_creator_by_message_id(replied_msg.message_id, replied_msg.chat.id)

    if game_creator_id is None:
        await message.answer("❌ Это сообщение не связано с активной игрой.")
        return

    if game_creator_id != message.from_user.id:
        await message.answer("❌ Только создатель игры может отменить её.")
        return

    try:
        await bot.delete_message(replied_msg.chat.id, replied_msg.message_id)
        delete_active_game_by_message_id(replied_msg.message_id, replied_msg.chat.id)
        await message.answer("✅ Игра отменена.")
    except Exception:
        await message.answer("❌ Не удалось удалить сообщение.")

@dp.message(Command("bal"))
async def cmd_balance(message: types.Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    await message.answer(f"Ваш баланс: {balance:.2f} $.")

@dp.callback_query(lambda call: call.data.startswith("accept_game:"))
async def accept_game(call: types.CallbackQuery):
    ensure_user_exists(call.from_user.id)
    data = call.data.split(":")
    stake = float(data[1])  # Было: int(data[1])
    game_type = data[2]
    user2_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    logging.info(f"Accept game called: stake={stake}, game_type={game_type}, user2_id={user2_id}, chat_id={chat_id}, msg_id={msg_id}")

    balance = get_user_balance(user2_id)
    if balance < stake:
        await call.answer("❌ Недостаточно средств для ставки.", show_alert=True)
        return

    opponent = get_active_game_by_stake_and_msg(stake, chat_id, user2_id, msg_id)
    logging.info(f"Opponent found: {opponent}")
    if opponent:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            logging.warning(f"Failed to delete message: {e}")

        if game_type == "cub":
            await start_dice_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "dart":
            await start_dart_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "bask":
            await start_basketball_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "boul":
            await start_bowling_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "slot":
            await start_slot_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "cubix":
            await start_cubix_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "cub2":
            await start_dice2_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "dart2":
            await start_dart2_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "boul2":
            await start_bowling2_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "cub3":
            await start_dice3_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "dart3":
            await start_dart3_game(bot, opponent, user2_id, stake, chat_id)
        elif game_type == "boul3":
            await start_bowling3_game(bot, opponent, user2_id, stake, chat_id)
    else:
        await call.answer("❌ Игра уже завершена или не найдена.", show_alert=True)

# ——— АДМИНСКИЕ КОМАНДЫ ———

def is_admin(user_id):
    return user_id in config.ADMINS

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    else:
        return f"ID {user.id}"

@dp.message(Command("pay"))
async def cmd_pay(message: types.Message):
    ensure_user_exists(message.from_user.id)
    if message.chat.type != "private":
        return
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return

    try:
        args = message.text.split()
        target = args[1]
        amount = int(args[2])
    except (IndexError, ValueError):
        await message.answer("❌ Используйте: /pay <username или ID> <сумма>")
        return

    user = None
    user_id = None

    # Проверяем, является ли target числом (ID)
    if target.isdigit():
        user_id = int(target)
    else:
        # Проверяем, начинается ли target с @ (username)
        if target.startswith("@"):
            target = target[1:]
        # Попробуем получить информацию о пользователе по username
        try:
            chat = await bot.get_chat(target)
            user_id = chat.id
        except Exception:
            await message.answer("❌ Пользователь не найден.")
            return

    if user_id:
        try:
            user = await bot.get_chat(user_id)
        except Exception:
            # Если не удалось получить информацию — используем ID
            user = types.User(id=user_id, is_bot=False, first_name="")

        add_user_balance(user_id, amount)
        display_name = get_user_display_name(user)
        await message.answer(f"✅ Пользователю {display_name} начислено {amount} $.")

        # Отправляем уведомление пользователю
        try:
            balance = get_user_balance(user_id)
            await bot.send_message(user_id, f"✅ Администратор начислил вам {amount} $. Текущий баланс: {balance}.")
        except Exception:
            pass  # Пользователь не писал боту
    else:
        await message.answer("❌ Пользователь не найден.")

@dp.message(Command("null"))
async def cmd_null(message: types.Message):
    ensure_user_exists(message.from_user.id)
    if message.chat.type != "private":
        return
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return

    try:
        target = message.text.split()[1]
    except (IndexError, ValueError):
        await message.answer("❌ Используйте: /null <username или ID>")
        return

    user_id = None

    # Проверяем, является ли target числом (ID)
    if target.isdigit():
        user_id = int(target)
    else:
        # Проверяем, начинается ли target с @ (username)
        if target.startswith("@"):
            target = target[1:]
        # Попробуем получить информацию о пользователе по username
        try:
            chat = await bot.get_chat(target)
            user_id = chat.id
        except Exception:
            await message.answer("❌ Пользователь не найден.")
            return

    if user_id:
        try:
            user = await bot.get_chat(user_id)
        except Exception:
            # Если не удалось получить информацию — используем ID
            user = types.User(id=user_id, is_bot=False, first_name="")

        set_user_balance(user_id, 0)
        display_name = get_user_display_name(user)
        await message.answer(f"✅ Баланс пользователя {display_name} обнулён.")
    else:
        await message.answer("❌ Пользователь не найден.")

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    ensure_user_exists(message.from_user.id)
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("✅ Вы являетесь администратором.")
    else:
        await message.answer("❌ Вы не являетесь администратором.")

# ————————————————————————————————————————————————————————————————————————

def get_list_markup(current_page, total_pages):
    markup = InlineKeyboardMarkup(inline_keyboard=[])
    row = []
    if current_page > 1:
        row.append(InlineKeyboardButton(text="⬅️", callback_data=f"list_page:{current_page - 1}"))
    if current_page < total_pages:
        row.append(InlineKeyboardButton(text="➡️", callback_data=f"list_page:{current_page + 1}"))
    if row:
        markup.inline_keyboard.append(row)
    return markup

@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    ensure_user_exists(message.from_user.id)
    if message.chat.type != "private":
        return
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return

    page = 1
    limit = 10
    offset = (page - 1) * limit
    users = get_all_users(limit, offset)
    total = get_users_count()
    total_pages = (total + limit - 1) // limit

    if not users:
        await message.answer("❌ Нет пользователей в базе.")
        return

    text = f"👥 Список пользователей (страница {page}/{total_pages}):\n\n"
    for user_id, balance in users:
        try:
            user = await bot.get_chat(user_id)
            display_name = get_user_display_name(user)
        except Exception:
            display_name = f"ID {user_id}"
        text += f"{display_name}: {balance} $\n"

    markup = get_list_markup(page, total_pages)
    await message.answer(text, reply_markup=markup)

@dp.callback_query(lambda call: call.data.startswith("list_page:"))
async def handle_list_pagination(call: types.CallbackQuery):
    ensure_user_exists(call.from_user.id)
    if not is_admin(call.from_user.id):
        await call.answer("❌ У вас нет прав.", show_alert=True)
        return

    page = int(call.data.split(":")[1])
    limit = 10
    offset = (page - 1) * limit
    users = get_all_users(limit, offset)
    total = get_users_count()
    total_pages = (total + limit - 1) // limit

    if not users:
        await call.answer("❌ Нет пользователей на этой странице.", show_alert=True)
        return

    text = f"👥 Список пользователей (страница {page}/{total_pages}):\n\n"
    for user_id, balance in users:
        try:
            user = await bot.get_chat(user_id)
            display_name = get_user_display_name(user)
        except Exception:
            display_name = f"ID {user_id}"
        text += f"{display_name}: {balance} $\n"

    markup = get_list_markup(page, total_pages)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()

# ————————————————————————————————————————————————————————————————————————

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())