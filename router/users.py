from fastapi import APIRouter, HTTPException, Depends, Request

from schemas.user import User
from database import get_db
from dependencies.auth import verify_user_session

router = APIRouter(prefix="/users", tags=["users"])

# API
@router.get("/me", response_model=User)
async def get_user_data(request: Request, current_user_id: int=Depends(verify_user_session), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, full_name FROM users WHERE id = %s", (current_user_id,))
    user_info = cursor.fetchone()
    # 防止意外，資料庫連接問題或Session資料不一致
    if user_info is None:
        request.session.pop("user_id", None)  # 使用者不存在，清除 Session
        raise HTTPException(status_code=401, detail="未經授權")
    return user_info