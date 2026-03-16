from database.db import get_user_profile, get_top_users

async def get_user_profile_service(user_id):
    profile = await get_user_profile(user_id)
    return profile

async def get_top_users_service(limit=10):
    top_users = await get_top_users(limit)
    return top_users