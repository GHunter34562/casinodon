import random
from database import remove_user_balance, add_user_balance

pending_games = {}  # ставка -> [user1_id, chat_id]

def create_game(stake, user1_id, chat_id):
    pending_games[stake] = {"user1_id": user1_id, "chat_id": chat_id}

def find_opponent(stake, user2_id, chat_id):
    if stake in pending_games:
        game = pending_games[stake]
        if game["chat_id"] == chat_id and game["user1_id"] != user2_id:
            opponent = game["user1_id"]
            del pending_games[stake]
            return opponent
    return None

# ——————————————————————————————————————————————————————————————————————————————————————————————————————

async def start_dice_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает кубик...")
    dice1 = await bot.send_dice(chat_id)
    d1 = dice1.dice.value

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает кубик...")
    dice2 = await bot.send_dice(chat_id)
    d2 = dice2.dice.value

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if d1 > d2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎉 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif d2 > d1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎉 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, "🤝 Ничья! Ставки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_dart_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎯 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает дротик...")
    dart1 = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d1 = dart1.dice.value

    await bot.send_message(chat_id, f"🎯 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает дротик...")
    dart2 = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d2 = dart2.dice.value

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if d1 > d2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎯 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif d2 > d1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎯 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, "🤝 Ничья! Ставки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_basketball_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🏀 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает мяч...")
    basket1 = await bot.send_dice(emoji="🏀", chat_id=chat_id)
    d1 = basket1.dice.value

    await bot.send_message(chat_id, f"🏀 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает мяч...")
    basket2 = await bot.send_dice(emoji="🏀", chat_id=chat_id)
    d2 = basket2.dice.value

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if d1 > d2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🏀 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif d2 > d1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🏀 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, "🤝 Ничья! Ставки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_bowling_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎳 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает шар...")
    bowl1 = await bot.send_dice(emoji="🎳", chat_id=chat_id)
    d1 = bowl1.dice.value

    await bot.send_message(chat_id, f"🎳 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает шар...")
    bowl2 = await bot.send_dice(emoji="🎳", chat_id=chat_id)
    d2 = bowl2.dice.value

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if d1 > d2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎳 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif d2 > d1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎳 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, "🤝 Ничья! Ставки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_slot_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎰 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} крутит слоты...")
    slot1 = await bot.send_dice(emoji="🎰", chat_id=chat_id)
    d1 = slot1.dice.value

    await bot.send_message(chat_id, f"🎰 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} крутит слоты...")
    slot2 = await bot.send_dice(emoji="🎰", chat_id=chat_id)
    d2 = slot2.dice.value

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if d1 > d2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎰 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif d2 > d1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎰 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, "🤝 Ничья! Ставки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_cubix_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает 3 куба...")
    dice1 = await bot.send_dice(chat_id=chat_id)
    d1 = dice1.dice.value

    dice2 = await bot.send_dice(chat_id=chat_id)
    d2 = dice2.dice.value

    dice3 = await bot.send_dice(chat_id=chat_id)
    d3 = dice3.dice.value

    score1 = (d1 + d2) * d3

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает 3 куба...")
    dice4 = await bot.send_dice(chat_id=chat_id)
    d4 = dice4.dice.value

    dice5 = await bot.send_dice(chat_id=chat_id)
    d5 = dice5.dice.value

    dice6 = await bot.send_dice(chat_id=chat_id)
    d6 = dice6.dice.value

    score2 = (d4 + d5) * d6

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if score1 > score2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎲 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nРезультат: {score1} > {score2}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif score2 > score1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎲 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nРезультат: {score2} > {score1}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, f"🤝 Ничья! Результаты: {score1} = {score2}\nСтавки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

# ——————————————————————————————————————————————————————————————————————————————————————————————————————

async def start_dice2_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает 2 куба...")
    dice1a = await bot.send_dice(chat_id=chat_id)
    d1a = dice1a.dice.value
    dice1b = await bot.send_dice(chat_id=chat_id)
    d1b = dice1b.dice.value
    score1 = d1a + d1b

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает 2 куба...")
    dice2a = await bot.send_dice(chat_id=chat_id)
    d2a = dice2a.dice.value
    dice2b = await bot.send_dice(chat_id=chat_id)
    d2b = dice2b.dice.value
    score2 = d2a + d2b

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if score1 > score2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎲 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nРезультат: {score1} > {score2}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif score2 > score1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎲 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nРезультат: {score2} > {score1}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, f"🤝 Ничья! Результаты: {score1} = {score2}\nСтавки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_dart2_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎯 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает 2 дротика...")
    dart1a = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d1a = dart1a.dice.value
    dart1b = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d1b = dart1b.dice.value
    score1 = d1a + d1b

    await bot.send_message(chat_id, f"🎯 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает 2 дротика...")
    dart2a = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d2a = dart2a.dice.value
    dart2b = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d2b = dart2b.dice.value
    score2 = d2a + d2b

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if score1 > score2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎯 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nРезультат: {score1} > {score2}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif score2 > score1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎯 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nРезультат: {score2} > {score1}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, f"🤝 Ничья! Результаты: {score1} = {score2}\nСтавки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_bowling2_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎳 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает 2 шара...")
    bowl1a = await bot.send_dice(emoji="🎳", chat_id=chat_id)
    d1a = bowl1a.dice.value
    bowl1b = await bot.send_dice(emoji="🎳", chat_id=chat_id)
    d1b = bowl1b.dice.value
    score1 = d1a + d1b

    await bot.send_message(chat_id, f"🎳 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает 2 шара...")
    bowl2a = await bot.send_dice(emoji=" bowling", chat_id=chat_id)
    d2a = bowl2a.dice.value
    bowl2b = await bot.send_dice(emoji=" bowling", chat_id=chat_id)
    d2b = bowl2b.dice.value
    score2 = d2a + d2b

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if score1 > score2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎳 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nРезультат: {score1} > {score2}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif score2 > score1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎳 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nРезультат: {score2} > {score1}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, f"🤝 Ничья! Результаты: {score1} = {score2}\nСтавки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

