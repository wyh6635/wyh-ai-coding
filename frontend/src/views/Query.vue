<template>
  <div class="query-page">
    <div class="page-header">
      <h1 class="page-title">数据查询</h1>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="按学员查询成绩" name="student">
        <div class="search-bar">
          <el-select v-model="studentForm.student_id" filterable placeholder="选择学员" style="width: 240px">
            <el-option v-for="s in students" :key="s.id" :label="`${s.student_no} - ${s.name}`" :value="s.id" />
          </el-select>
          <el-select v-model="studentForm.exam_type" placeholder="考试类型" clearable style="width: 140px">
            <el-option v-for="t in examTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
          <el-button type="primary" @click="queryStudentScores">查询</el-button>
        </div>

        <div v-if="studentResult" class="student-summary">
          <div class="summary-card">
            <div class="summary-item">
              <span class="label">学员</span>
              <span class="value">{{ studentResult.student_name }}</span>
            </div>
            <div class="summary-item">
              <span class="label">班级</span>
              <span class="value">{{ studentResult.class_name }}</span>
            </div>
            <div class="summary-item">
              <span class="label">科目数</span>
              <span class="value">{{ studentResult.scores.length }}</span>
            </div>
            <div class="summary-item highlight">
              <span class="label">平均分</span>
              <span class="value">{{ studentResult.avg_score?.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <el-table :data="studentResult?.scores || []" v-loading="loading" stripe>
          <el-table-column prop="subject_name" label="科目" width="160" />
          <el-table-column prop="score_value" label="成绩" width="100" align="center">
            <template #default="{ row }">
              <span :class="scoreClass(row.score_value)">{{ row.score_value?.toFixed(1) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="grade_level" label="等级" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="gradeTagType(row.grade_level)" size="small">{{ row.grade_level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="exam_type" label="考试类型" width="120">
            <template #default="{ row }">{{ examTypeText(row.exam_type) }}</template>
          </el-table-column>
          <el-table-column prop="term" label="学期" width="200" />
          <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        </el-table>
        <el-empty v-if="!loading && !studentResult?.scores.length" description="请选择学员后查询" />
      </el-tab-pane>

      <el-tab-pane label="班级成绩统计" name="class">
        <div class="search-bar">
          <el-select v-model="classForm.class_name" placeholder="选择班级" clearable style="width: 180px">
            <el-option v-for="cls in classNames" :key="cls" :label="cls" :value="cls" />
          </el-select>
          <el-select v-model="classForm.subject_id" placeholder="科目" clearable style="width: 180px">
            <el-option v-for="s in subjects" :key="s.id" :label="s.subject_name" :value="s.id" />
          </el-select>
          <el-select v-model="classForm.exam_type" placeholder="考试类型" clearable style="width: 140px">
            <el-option v-for="t in examTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
          <el-button type="primary" @click="queryClassScores">统计</el-button>
        </div>

        <div class="stats-summary" v-if="classResult">
          <el-descriptions :column="4" border>
            <el-descriptions-item label="班级">{{ classResult.class_name }}</el-descriptions-item>
            <el-descriptions-item label="学员人数">{{ classResult.student_count }}</el-descriptions-item>
            <el-descriptions-item label="参考人数">{{ classResult.reference_count }}</el-descriptions-item>
            <el-descriptions-item label="科目">{{ classResult.subject_name }}</el-descriptions-item>
            <el-descriptions-item label="平均分">
              <span class="score-a">{{ classResult.avg_score?.toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="最高分">
              <span class="score-a">{{ classResult.max_score?.toFixed(1) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="最低分">
              <span class="score-f">{{ classResult.min_score?.toFixed(1) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="及格率">
              <span :class="classResult.pass_rate >= 80 ? 'score-a' : classResult.pass_rate >= 60 ? 'score-c' : 'score-f'">
                {{ classResult.pass_rate?.toFixed(1) }}%
              </span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <el-table :data="classResult?.details || []" v-loading="loading" stripe style="margin-top: 16px">
          <el-table-column prop="student_no" label="学号" width="120" />
          <el-table-column prop="student_name" label="姓名" width="120" />
          <el-table-column prop="score_value" label="成绩" width="120" align="center">
            <template #default="{ row }">
              <span :class="scoreClass(row.score_value)">{{ row.score_value?.toFixed(1) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="grade_level" label="等级" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="gradeTagType(row.grade_level)" size="small">{{ row.grade_level }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && !classResult?.details?.length" description="请选择条件后统计" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getStudents, getAllSubjects, getExamTypes, getClassNames, getScores } from '../api'

const loading = ref(false)
const activeTab = ref('student')

const students = ref([])
const subjects = ref([])
const examTypes = ref([])
const classNames = ref([])

const studentForm = reactive({ student_id: null, exam_type: null })
const studentResult = ref(null)

const classForm = reactive({ class_name: '', subject_id: null, exam_type: null })
const classResult = ref(null)

const examTypeText = (t) => examTypes.value.find(x => x.value === t)?.label || '未知'
const scoreClass = (s) => {
  if (s >= 90) return 'score-a'
  if (s >= 80) return 'score-b'
  if (s >= 60) return 'score-c'
  return 'score-f'
}
const gradeTagType = (g) => ({ A: 'success', B: '', C: 'warning', D: 'danger', F: 'danger' }[g] || '')

const queryStudentScores = async () => {
  if (!studentForm.student_id) return
  loading.value = true
  try {
    const res = await getScores({
      page: 1, page_size: 500,
      student_id: studentForm.student_id,
      exam_type: studentForm.exam_type
    })
    if (res.code === 200) {
      const list = res.data.list
      if (!list.length) {
        studentResult.value = { student_name: '', class_name: '', scores: [], avg_score: 0 }
        return
      }
      const studentInfo = list[0]
      const scores = list.map(s => ({
        subject_name: s.subject_name,
        score_value: s.score_value,
        grade_level: s.grade_level,
        exam_type: s.exam_type,
        term: s.term,
        remark: s.remark
      }))
      const avg = scores.reduce((a, b) => a + b.score_value, 0) / scores.length
      studentResult.value = {
        student_name: studentInfo.student_name,
        class_name: studentInfo.class_name,
        scores,
        avg_score: avg
      }
    }
  } catch (e) {} finally { loading.value = false }
}

const queryClassScores = async () => {
  if (!classForm.subject_id) {
    classResult.value = null
    return
  }
  loading.value = true
  try {
    const res = await getScores({
      page: 1, page_size: 1000,
      subject_id: classForm.subject_id,
      class_name: classForm.class_name || undefined,
      exam_type: classForm.exam_type
    })
    if (res.code === 200) {
      const list = res.data.list
      const filtered = list.filter(s => !classForm.class_name || s.class_name === classForm.class_name)
      if (!filtered.length) {
        classResult.value = null
        return
      }
      const scores = filtered.map(s => s.score_value)
      const total = scores.length
      const sum = scores.reduce((a, b) => a + b, 0)
      const avg = sum / total
      const max = Math.max(...scores)
      const min = Math.min(...scores)
      const passCount = scores.filter(s => s >= 60).length
      const passRate = (passCount / total) * 100

      const subjectInfo = subjects.value.find(s => s.id === classForm.subject_id)

      classResult.value = {
        class_name: classForm.class_name || '全部班级',
        student_count: total,
        reference_count: total,
        subject_name: subjectInfo?.subject_name || '',
        avg_score: avg,
        max_score: max,
        min_score: min,
        pass_rate: passRate,
        details: filtered.map(s => ({
          student_no: s.student_no,
          student_name: s.student_name,
          score_value: s.score_value,
          grade_level: s.grade_level
        }))
      }
    }
  } catch (e) {} finally { loading.value = false }
}

const loadInitData = async () => {
  try {
    const [stuRes, subRes, typeRes, clsRes] = await Promise.all([
      getStudents({ page: 1, page_size: 200 }),
      getAllSubjects(),
      getExamTypes(),
      getClassNames()
    ])
    if (stuRes.code === 200) students.value = stuRes.data.list
    if (subRes.code === 200) subjects.value = subRes.data
    if (typeRes.code === 200) examTypes.value = typeRes.data
    if (clsRes.code === 200) classNames.value = clsRes.data
  } catch (e) {}
}

onMounted(() => {
  loadInitData()
})
</script>

<style lang="scss" scoped>
.query-page { max-width: 1400px; }

.page-header {
  margin-bottom: 20px;
  .page-title { font-size: 24px; font-weight: 600; color: #1e293b; margin: 0; }
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.student-summary { margin-bottom: 20px; }

.summary-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-radius: 12px;
}

.summary-item {
  .label { display: block; font-size: 12px; color: #64748b; margin-bottom: 4px; }
  .value { font-size: 20px; font-weight: 600; color: #1e293b; }
  &.highlight .value { color: #3b82f6; }
}

.stats-summary { margin-bottom: 16px; }

.score-a { color: #10b981; font-weight: 600; }
.score-b { color: #3b82f6; font-weight: 600; }
.score-c { color: #f59e0b; font-weight: 600; }
.score-f { color: #ef4444; font-weight: 600; }

:deep(.el-tabs--border-card > .el-tabs__header) {
  border: 1px solid #e2e8f0;
  border-radius: 8px 8px 0 0;
}

:deep(.el-tabs--border-card > .el-tabs__content) {
  border: 1px solid #e2e8f0;
  border-radius: 0 0 8px 8px;
}
</style>