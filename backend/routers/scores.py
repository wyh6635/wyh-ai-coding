from fastapi import APIRouter
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, field_validator
from database import query_one, query_list, execute
from utils.response import make_response

router = APIRouter(prefix='/api/scores', tags=['成绩管理'])


class ScoreCreate(BaseModel):
    student_id: int
    subject_id: int
    score_value: float
    exam_type: int = 1
    exam_date: Optional[str] = None
    term: Optional[str] = None
    remark: Optional[str] = None

    @field_validator('student_id', 'subject_id')
    @classmethod
    def validate_ids(cls, v, info):
        if not v or v <= 0:
            raise ValueError(f'{info.field_name}必须大于0')
        return v

    @field_validator('score_value')
    @classmethod
    def validate_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('成绩必须在0-100之间')
        return v


class ScoreBatchCreate(BaseModel):
    student_id: int
    scores: list


class ScoreUpdate(BaseModel):
    score_value: Optional[float] = None
    exam_type: Optional[int] = None
    exam_date: Optional[str] = None
    term: Optional[str] = None
    remark: Optional[str] = None


def calc_grade_level(score: float) -> str:
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


@router.get('')
def list_scores(
    page: int = 1,
    page_size: int = 10,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    exam_type: Optional[int] = None,
    term: Optional[str] = None,
    keyword: Optional[str] = None,
    class_name: Optional[str] = None
):
    conditions = ['st.deleted = 0']
    params = []

    if student_id:
        conditions.append('s.student_id = %s')
        params.append(student_id)
    if subject_id:
        conditions.append('s.subject_id = %s')
        params.append(subject_id)
    if exam_type:
        conditions.append('s.exam_type = %s')
        params.append(exam_type)
    if term:
        conditions.append('s.term LIKE %s')
        params.append(f'%{term}%')
    if keyword:
        conditions.append('(st.name LIKE %s OR st.student_no LIKE %s)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if class_name:
        conditions.append('st.class_name = %s')
        params.append(class_name)

    where_clause = ' AND '.join(conditions)
    offset = (page - 1) * page_size

    count_sql = f"""
        SELECT COUNT(*) as total FROM score s
        JOIN student st ON s.student_id = st.id
        JOIN subject sub ON s.subject_id = sub.id
        WHERE {where_clause}
    """
    total = query_one(count_sql, tuple(params))['total']

    list_sql = f"""
        SELECT s.id, s.student_id, s.subject_id, s.score_value, s.grade_level,
               s.exam_type, s.exam_date, s.term, s.remark,
               st.student_no, st.name as student_name, st.class_name,
               sub.subject_code, sub.subject_name
        FROM score s
        JOIN student st ON s.student_id = st.id
        JOIN subject sub ON s.subject_id = sub.id
        WHERE {where_clause}
        ORDER BY s.id DESC
        LIMIT %s OFFSET %s
    """
    list_data = query_list(list_sql, tuple(params + [page_size, offset]))

    for item in list_data:
        if item.get('exam_date'):
            item['exam_date'] = str(item['exam_date'])
        if item.get('score_value') is not None:
            item['score_value'] = float(item['score_value'])
        for key, val in item.items():
            if isinstance(val, Decimal):
                item[key] = float(val)

    return make_response(data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'list': list_data
    })


@router.get('/{score_id}')
def get_score(score_id: int):
    score = query_one("""
        SELECT s.*, st.student_no, st.name as student_name,
               sub.subject_code, sub.subject_name
        FROM score s
        JOIN student st ON s.student_id = st.id
        JOIN subject sub ON s.subject_id = sub.id
        WHERE s.id = %s
    """, (score_id,))

    if not score:
        return make_response(code=404, msg='成绩不存在')

    if score.get('exam_date'):
        score['exam_date'] = str(score['exam_date'])
    if score.get('score_value') is not None:
        score['score_value'] = float(score['score_value'])
    for key, val in score.items():
        if isinstance(val, Decimal):
            score[key] = float(val)

    return make_response(data=score)


