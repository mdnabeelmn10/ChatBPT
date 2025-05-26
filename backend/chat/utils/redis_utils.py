from django.core.cache import cache

def is_allowed(user_id, limit=10, timeout=86400):
    key = f"user:{user_id}:chat_limit"
    current = cache.get(key)

    if current is None:
        cache.set(key, 1, timeout=timeout)  # 1 day TTL
        return True
    elif current < limit:
        cache.incr(key)
        return True
    return False


def get_remaining_chats(user_id, limit=10):
    key = f"user:{user_id}:chat_limit"
    current = cache.get(key)
    if current is None:
        return limit
    return max(0, limit - int(current))
