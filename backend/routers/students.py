from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel, field_validator
from database import query_one, query_list, execute
from utils.response import make_response

router = APIRouter(prefix='/api/students', tags=['学员管理'])


class StudentCreate(BaseModel):
    student_no: str
    name: str
    gender: int = 1
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: str
    class_name: Optional[str] = None
    status: int = 1

    @field_validator('student_no', 'name', 'enrollment_date')
    @classmethod
    def validate_required(cls, v, info):
        if not v or not str(v).strip():
            raise ValueError(f'{info.field_name}不能为空')
        return str(v).strip()


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[int] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None
    address: Optional[str] = None
    class_name: Optional[str] = None
    status: Optional[int] = None


@router.get('')
def list_students(
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
    class_name: Optional[str] = None,
    status: Optional[int] = None
):
    conditions = ['deleted = 0']
    params = []

    if keyword:
        conditions.append('(student_no LIKE %s OR name LIKE %s)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if class_name:
        conditions.append('class_name = %s')
        params.append(class_name)
    if status is not None:
        conditions.append('status = %s')
        params.append(status)

    where_clause = ' AND '.join(conditions)
    offset = (page - 1) * page_size

    count_sql = f"SELECT COUNT(*) as total FROM student WHERE {where_clause}"
    total = query_one(count_sql, tuple(params))['total']

    list_sql = f"""
        SELECT id, student_no, name, gender, birth_date, phone, email,
               id_card, address, enrollment_date, class_name, status, created_at
        FROM student
        WHERE {where_clause}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """
    list_data = query_list(list_sql, tuple(params + [page_size, offset]))

    for item in list_data:
        if item.get('birth_date'):
            item['birth_date'] = str(item['birth_date'])
        if item.get('enrollment_date'):
            item['enrollment_date'] = str(item['enrollment_date'])
        if item.get('created_at'):
            item['created_at'] = str(item['created_at'])

    return make_response(data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'list': list_data
    })


@router.get('/{student_id}')
def get_student(student_id: int):
    student = query_one("""
        SELECT id, student_no, name, gender, birth_date, phone, email,
               id_card, address, enrollment_date, class_name, status
        FROM student WHERE id = %s AND deleted = 0
    """, (student_id,))

    if not student:
        return make_response(code=404, msg='学员不存在')

    if student.get('birth_date'):
        student['birth_date'] = str(student['birth_date'])
    if student.get('enrollment_date'):
        student['enrollment_date'] = str(student['enrollment_date'])

    return make_response(data=student)


@router.post('')
def create_student(data: StudentCreate):
    exists = query_one(
        "SELECT id FROM student WHERE student_no = %s AND deleted = 0",
        (data.student_no,)
    )
    if exists:
        return make_response(code=400, msg='学号已存在')

    if data.phone:
        phone_exists = query_one(
            "SELECT id FROM student WHERE phone = %s AND deleted = 0",
            (data.phone,)
        )
        if phone_exists:
            return make_response(code=400, msg='手机号已被使用')

    if data.id_card:
        id_exists = query_one(
            "SELECT id FROM student WHERE id_card = %s AND deleted = 0",
            (data.id_card,)
        )
        if id_exists:
            return make_response(code=400, msg='身份证号已被使用')

    try:
        sql = """
            INSERT INTO student (student_no, name, gender, birth_date, phone, email,
                                 id_card, address, enrollment_date, class_name, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data.student_no, data.name, data.gender, data.birth_date,
            data.phone, data.email, data.id_card, data.address,
            data.enrollment_date, data.class_name, data.status
        )
        result = execute(sql, params)
        return make_response(msg='新增成功', data={'affected': result})
    except Exception as e:
        error_msg = str(e)
        if 'Duplicate entry' in error_msg:
            if 'uk_phone' in error_msg:
                return make_response(code=400, msg='手机号已被使用')
            if 'uk_id_card' in error_msg:
                return make_response(code=400, msg='身份证号已被使用')
            if 'uk_student_no' in error_msg:
                return make_response(code=400, msg='学号已存在')
        return make_response(code=500, msg=f'新增失败: {error_msg}')


@router.put('/{student_id}')
def update_student(student_id: int, data: StudentUpdate):
    student = query_one(
        "SELECT id FROM student WHERE id = %s AND deleted = 0",
        (student_id,)
    )
    if not student:
        return make_response(code=404, msg='学员不存在')

    updates = []
    params = []

    if data.name is not None:
        updates.append("name = %s")
        params.append(data.name)
    if data.gender is not None:
        updates.append("gender = %s")
        params.append(data.gender)
    if data.birth_date is not None:
        updates.append("birth_date = %s")
        params.append(data.birth_date)
    if data.phone is not None:
        if data.phone and data.phone != student.get('phone'):
            phone_exists = query_one(
                "SELECT id FROM student WHERE phone = %s AND deleted = 0 AND id != %s",
                (data.phone, student_id)
            )
            if phone_exists:
                return make_response(code=400, msg='手机号已被其他学员使用')
        updates.append("phone = %s")
        params.append(data.phone)
    if data.email is not None:
        updates.append("email = %s")
        params.append(data.email)
    if data.id_card is not None:
        if data.id_card and data.id_card != student.get('id_card'):
            id_exists = query_one(
                "SELECT id FROM student WHERE id_card = %s AND deleted = 0 AND id != %s",
                (data.id_card, student_id)
            )
            if id_exists:
                return make_response(code=400, msg='身份证号已被其他学员使用')
        updates.append("id_card = %s")
        params.append(data.id_card)
    if data.address is not None:
        updates.append("address = %s")
        params.append(data.address)
    if data.class_name is not None:
        updates.append("class_name = %s")
        params.append(data.class_name)
    if data.status is not None:
        updates.append("status = %s")
        params.append(data.status)

    if not updates:
        return make_response(msg='没有需要更新的字段')

    try:
        sql = f"UPDATE student SET {', '.join(updates)} WHERE id = %s"
        params.append(student_id)
        execute(sql, tuple(params))
        return make_response(msg='更新成功')
    except Exception as e:
        error_msg = str(e)
        if 'Duplicate entry' in error_msg:
            if 'uk_phone' in error_msg:
                return make_response(code=400, msg='手机号已被其他学员使用')
            if 'uk_id_card' in error_msg:
                return make_response(code=400, msg='身份证号已被其他学员使用')
        return make_response(code=500, msg=f'更新失败: {error_msg}')


@router.delete('/{student_id}')
def delete_student(student_id: int):
    student = query_one(
        "SELECT id FROM student WHERE id = %s AND deleted = 0",
        (student_id,)
    )
    if not student:
        return make_response(code=404, msg='学员不存在')

    has_scores = query_one(
        "SELECT id FROM score WHERE student_id = %s LIMIT 1",
        (student_id,)
    )
    if has_scores:
        return make_response(code=400, msg='该学员有关联成绩记录，无法删除。请先删除相关成绩后再试。')

    try:
        execute("UPDATE student SET deleted = 1 WHERE id = %s", (student_id,))
        return make_response(msg='删除成功')
    except Exception as e:
        return make_response(code=500, msg=f'删除失败: {str(e)}')