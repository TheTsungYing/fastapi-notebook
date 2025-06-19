from fastapi import APIRouter, HTTPException, Depends, Request, Response

from passlib.context import CryptContext

from schemas.user import UserCreate, User, Login
from database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

# 密碼雜湊工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 驗證使用者
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 取得密碼雜湊
def get_password_hash(password):
    return pwd_context.hash(password)

# API
@router.post("/register", response_model=User, status_code=201)
async def register_user(user: UserCreate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="使用者名稱已存在")

    hashed_password = get_password_hash(user.password)
    sql = "INSERT INTO users (username, password, email, full_name) VALUES (%s, %s, %s, %s)"
    val = (user.username, hashed_password, user.email, user.full_name)
    cursor.execute(sql, val)
    db.commit()
    user_id = cursor.lastrowid
    dict_cursor = db.cursor(dictionary=True)
    dict_cursor.execute("SELECT id, username, email, full_name FROM users WHERE id = %s", (user_id,))
    new_user = dict_cursor.fetchone()
    return new_user

@router.post("/login")
async def login(login_data: Login, request: Request, response: Response, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (login_data.username,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="使用者名稱或密碼錯誤")
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="使用者名稱或密碼錯誤")

    # 將使用者 ID 儲存到 Session
    request.session["user_id"] = user["id"]
    return {"success": True ,"message": "登入成功"}

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "登出成功"}