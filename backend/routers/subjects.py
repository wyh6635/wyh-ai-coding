from fastapi import APIRouter
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, field_validator
from database import query_one, query_list, execute
from utils.response import make_response

router = APIRouter(prefix='/api/subjects', tags=['科目管理'])


class SubjectCreate(BaseModel):
    subject_code: str
    subject_name: str
    category: Optional[str] = None
    credit: float = 0.0
    total_hours: int = 0
    description: Optional[str] = None
    status: int = 1

    @field_validator('subject_code', 'subject_name')
    @classmethod
    def validate_required(cls, v, info):
        if not v or not str(v).strip():
            raise ValueError(f'{info.field_name}不能为空')
        return str(v).strip()


class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    category: Optional[str] = None
    credit: Optional[float] = None
    total_hours: Optional[int] = None
    description: Optional[str] = None
    status: Optional[int] = None

    @field_validator('subject_name')
    @classmethod
    def validate_subject_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('科目名称不能为空')
        return v


@router.get('')
def list_subjects(
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[int] = None
):
    conditions = ['1=1']
    params = []

    if keyword:
        conditions.append('(subject_code LIKE %s OR subject_name LIKE %s)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if category:
        conditions.append('category = %s')
        params.append(category)
    if status is not None:
        conditions.append('status = %s')
        params.append(status)

    where_clause = ' AND '.join(conditions)
    offset = (page - 1) * page_size

    count_sql = f"SELECT COUNT(*) as total FROM subject WHERE {where_clause}"
    total = query_one(count_sql, tuple(params))['total']

    list_sql = f"""
        SELECT id, subject_code, subject_name, category, credit, total_hours,
               description, status, created_at
        FROM subject
        WHERE {where_clause}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """
    list_data = query_list(list_sql, tuple(params + [page_size, offset]))

    for item in list_data:
        if item.get('created_at'):
            item['created_at'] = str(item['created_at'])
        for key, val in item.items():
            if isinstance(val, Decimal):
                item[key] = float(val)

    return make_response(data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'list': list_data
    })


@router.get('/all')
def get_all_subjects():
    subjects = query_list(
        "SELECT id, subject_code, subject_name, category, credit, status FROM subject WHERE status = 1 ORDER BY id"
    )
    for item in subjects:
        for key, val in item.items():
            if isinstance(val, Decimal):
                item[key] = float(val)
    return make_response(data=subjects)


@router.get('/{subject_id}')
def get_subject(subject_id: int):
    subject = query_one("""
        SELECT id, subject_code, subject_name, category, credit, total_hours,
               description, status
        FROM subject WHERE id = %s
    """, (subject_id,))

    if not subject:
        return make_response(code=404, msg='科目不存在')

    for key, val in subject.items():
        if isinstance(val, Decimal):
            subject[key] = float(val)

    return make_response(data=subject)


@router.post('')
def create_subject(data: SubjectCreate):
    exists = query_one(
        "SELECT id FROM subject WHERE subject_code = %s",
        (data.subject_code,)
    )
    if exists:
        return make_response(code=400, msg='科目编码已存在')

    name_exists = query_one(
        "SELECT id FROM subject WHERE subject_name = %s",
        (data.subject_name,)
    )
    if name_exists:
        return make_response(code=400, msg='科目名称已存在')

    sql = """
        INSERT INTO subject (subject_code, subject_name, category, credit, total_hours, description, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data.subject_code, data.subject_name, data.category,
        data.credit, data.total_hours, data.description, data.status
    )
    result = execute(sql, params)
    return make_response(msg='新增成功', data={'affected': result})


@router.put('/{subject_id}')
def update_subject(subject_id: int, data: SubjectUpdate):
    subject = query_one(
        "SELECT id FROM subject WHERE id = %s",
        (subject_id,)
    )
    if not subject:
        return make_response(code=404, msg='科目不存在')

    updates = []
    params = []

    if data.subject_name is not None:
        if data.subject_name and data.subject_name != subject.get('subject_name'):
            name_exists = query_one(
                "SELECT id FROM subject WHERE subject_name = %s AND id != %s",
                (data.subject_name, subject_id)
            )
            if name_exists:
                return make_response(code=400, msg='科目名称已存在')
        updates.append("subject_name = %s")
        params.append(data.subject_name)

    if data.category is not None:
        updates.append("category = %s")
        params.append(data.category)
    if data.credit is not None:
        updates.append("credit = %s")
        params.append(data.credit)
    if data.total_hours is not None:
        updates.append("total_hours = %s")
        params.append(data.total_hours)
    if data.description is not None:
        updates.append("description = %s")
        params.append(data.description)
    if data.status is not None:
        updates.append("status = %s")
        params.append(data.status)

    if not updates:
        return make_response(msg='没有需要更新的字段')

    try:
        sql = f"UPDATE subject SET {', '.join(updates)} WHERE id = %s"
        params.append(subject_id)
        execute(sql, tuple(params))
        return make_response(msg='更新成功')
    except Exception as e:
        error_msg = str(e)
        if 'Duplicate entry' in error_msg:
            if 'uk_subject_name' in error_msg:
                return make_response(code=400, msg='科目名称已存在')
        return make_response(code=500, msg=f'更新失败: {error_msg}')


@router.delete('/{subject_id}')
def delete_subject(subject_id: int):
    subject = query_one(
        "SELECT id FROM subject WHERE id = %s",
        (subject_id,)
    )
    if not subject:
        return make_response(code=404, msg='科目不存在')

    has_scores = query_one(
        "SELECT id FROM score WHERE subject_id = %s LIMIT 1",
        (subject_id,)
    )
    if has_scores:
        return make_response(code=400, msg='该科目有关联成绩记录，无法删除。请先删除相关成绩后再试。')

    try:
        execute("DELETE FROM subject WHERE id = %s", (subject_id,))
        return make_response(msg='删除成功')
    except Exception as e:
        error_msg = str(e)
        if 'CONSTRAINT' in error_msg or 'foreign key' in error_msg.lower():
            return make_response(code=400, msg='该科目有关联数据，无法删除')
        return make_response(code=500, msg=f'删除失败: {error_msg}')