-- =====================================================
-- 学员管理系统数据库设计
-- 数据库: student_management
-- 工具: DBeaver 26.1.4
-- MySQL版本: 8.0+
-- =====================================================

-- 第一步：创建数据库（单独选中这一部分执行）
CREATE DATABASE IF NOT EXISTS `student_management` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 第二步：切换到该数据库（单独选中这一部分执行）
USE `student_management`;

-- =====================================================
-- 第三步：创建表结构（选中以下所有CREATE语句执行）
-- =====================================================

-- 0. 用户表（登录用）
CREATE TABLE IF NOT EXISTS `user` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID（主键）',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL COMMENT '密码（加密存储）',
    `real_name` VARCHAR(50) NULL COMMENT '真实姓名',
    `avatar` VARCHAR(255) NULL COMMENT '头像URL',
    `email` VARCHAR(100) NULL COMMENT '邮箱',
    `phone` VARCHAR(20) NULL COMMENT '手机号',
    `role` VARCHAR(30) NOT NULL DEFAULT 'student' COMMENT '角色：admin-管理员，student-学员',
    `status` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
    `last_login_time` DATETIME NULL COMMENT '最后登录时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_role` (`role`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表';

-- 初始用户数据（密码为明文: 123456，实际存储为SHA256加密）
INSERT INTO `user` (`username`, `password`, `real_name`, `email`, `phone`, `role`, `status`) VALUES
('admin', SHA2('123456', 256), '系统管理员', 'admin@edu.cn', '13800000000', 'admin', 1),
('student001', SHA2('123456', 256), '张明', 'zhangming@edu.cn', '13800001111', 'student', 1);

