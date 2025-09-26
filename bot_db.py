# bot_db.py

users = {}
pending_games = {}  # ставка -> [user1_id, user2_id, chat_id]

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {"balance": 0, "payments": {}}
    return users[user_id]

def add_balance(user_id, amount):
    user = get_user(user_id)
    user["balance"] += amount

def remove_balance(user_id, amount):
    user = get_user(user_id)
    if user["balance"] >= amount:
        user["balance"] -= amount
        return True
    return False

def save_payment(user_id, bill_id, amount_usd, expected_amount):
    user = get_user(user_id)
    user["payments"][bill_id] = {"amount_usd": amount_usd, "expected_amount": expected_amount, "paid": False}

def update_payment_status(user_id, bill_id, paid):
    user = get_user(user_id)
    if bill_id in user["payments"]:
        user["payments"][bill_id]["paid"] = paid
        return True
    return False

def get_payment_status(user_id, bill_id):
    user = get_user(user_id)
    return user["payments"].get(bill_id, {}).get("paid", False)

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