from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional

from dependencies.auth import verify_user_session
from database import get_db
from schemas.note import NoteCreate, NoteUpdate, NoteOutput

router = APIRouter(prefix="/notes", tags=["notes"])

async def verify_note_ownership(note_id: int, current_user_id: int=Depends(verify_user_session), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    sql = "SELECT id FROM notes WHERE id = %s and user_id = %s"
    val = (note_id, current_user_id)
    cursor.execute(sql, val)
    existing_note = cursor.fetchone()
    if existing_note is None:
        raise HTTPException(status_code=404, detail="筆記不存在或無權限訪問")
    return None


@router.post("", status_code=201)
async def create_note(note: NoteCreate, current_user_id: int=Depends(verify_user_session), db=Depends(get_db)):
    cursor = db.cursor()
    sql = "INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s)"
    val = (current_user_id, note.title, note.content)
    cursor.execute(sql, val)
    db.commit()
    return {"message":"筆記建立成功"}

@router.get("")
async def get_notes(title: Optional[str] = Query(None), current_user_id: int=Depends(verify_user_session), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    if title:
        sql = "SELECT id, title FROM notes WHERE user_id = %s AND title LIKE %s"
        val = (current_user_id, f"%{title}%")
    else:
        sql = "SELECT id, title FROM notes WHERE user_id = %s"
        val = (current_user_id,)
    cursor.execute(sql, val)
    notes = cursor.fetchall()
    return notes

@router.get("/{note_id}")
async def get_note(note_id: int, is_owner: None=Depends(verify_note_ownership), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    sql = "SELECT id, user_id, title, content, created_time, updated_time FROM notes WHERE id = %s"
    val = (note_id,)
    cursor.execute(sql, val)
    note = cursor.fetchone()
    if note is None:
        raise HTTPException(status_code=404, detail="筆記不存在或無權限訪問")
    sql = "SELECT tag_name from tags INNER JOIN note_tag ON tags.id = note_tag.tag_id WHERE note_id = %s"
    val = (note_id,)
    cursor.execute(sql, val)
    tags_result = cursor.fetchall()
    tags = []
    for tag in tags_result:
        tags.append(tag["tag_name"])
    note["tags"] = tags
    return note

@router.post("/{note_id}")
async def update_note(note_id: int, note: NoteUpdate, is_owner: None=Depends(verify_note_ownership), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    # 更新筆記的基本資訊
    sql = "UPDATE notes SET title = %s, content = %s WHERE id = %s"
    val = (note.title, note.content, note_id)
    cursor.execute(sql, val)

    # 取得筆記目前已有的標籤名稱
    sql = "SELECT tag_name FROM note_tag INNER JOIN tags ON note_tag.tag_id = tags.id WHERE note_id = %s"
    val = (note_id,)
    cursor.execute(sql, val)
    note_tags = cursor.fetchall()
    # 將資料庫中的標籤組和要更新的標籤組轉換為集合
    note_tags_set = set()
    for tag in note_tags:
        note_tags_set.add(tag["tag_name"])

    # 將要更新的標籤組轉換為集合
    update_note_tags_set = set(note.tags)

    # 新增標籤
    tags_to_add = update_note_tags_set - note_tags_set 
    for tag_name in tags_to_add:
        # 查詢tags中是否有相同的tag，如果沒有則新增到tags中
        sql = "SELECT id FROM tags WHERE tag_name = %s"
        val = (tag_name,)
        cursor.execute(sql, val)
        tag = cursor.fetchone()
        if tag is None:
            sql = "INSERT INTO tags (tag_name) VALUES (%s)"
            val = (tag_name,)
            cursor.execute(sql, val)
            tag_id = cursor.lastrowid
        else:
            tag_id = tag["id"]
        # 將標籤連結到筆記
        sql = "INSERT INTO note_tag (note_id, tag_id) VALUES (%s, %s)"
        val = (note_id, tag_id)
        cursor.execute(sql, val)
    
    # 刪除標籤
    tags_to_remove = note_tags_set - update_note_tags_set
    for tag_name in tags_to_remove:
        sql = "SELECT id FROM tags WHERE tag_name = %s"
        val = (tag_name,)
        cursor.execute(sql, val)
        tag = cursor.fetchone()
        sql = "DELETE FROM note_tag WHERE note_id = %s AND tag_id = %s"
        val = (note_id, tag["id"])
        cursor.execute(sql, val)

        # 如果其他筆記沒有連結此標籤，則刪除此標籤
        sql = "SELECT COUNT(*) FROM note_tag WHERE tag_id = %s"
        val = (tag["id"],)
        cursor.execute(sql, val)
        count = cursor.fetchone()["COUNT(*)"]
        if count == 0:
            sql = "DELETE FROM tags WHERE id = %s"
            val = (tag["id"],)
            cursor.execute(sql, val)

    db.commit()
    return {"message":"筆記更新成功"}

@router.delete("/{note_id}")
async def delete_note(note_id: int, is_owner: None=Depends(verify_note_ownership), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    # 如果其他筆記沒有連結準備刪除筆記的標籤，則刪除標籤
    sql = "SELECT tag_id FROM note_tag WHERE note_id = %s"
    val = (note_id,)
    cursor.execute(sql, val)
    note_tags = cursor.fetchall()
    for tag in note_tags:
        sql = "SELECT COUNT(*) FROM note_tag WHERE tag_id = %s"
        val = (tag["tag_id"],)
        cursor.execute(sql, val)
        count = cursor.fetchone()["COUNT(*)"]
        if count == 1:
            sql = "DELETE FROM tags WHERE id = %s"
            val = (tag["tag_id"],)
            cursor.execute(sql, val)

    sql = "DELETE FROM notes WHERE id = %s"
    val = (note_id,)
    cursor.execute(sql, val)

    db.commit()
    return {"message":"筆記刪除成功"}