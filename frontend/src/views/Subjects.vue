<template>
  <div class="subjects-page">
    <div class="page-header">
      <h1 class="page-title">科目管理</h1>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>新增科目
      </el-button>
    </div>

    <div class="card">
      <div class="search-bar">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索科目编码或名称"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
          @keyup.enter="loadData"
        />
        <el-select v-model="searchParams.category" placeholder="类别" clearable style="width: 140px">
          <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
        </el-select>
        <el-select v-model="searchParams.status" placeholder="状态" clearable style="width: 120px">
          <el-option label="启用" :value="1" />
          <el-option label="停用" :value="0" />
        </el-select>
        <el-button type="primary" @click="loadData">
          <el-icon><Search /></el-icon>搜索
        </el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="subject_code" label="科目编码" width="140" />
        <el-table-column prop="subject_name" label="科目名称" width="160" />
        <el-table-column prop="category" label="类别" width="120" />
        <el-table-column prop="credit" label="学分" width="80" align="center">
          <template #default="{ row }">{{ row.credit?.toFixed(1) }}</template>
        </el-table-column>
        <el-table-column prop="total_hours" label="学时" width="80" align="center" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="light" size="small">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="warning" link @click="toggleStatus(row)">
              {{ row.status === 1 ? '停用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑科目' : '新增科目'" width="500px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="科目编码" prop="subject_code">
          <el-input v-model="form.subject_code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="科目名称" prop="subject_name">
          <el-input v-model="form.subject_name" />
        </el-form-item>
        <el-form-item label="类别">
          <el-select v-model="form.category" style="width: 100%" allow-create filterable>
            <el-option v-for="cat in defaultCategories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学分">
              <el-input-number v-model="form.credit" :min="0" :max="10" :step="0.5" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学时">
              <el-input-number v-model="form.total_hours" :min="0" :max="200" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getSubjects, createSubject, updateSubject, deleteSubject, getCategories } from '../api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)
const categories = ref([])
const defaultCategories = ['文化课', '专业课', '选修课', '公共课', '实验课']

const searchParams = reactive({ keyword: '', category: '', status: null })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref([])

const form = reactive({
  subject_code: '', subject_name: '', category: '',
  credit: 0, total_hours: 0, description: '', status: 1
})

const rules = {
  subject_code: [{ required: true, message: '请输入科目编码', trigger: 'blur' }],
  subject_name: [{ required: true, message: '请输入科目名称', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSubjects({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchParams.keyword || undefined,
      category: searchParams.category || undefined,
      status: searchParams.status
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
  searchParams.category = ''
  searchParams.status = null
  pagination.page = 1
  loadData()
}

const resetForm = () => {
  Object.assign(form, {
    subject_code: '', subject_name: '', category: '',
    credit: 0, total_hours: 0, description: '', status: 1
  })
  formRef.value?.clearValidate()
}

const openDialog = (row = null) => {
  resetForm()
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.assign(form, {
      subject_code: row.subject_code, subject_name: row.subject_name,
      category: row.category || '', credit: row.credit,
      total_hours: row.total_hours, description: row.description || '',
      status: row.status
    })
  } else {
    isEdit.value = false
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch { return }

  submitting.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updateSubject(editId.value, form)
    } else {
      res = await createSubject(form)
    }
    if (res.code === 200) {
      ElMessage.success(res.msg)
      dialogVisible.value = false
      loadData()
    }
  } catch (e) {} finally {
    submitting.value = false
  }
}

const toggleStatus = async (row) => {
  const newStatus = row.status === 1 ? 0 : 1
  try {
    const res = await updateSubject(row.id, { status: newStatus })
    if (res.code === 200) {
      ElMessage.success(newStatus === 1 ? '已启用' : '已停用')
      loadData()
    }
  } catch (e) {}
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除科目"${row.subject_name}"吗？`, '提示', { type: 'warning' })
    const res = await deleteSubject(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (e) {}
}

const loadCategories = async () => {
  try {
    const res = await getCategories()
    if (res.code === 200) categories.value = res.data
  } catch (e) {}
}

onMounted(() => {
  loadData()
  loadCategories()
})
</script>

<style lang="scss" scoped>
.subjects-page { max-width: 1400px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  .page-title { font-size: 24px; font-weight: 600; color: #1e293b; margin: 0; }
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
</style>