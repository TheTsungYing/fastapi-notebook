from fastapi import Request, HTTPException

# 從 Session 中取得目前使用者id
async def verify_user_session(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="未經授權")
    return user_id