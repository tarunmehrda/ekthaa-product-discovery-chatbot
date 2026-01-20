# Very simple in-memory context per user_id

USER_CONTEXT = {}

def get_context(user_id: str):
    return USER_CONTEXT.get(user_id, {})

def update_context(user_id: str, data: dict):
    prev = USER_CONTEXT.get(user_id, {})
    prev.update({k:v for k,v in data.items() if v is not None})
    USER_CONTEXT[user_id] = prev
    return prev
