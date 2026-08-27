<template>
  <div class="scores-page">
    <div class="page-header">
      <h1 class="page-title">成绩管理</h1>
      <div>
        <el-button type="success" @click="openBatchDialog()">
          <el-icon><Files /></el-icon>批量录入
        </el-button>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>录入成绩
        </el-button>
      </div>
    </div>

    <div class="card">
      <div class="search-bar">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索学员姓名或学号"
          clearable
          style="width: 220px"
          :prefix-icon="Search"
          @keyup.enter="loadData"
        />
        <el-select v-model="searchParams.exam_type" placeholder="考试类型" clearable style="width: 140px">
          <el-option v-for="t in examTypes" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-input v-model="searchParams.term" placeholder="学期" clearable style="width: 180px" />
        <el-button type="primary" @click="loadData">
          <el-icon><Search /></el-icon>搜索
        </el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="subject_name" label="科目" width="140" />
        <el-table-column prop="score_value" label="成绩" width="100" align="center">
          <template #default="{ row }">
            <span :class="scoreClass(row.score_value)">{{ row.score_value?.toFixed(1) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="grade_level" label="等级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="gradeTagType(row.grade_level)" size="small" effect="dark">
              {{ row.grade_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_type" label="考试类型" width="120">
          <template #default="{ row }">
            {{ examTypeText(row.exam_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="term" label="学期" width="180" />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑成绩' : '录入成绩'" width="500px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="学员" prop="student_id">
          <el-select v-model="form.student_id" filterable placeholder="选择学员" style="width: 100%">
            <el-option v-for="s in students" :key="s.id" :label="`${s.student_no} - ${s.name}`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="科目" prop="subject_id">
          <el-select v-model="form.subject_id" placeholder="选择科目" style="width: 100%">
            <el-option v-for="s in subjects" :key="s.id" :label="s.subject_name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="成绩" prop="score_value">
              <el-input-number v-model="form.score_value" :min="0" :max="100" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="考试类型" prop="exam_type">
              <el-select v-model="form.exam_type" style="width: 100%">
                <el-option v-for="t in examTypes" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考试日期">
          <el-date-picker v-model="form.exam_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="学期">
          <el-input v-model="form.term" placeholder="如: 2024-2025学年第一学期" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialogVisible" title="批量录入成绩" width="700px" :close-on-click-modal="false">
      <el-form label-width="100px">
        <el-form-item label="选择学员">
          <el-select v-model="batchForm.student_id" filterable placeholder="选择学员" style="width: 100%" @change="onBatchStudentChange">
            <el-option v-for="s in students" :key="s.id" :label="`${s.student_no} - ${s.name}`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="考试类型">
              <el-select v-model="batchForm.exam_type" style="width: 100%">
                <el-option v-for="t in examTypes" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="学期">
              <el-input v-model="batchForm.term" placeholder="如: 2024-2025学年第一学期" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="batch-table">
        <div class="batch-header">
          <span>科目</span>
          <span>成绩(0-100)</span>
          <span>操作</span>
        </div>
        <div v-for="(item, index) in batchForm.scores" :key="index" class="batch-row">
          <el-select v-model="item.subject_id" placeholder="选择科目">
            <el-option v-for="s in subjects" :key="s.id" :label="s.subject_name" :value="s.id" />
          </el-select>
          <el-input-number v-model="item.score_value" :min="0" :max="100" :step="0.5" />
          <el-button type="danger" link @click="removeBatchItem(index)">删除</el-button>
        </div>
        <div class="batch-empty" v-if="!batchForm.scores.length">暂无添加，点击下方按钮添加</div>
        <el-button type="primary" link @click="addBatchItem">+ 添加科目</el-button>
      </div>

      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleBatchSubmit">批量提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Files } from '@element-plus/icons-vue'
import {
  getScores, createScore, updateScore, deleteScore,
  getAllSubjects, getStudents, getExamTypes, batchCreateScores
} from '../api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const batchDialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)

const students = ref([])
const subjects = ref([])
const examTypes = ref([])

const searchParams = reactive({ keyword: '', exam_type: null, term: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref([])

const form = reactive({
  student_id: null, subject_id: null, score_value: 0,
  exam_type: 1, exam_date: '', term: '', remark: ''
})

const batchForm = reactive({
  student_id: null,
  exam_type: 2,
  term: '',
  scores: []
})

const rules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  subject_id: [{ required: true, message: '请选择科目', trigger: 'change' }],
  score_value: [{ required: true, message: '请输入成绩', trigger: 'blur' }]
}

const examTypeText = (t) => examTypes.value.find(x => x.value === t)?.label || '未知'
const scoreClass = (s) => {
  if (s >= 90) return 'score-a'
  if (s >= 80) return 'score-b'
  if (s >= 60) return 'score-c'
  return 'score-f'
}
const gradeTagType = (g) => ({ A: 'success', B: '', C: 'warning', D: 'danger', F: 'danger' }[g] || '')

const loadData = async () => {
  loading.value = true
  try {
    const res = await getScores({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchParams.keyword || undefined,
      exam_type: searchParams.exam_type,
      term: searchParams.term || undefined
    })
    if (res.code === 200) {
      tableData.value = res.data.list
      pagination.total = res.data.total
    }
  } catch (e) {} finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchParams.keyword = ''
  searchParams.exam_type = null
  searchParams.term = ''
  pagination.page = 1
  loadData()
}

const resetForm = () => {
  Object.assign(form, {
    student_id: null, subject_id: null, score_value: 0,
    exam_type: 1, exam_date: '', term: '', remark: ''
  })
  formRef.value?.clearValidate()
}

const openDialog = (row = null) => {
  resetForm()
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.assign(form, {
      student_id: row.student_id, subject_id: row.subject_id,
      score_value: row.score_value, exam_type: row.exam_type,
      exam_date: row.exam_date, term: row.term || '', remark: row.remark || ''
    })
  } else {
    isEdit.value = false
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updateScore(editId.value, form)
    } else {
      res = await createScore(form)
    }
    if (res.code === 200) {
      ElMessage.success(res.msg)
      dialogVisible.value = false
      loadData()
    }
  } catch (e) {} finally { submitting.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除这条成绩记录吗？', '提示', { type: 'warning' })
    const res = await deleteScore(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (e) {}
}

const openBatchDialog = () => {
  batchForm.student_id = null
  batchForm.scores = []
  batchForm.exam_type = 2
  batchForm.term = ''
  addBatchItem()
  batchDialogVisible.value = true
}

const addBatchItem = () => {
  batchForm.scores.push({ subject_id: null, score_value: 0 })
}

const removeBatchItem = (index) => {
  batchForm.scores.splice(index, 1)
}

const onBatchStudentChange = () => {}

const handleBatchSubmit = async () => {
  if (!batchForm.student_id) {
    ElMessage.warning('请选择学员')
    return
  }
  if (!batchForm.scores.length) {
    ElMessage.warning('请添加至少一个科目')
    return
  }
  for (const item of batchForm.scores) {
    if (!item.subject_id) {
      ElMessage.warning('请选择科目')
      return
    }
  }

  submitting.value = true
  try {
    const res = await batchCreateScores({
      student_id: batchForm.student_id,
      scores: batchForm.scores.map(s => ({
        subject_id: s.subject_id,
        score_value: s.score_value,
        exam_type: batchForm.exam_type,
        term: batchForm.term,
        exam_date: new Date().toISOString().split('T')[0]
      }))
    })
    if (res.code === 200) {
      ElMessage.success(res.msg)
      batchDialogVisible.value = false
      loadData()
    }
  } catch (e) {} finally { submitting.value = false }
}

const loadInitData = async () => {
  try {
    const [subRes, stuRes, typeRes] = await Promise.all([
      getAllSubjects(),
      getStudents({ page: 1, page_size: 100 }),
      getExamTypes()
    ])
    if (subRes.code === 200) subjects.value = subRes.data
    if (stuRes.code === 200) students.value = stuRes.data.list
    if (typeRes.code === 200) examTypes.value = typeRes.data
  } catch (e) {}
}

onMounted(() => {
  loadData()
  loadInitData()
})
</script>

<style lang="scss" scoped>
.scores-page { max-width: 1400px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  .page-title { font-size: 24px; font-weight: 600; color: #1e293b; margin: 0; }
  div { display: flex; gap: 12px; }
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.score-a { color: #10b981; font-weight: 600; }
.score-b { color: #3b82f6; font-weight: 600; }
.score-c { color: #f59e0b; }
.score-f { color: #ef4444; font-weight: 600; }

.batch-table {
  .batch-header, .batch-row {
    display: grid;
    grid-template-columns: 2fr 1fr auto;
    gap: 12px;
    align-items: center;
    margin-bottom: 12px;
  }
  .batch-header {
    font-weight: 600;
    color: #64748b;
    font-size: 13px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
  }
  .batch-empty {
    text-align: center;
    color: #94a3b8;
    padding: 20px;
    font-size: 13px;
  }
}
</style>