-- 1. 学员表
CREATE TABLE IF NOT EXISTS `student` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '学员ID（主键）',
    `student_no` VARCHAR(20) NOT NULL COMMENT '学号（唯一）',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `gender` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '性别：1-男，2-女，0-未知',
    `birth_date` DATE NULL COMMENT '出生日期',
    `phone` VARCHAR(20) NULL COMMENT '手机号',
    `email` VARCHAR(100) NULL COMMENT '电子邮箱',
    `id_card` VARCHAR(18) NULL COMMENT '身份证号',
    `address` VARCHAR(200) NULL COMMENT '家庭地址',
    `enrollment_date` DATE NOT NULL COMMENT '入学日期',
    `class_name` VARCHAR(50) NULL COMMENT '班级名称',
    `status` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态：1-在读，2-休学，3-毕业，4-退学',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_student_no` (`student_no`),
    UNIQUE KEY `uk_phone` (`phone`),
    UNIQUE KEY `uk_id_card` (`id_card`),
    KEY `idx_name` (`name`),
    KEY `idx_status` (`status`),
    KEY `idx_class_name` (`class_name`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学员基本信息表';

-- 2. 科目表
CREATE TABLE IF NOT EXISTS `subject` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '科目ID（主键）',
    `subject_code` VARCHAR(20) NOT NULL COMMENT '科目编码（唯一）',
    `subject_name` VARCHAR(50) NOT NULL COMMENT '科目名称',
    `category` VARCHAR(30) NULL COMMENT '科目类别：如-文化课、专业课、选修课',
    `credit` DECIMAL(5,2) UNSIGNED DEFAULT 0.00 COMMENT '学分',
    `total_hours` INT UNSIGNED DEFAULT 0 COMMENT '总学时',
    `description` VARCHAR(500) NULL COMMENT '科目描述',
    `status` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态：1-启用，0-停用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_subject_code` (`subject_code`),
    UNIQUE KEY `uk_subject_name` (`subject_name`),
    KEY `idx_category` (`category`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='科目信息表';

-- 3. 成绩表
CREATE TABLE IF NOT EXISTS `score` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '成绩记录ID（主键）',
    `student_id` BIGINT UNSIGNED NOT NULL COMMENT '学员ID（外键 → student.id）',
    `subject_id` BIGINT UNSIGNED NOT NULL COMMENT '科目ID（外键 → subject.id）',
    `score_value` DECIMAL(5,2) NULL COMMENT '成绩分数（百分制，允许小数）',
    `grade_level` CHAR(2) NULL COMMENT '等级：A、B、C、D、F',
    `exam_type` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '考试类型：1-期中考试，2-期末考试，3-平时测验，4-补考',
    `exam_date` DATE NULL COMMENT '考试日期',
    `term` VARCHAR(20) NULL COMMENT '学期：如-2025-2026学年第一学期',
    `remark` VARCHAR(200) NULL COMMENT '备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_student_subject_exam` (`student_id`, `subject_id`, `exam_type`, `term`),
    KEY `idx_subject_id` (`subject_id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_exam_type` (`exam_type`),
    KEY `idx_term` (`term`),
    CONSTRAINT `fk_score_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_score_subject` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学员成绩表';

-- 创建额外索引
CREATE INDEX idx_term_student ON score(term, student_id);
CREATE INDEX idx_term_subject ON score(term, subject_id);

-- =====================================================
-- 第四步：插入初始数据（选中以下INSERT语句执行）
-- =====================================================

-- 插入科目数据
INSERT INTO `subject` (`subject_code`, `subject_name`, `category`, `credit`, `total_hours`, `description`) VALUES
('MATH101', '高等数学', '文化课', 4.00, 64, '大学数学基础课程'),
('ENGL101', '大学英语', '文化课', 3.00, 48, '英语听说读写综合训练'),
('PHYS101', '大学物理', '文化课', 4.00, 56, '物理学基础理论'),
('CS101', '计算机基础', '专业课', 3.00, 48, '计算机科学导论与编程基础'),
('ECON101', '经济学原理', '选修课', 2.00, 32, '微观与宏观经济学基础'),
('PSYCH101', '心理学概论', '选修课', 2.00, 32, '心理学基础知识'),
('MATH201', '线性代数', '文化课', 3.00, 48, '矩阵与线性空间理论'),
('CS201', '数据结构', '专业课', 4.00, 64, '数据结构与算法分析');

-- 插入学员数据
INSERT INTO `student` (`student_no`, `name`, `gender`, `birth_date`, `phone`, `email`, `id_card`, `address`, `enrollment_date`, `class_name`, `status`) VALUES
('S20240001', '张明', 1, '2006-03-15', '13800001111', 'zhangming@edu.cn', '110101200603151234', '北京市海淀区学院路1号', '2024-09-01', '计算机应用技术1班', 1),
('S20240002', '李婷', 2, '2006-07-22', '13800002222', 'liting@edu.cn', '110101200607225678', '北京市朝阳区建国路2号', '2024-09-01', '计算机应用技术1班', 1),
('S20240003', '王浩', 1, '2005-11-10', '13800003333', 'wanghao@edu.cn', '110101200511103456', '上海市浦东新区陆家嘴路3号', '2024-09-01', '计算机应用技术2班', 1),
('S20240004', '刘洋', 2, '2006-09-05', '13800004444', 'liuyang@edu.cn', '110101200609057890', '广州市天河区体育西路4号', '2024-09-01', '计算机应用技术2班', 1),
('S20230001', '陈晨', 1, '2005-01-20', '13800005555', 'chenchen@edu.cn', '110101200501201111', '深圳市南山区科技园路5号', '2023-09-01', '软件工程1班', 3),
('S20230002', '赵雪', 2, '2005-04-18', '13800006666', 'zhaoxue@edu.cn', '110101200504182222', '杭州市西湖区文三路6号', '2023-09-01', '软件工程1班', 2),
('S20250001', '孙悦', 2, '2007-02-28', '13800007777', 'sunyue@edu.cn', '110101200702283333', '成都市武侯区天府大道7号', '2025-03-01', '人工智能技术1班', 1);

-- 插入成绩数据
INSERT INTO `score` (`student_id`, `subject_id`, `score_value`, `grade_level`, `exam_type`, `exam_date`, `term`, `remark`) VALUES
(1, 1, 85.50, 'B', 2, '2025-01-10', '2024-2025学年第一学期', '期末成绩优秀'),
(1, 2, 78.00, 'C', 2, '2025-01-12', '2024-2025学年第一学期', NULL),
(1, 3, 92.00, 'A', 2, '2025-01-14', '2024-2025学年第一学期', NULL),
(2, 1, 88.00, 'B', 2, '2025-01-10', '2024-2025学年第一学期', NULL),
(2, 2, 95.00, 'A', 2, '2025-01-12', '2024-2025学年第一学期', '年级第一'),
(2, 3, 76.50, 'C', 2, '2025-01-14', '2024-2025学年第一学期', '需加强物理基础'),
(3, 1, 65.00, 'D', 2, '2025-01-10', '2024-2025学年第一学期', NULL),
(3, 4, 82.00, 'B', 2, '2025-01-16', '2024-2025学年第一学期', NULL),
(4, 1, 70.00, 'C', 2, '2025-01-10', '2024-2025学年第一学期', NULL),
(4, 4, 90.50, 'A', 2, '2025-01-16', '2024-2025学年第一学期', '编程能力突出'),
(5, 1, 88.00, 'B', 2, '2024-01-12', '2023-2024学年第一学期', NULL),
(5, 4, 75.00, 'C', 2, '2024-01-16', '2023-2024学年第一学期', NULL),
(6, 1, 52.00, 'F', 2, '2024-01-12', '2023-2024学年第一学期', '需要补考'),
(7, 2, 67.00, 'D', 1, '2025-04-20', '2024-2025学年第二学期', '期中考试'),
(1, 5, 82.00, 'B', 1, '2025-04-22', '2024-2025学年第二学期', NULL),
(2, 5, 91.00, 'A', 1, '2025-04-22', '2024-2025学年第二学期', NULL),
(6, 1, 68.00, 'D', 4, '2024-03-01', '2023-2024学年第一学期', '补考通过');

-- =====================================================
-- 第五步：创建视图（可选）
-- =====================================================
CREATE OR REPLACE VIEW `v_student_score` AS
SELECT 
    s.student_no AS `学号`,
    s.name AS `姓名`,
    s.class_name AS `班级`,
    sub.subject_code AS `科目编码`,
    sub.subject_name AS `科目名称`,
    sc.score_value AS `成绩`,
    sc.grade_level AS `等级`,
    CASE sc.exam_type
        WHEN 1 THEN '期中考试'
        WHEN 2 THEN '期末考试'
        WHEN 3 THEN '平时测验'
        WHEN 4 THEN '补考'
        ELSE '未知'
    END AS `考试类型`,
    sc.term AS `学期`,
    sc.exam_date AS `考试日期`
FROM score sc
INNER JOIN student s ON sc.student_id = s.id
INNER JOIN subject sub ON sc.subject_id = sub.id
WHERE s.deleted = 0
ORDER BY s.student_no, sc.term DESC, sc.exam_type;

-- =====================================================
-- 验证数据
-- =====================================================
SELECT COUNT(*) AS `学员总数` FROM student;
SELECT COUNT(*) AS `科目总数` FROM subject;
SELECT COUNT(*) AS `成绩记录总数` FROM score;

-- =====================================================
-- 查询示例：查看所有成绩视图
-- =====================================================
SELECT * FROM v_student_score LIMIT 10;

-- =====================================================
-- 结束
-- =====================================================