@router.post('')
def create_score(data: ScoreCreate):
    student = query_one("SELECT id FROM student WHERE id = %s AND deleted = 0", (data.student_id,))
    if not student:
        return make_response(code=400, msg='学员不存在')

    subject = query_one("SELECT id FROM subject WHERE id = %s AND status = 1", (data.subject_id,))
    if not subject:
        return make_response(code=400, msg='科目不存在或已停用')

    exists = query_one("""
        SELECT id FROM score
        WHERE student_id = %s AND subject_id = %s AND exam_type = %s
        AND (%s IS NULL OR term = %s)
    """, (data.student_id, data.subject_id, data.exam_type, data.term, data.term))
    if exists:
        return make_response(code=400, msg='该学员该科目该次考试已有成绩')

    grade_level = calc_grade_level(data.score_value)

    sql = """
        INSERT INTO score (student_id, subject_id, score_value, grade_level,
                          exam_type, exam_date, term, remark)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data.student_id, data.subject_id, data.score_value, grade_level,
        data.exam_type, data.exam_date, data.term, data.remark
    )
    result = execute(sql, params)
    return make_response(msg='录入成功', data={'affected': result})


@router.post('/batch')
def batch_create_scores(data: ScoreBatchCreate):
    student = query_one("SELECT id FROM student WHERE id = %s AND deleted = 0", (data.student_id,))
    if not student:
        return make_response(code=400, msg='学员不存在')

    success_count = 0
    errors = []

    for item in data.scores:
        try:
            subject_id = item.get('subject_id')
            score_value = float(item.get('score_value', 0))
            exam_type = item.get('exam_type', 1)
            exam_date = item.get('exam_date')
            term = item.get('term')
            remark = item.get('remark')

            if not subject_id or score_value < 0 or score_value > 100:
                errors.append(f'科目{subject_id}: 成绩无效')
                continue

            subject = query_one("SELECT id FROM subject WHERE id = %s AND status = 1", (subject_id,))
            if not subject:
                errors.append(f'科目{subject_id}: 不存在或已停用')
                continue

            exists = query_one("""
                SELECT id FROM score
                WHERE student_id = %s AND subject_id = %s AND exam_type = %s
                AND (%s IS NULL OR term = %s)
            """, (data.student_id, subject_id, exam_type, term, term))
            if exists:
                errors.append(f'科目{subject_id}: 成绩已存在')
                continue

            grade_level = calc_grade_level(score_value)
            sql = """
                INSERT INTO score (student_id, subject_id, score_value, grade_level,
                                  exam_type, exam_date, term, remark)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute(sql, (
                data.student_id, subject_id, score_value, grade_level,
                exam_type, exam_date, term, remark
            ))
            success_count += 1
        except Exception as e:
            errors.append(f'条目错误: {str(e)}')

    msg = f'成功录入 {success_count} 条'
    if errors:
        msg += f'，失败 {len(errors)} 条: {"; ".join(errors[:3])}'
    return make_response(msg=msg, data={'success': success_count, 'errors': errors})


@router.put('/{score_id}')
def update_score(score_id: int, data: ScoreUpdate):
    score = query_one("SELECT id FROM score WHERE id = %s", (score_id,))
    if not score:
        return make_response(code=404, msg='成绩不存在')

    updates = []
    params = []
    if data.score_value is not None:
        if data.score_value < 0 or data.score_value > 100:
            return make_response(code=400, msg='成绩必须在0-100之间')
        updates.append("score_value = %s")
        params.append(data.score_value)
        updates.append("grade_level = %s")
        params.append(calc_grade_level(data.score_value))
    if data.exam_type is not None:
        updates.append("exam_type = %s")
        params.append(data.exam_type)
    if data.exam_date is not None:
        updates.append("exam_date = %s")
        params.append(data.exam_date)
    if data.term is not None:
        updates.append("term = %s")
        params.append(data.term)
    if data.remark is not None:
        updates.append("remark = %s")
        params.append(data.remark)

    if not updates:
        return make_response(msg='没有需要更新的字段')

    sql = f"UPDATE score SET {', '.join(updates)} WHERE id = %s"
    params.append(score_id)
    execute(sql, tuple(params))
    return make_response(msg='更新成功')


@router.delete('/{score_id}')
def delete_score(score_id: int):
    score = query_one("SELECT id FROM score WHERE id = %s", (score_id,))
    if not score:
        return make_response(code=404, msg='成绩不存在')

    execute("DELETE FROM score WHERE id = %s", (score_id,))
    return make_response(msg='删除成功')


@router.get('/stats/summary')
def get_scores_summary():
    subject_stats = query_list("""
        SELECT 
            sub.id,
            sub.subject_name,
            sub.subject_code,
            sub.category,
            COUNT(s.id) as score_count,
            ROUND(AVG(s.score_value), 1) as avg_score,
            MAX(s.score_value) as max_score,
            MIN(s.score_value) as min_score
        FROM subject sub
        LEFT JOIN score s ON sub.id = s.subject_id
        WHERE sub.status = 1
        GROUP BY sub.id, sub.subject_name, sub.subject_code, sub.category
        ORDER BY avg_score DESC
    """)

    for item in subject_stats:
        for key, val in item.items():
            if isinstance(val, Decimal):
                item[key] = float(val)

    exam_types = query_list("""
        SELECT DISTINCT exam_type, COUNT(*) as cnt
        FROM score
        GROUP BY exam_type
    """)

    terms = query_list("""
        SELECT DISTINCT term FROM score WHERE term IS NOT NULL ORDER BY term DESC
    """)

    return make_response(data={
        'subject_stats': subject_stats,
        'exam_types': exam_types,
        'terms': [t['term'] for t in terms if t['term']]
    })