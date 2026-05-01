from config import ALLOWED_USER_IDS

def is_allowed(user_id):
    return user_id in ALLOWED_USER_IDS