# ——————————————————————————————————————————————————————————————————————————————————————————————————————

async def start_dice3_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает 3 куба...")
    dice1a = await bot.send_dice(chat_id=chat_id)
    d1a = dice1a.dice.value
    dice1b = await bot.send_dice(chat_id=chat_id)
    d1b = dice1b.dice.value
    dice1c = await bot.send_dice(chat_id=chat_id)
    d1c = dice1c.dice.value
    score1 = d1a + d1b + d1c

    await bot.send_message(chat_id, f"🎲 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает 3 куба...")
    dice2a = await bot.send_dice(chat_id=chat_id)
    d2a = dice2a.dice.value
    dice2b = await bot.send_dice(chat_id=chat_id)
    d2b = dice2b.dice.value
    dice2c = await bot.send_dice(chat_id=chat_id)
    d2c = dice2c.dice.value
    score2 = d2a + d2b + d2c

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if score1 > score2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎲 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nРезультат: {score1} > {score2}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif score2 > score1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎲 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nРезультат: {score2} > {score1}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, f"🤝 Ничья! Результаты: {score1} = {score2}\nСтавки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_dart3_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎯 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает 3 дротика...")
    dart1a = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d1a = dart1a.dice.value
    dart1b = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d1b = dart1b.dice.value
    dart1c = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d1c = dart1c.dice.value
    score1 = d1a + d1b + d1c

    await bot.send_message(chat_id, f"🎯 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает 3 дротика...")
    dart2a = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d2a = dart2a.dice.value
    dart2b = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d2b = dart2b.dice.value
    dart2c = await bot.send_dice(emoji="🎯", chat_id=chat_id)
    d2c = dart2c.dice.value
    score2 = d2a + d2b + d2c

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if score1 > score2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎯 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nРезультат: {score1} > {score2}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif score2 > score1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎯 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nРезультат: {score2} > {score1}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, f"🤝 Ничья! Результаты: {score1} = {score2}\nСтавки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)

async def start_bowling3_game(bot, user1_id, user2_id, stake, chat_id):
    if not remove_user_balance(user1_id, stake) or not remove_user_balance(user2_id, stake):
        await bot.send_message(chat_id, "❌ Один из участников не имеет достаточного баланса.")
        return

    await bot.send_message(chat_id, f"🎳 @{(await bot.get_chat_member(chat_id, user1_id)).user.username} бросает 3 шара...")
    bowl1a = await bot.send_dice(emoji="🎳", chat_id=chat_id)
    d1a = bowl1a.dice.value
    bowl1b = await bot.send_dice(emoji=" bowling", chat_id=chat_id)
    d1b = bowl1b.dice.value
    bowl1c = await bot.send_dice(emoji=" bowling", chat_id=chat_id)
    d1c = bowl1c.dice.value
    score1 = d1a + d1b + d1c

    await bot.send_message(chat_id, f"🎳 @{(await bot.get_chat_member(chat_id, user2_id)).user.username} бросает 3 шара...")
    bowl2a = await bot.send_dice(emoji=" bowling", chat_id=chat_id)
    d2a = bowl2a.dice.value
    bowl2b = await bot.send_dice(emoji=" bowling", chat_id=chat_id)
    d2b = bowl2b.dice.value
    bowl2c = await bot.send_dice(emoji=" bowling", chat_id=chat_id)
    d2c = bowl2c.dice.value
    score2 = d2a + d2b + d2c

    total = stake * 2
    commission = total * 0.05
    prize = total - commission

    if score1 > score2:
        winner_id = user1_id
        await bot.send_message(chat_id, f"🎳 Победитель: @{(await bot.get_chat_member(chat_id, user1_id)).user.username}!\nРезультат: {score1} > {score2}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    elif score2 > score1:
        winner_id = user2_id
        await bot.send_message(chat_id, f"🎳 Победитель: @{(await bot.get_chat_member(chat_id, user2_id)).user.username}!\nРезультат: {score2} > {score1}\nВыигрыш: {prize:.2f} $.")
        add_user_balance(winner_id, prize)
    else:
        await bot.send_message(chat_id, f"🤝 Ничья! Результаты: {score1} = {score2}\nСтавки возвращены.")
        add_user_balance(user1_id, stake)
        add_user_balance(user2_id, stake)