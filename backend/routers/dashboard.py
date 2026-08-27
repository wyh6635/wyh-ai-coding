from fastapi import APIRouter, Depends
from typing import Optional
from decimal import Decimal
from database import query_one, query_list
from utils.response import make_response

router = APIRouter(prefix='/api/dashboard', tags=['数据看板'])


@router.get('/stats')
def get_dashboard_stats():
    student_total = query_one("SELECT COUNT(*) as total FROM student WHERE deleted = 0")['total']
    student_active = query_one("SELECT COUNT(*) as total FROM student WHERE deleted = 0 AND status = 1")['total']
    subject_total = query_one("SELECT COUNT(*) as total FROM subject WHERE status = 1")['total']
    subject_all = query_one("SELECT COUNT(*) as total FROM subject")['total']
    score_total = query_one("SELECT COUNT(*) as total FROM score")['total']
    exam_count = query_one("SELECT COUNT(DISTINCT CONCAT(exam_type, '-', IFNULL(term, ''))) as total FROM score")['total']

    return make_response(data={
        'student_total': student_total,
        'student_active': student_active,
        'subject_total': subject_total,
        'subject_all': subject_all,
        'score_total': score_total,
        'exam_count': exam_count
    })


@router.get('/subject-scores')
def get_subject_scores():
    stats = query_list("""
        SELECT 
            sub.id,
            sub.subject_name,
            sub.subject_code,
            COUNT(s.id) as score_count,
            ROUND(AVG(s.score_value), 1) as avg_score
        FROM subject sub
        LEFT JOIN score s ON sub.id = s.subject_id
        WHERE sub.status = 1
        GROUP BY sub.id, sub.subject_name, sub.subject_code
        ORDER BY avg_score DESC
    """)

    for item in stats:
        if item.get('avg_score'):
            item['avg_score'] = float(item['avg_score'])
        else:
            item['avg_score'] = 0
        if item.get('score_count'):
            item['score_count'] = int(item['score_count'])
        else:
            item['score_count'] = 0

    return make_response(data=stats)


@router.get('/recent-students')
def get_recent_students(limit: int = 5):
    students = query_list("""
        SELECT id, student_no, name, class_name, status, created_at
        FROM student WHERE deleted = 0
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    for item in students:
        if item.get('created_at'):
            item['created_at'] = str(item['created_at'])

    return make_response(data=students)


@router.get('/recent-scores')
def get_recent_scores(limit: int = 5):
    scores = query_list("""
        SELECT s.id, s.score_value, s.grade_level, s.exam_type, s.term,
               st.name as student_name, st.student_no,
               sub.subject_name
        FROM score s
        JOIN student st ON s.student_id = st.id
        JOIN subject sub ON s.subject_id = sub.id
        ORDER BY s.id DESC
        LIMIT %s
    """, (limit,))

    for item in scores:
        if item.get('exam_date'):
            item['exam_date'] = str(item['exam_date'])
        for key, val in item.items():
            if isinstance(val, Decimal):
                item[key] = float(val)

    return make_response(data=scores)


@router.get('/exam-types')
def get_exam_types():
    types = [
        {'value': 1, 'label': '期中考试'},
        {'value': 2, 'label': '期末考试'},
        {'value': 3, 'label': '平时测验'},
        {'value': 4, 'label': '补考'}
    ]
    return make_response(data=types)


@router.get('/categories')
def get_categories():
    categories = query_list("""
        SELECT DISTINCT category FROM subject WHERE category IS NOT NULL ORDER BY category
    """)
    return make_response(data=[c['category'] for c in categories if c['category']])


@router.get('/class-names')
def get_class_names():
    classes = query_list("""
        SELECT DISTINCT class_name FROM student 
        WHERE class_name IS NOT NULL AND deleted = 0 
        ORDER BY class_name
    """)
    return make_response(data=[c['class_name'] for c in classes if c['class_name']])