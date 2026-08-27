<template>
  <div class="students-page">
    <div class="page-header">
      <h1 class="page-title">学员管理</h1>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>新增学员
      </el-button>
    </div>

    <div class="card">
      <div class="search-bar">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索学号或姓名"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
          @keyup.enter="loadData"
        />
        <el-select v-model="searchParams.status" placeholder="状态" clearable style="width: 120px">
          <el-option label="在读" :value="1" />
          <el-option label="休学" :value="2" />
          <el-option label="毕业" :value="3" />
          <el-option label="退学" :value="4" />
        </el-select>
        <el-select v-model="searchParams.class_name" placeholder="班级" clearable style="width: 180px">
          <el-option v-for="cls in classNames" :key="cls" :label="cls" :value="cls" />
        </el-select>
        <el-button type="primary" @click="loadData">
          <el-icon><Search /></el-icon>搜索
        </el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            {{ row.gender === 1 ? '男' : row.gender === 2 ? '女' : '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" width="160" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="light">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enrollment_date" label="入学日期" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
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
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学员' : '新增学员'" width="600px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学号" prop="student_no">
              <el-input v-model="form.student_no" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="form.gender" style="width: 100%">
                <el-option label="男" :value="1" />
                <el-option label="女" :value="2" />
                <el-option label="未知" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker v-model="form.birth_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="form.id_card" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班级">
              <el-input v-model="form.class_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入学日期" prop="enrollment_date">
              <el-date-picker v-model="form.enrollment_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="在读" :value="1" />
                <el-option label="休学" :value="2" />
                <el-option label="毕业" :value="3" />
                <el-option label="退学" :value="4" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="地址">
              <el-input v-model="form.address" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { getStudents, createStudent, updateStudent, deleteStudent, getClassNames } from '../api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const editId = ref(null)
const classNames = ref([])

const searchParams = reactive({
  keyword: '',
  status: null,
  class_name: null
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const form = reactive({
  student_no: '',
  name: '',
  gender: 1,
  birth_date: '',
  phone: '',
  email: '',
  id_card: '',
  address: '',
  enrollment_date: '',
  class_name: '',
  status: 1
})

const rules = {
  student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  enrollment_date: [{ required: true, message: '请选择入学日期', trigger: 'change' }]
}

const statusText = (s) => ({ 1: '在读', 2: '休学', 3: '毕业', 4: '退学' }[s] || '未知')
const statusTagType = (s) => ({ 1: 'success', 2: 'warning', 3: 'info', 4: 'danger' }[s] || '')

const loadData = async () => {
  loading.value = true
  try {
    const res = await getStudents({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchParams.keyword || undefined,
      status: searchParams.status,
      class_name: searchParams.class_name || undefined
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
  searchParams.status = null
  searchParams.class_name = null
  pagination.page = 1
  loadData()
}

const resetForm = () => {
  Object.assign(form, {
    student_no: '', name: '', gender: 1, birth_date: '',
    phone: '', email: '', id_card: '', address: '',
    enrollment_date: '', class_name: '', status: 1
  })
  formRef.value?.clearValidate()
}

const openDialog = (row = null) => {
  resetForm()
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.assign(form, {
      student_no: row.student_no,
      name: row.name,
      gender: row.gender,
      birth_date: row.birth_date,
      phone: row.phone,
      email: row.email,
      id_card: row.id_card,
      address: row.address,
      enrollment_date: row.enrollment_date,
      class_name: row.class_name,
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
  } catch {
    return
  }

  submitting.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updateStudent(editId.value, form)
    } else {
      res = await createStudent(form)
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

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除学员"${row.name}"吗？`, '提示', {
      type: 'warning'
    })
    const res = await deleteStudent(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (e) {}
}

const loadClassNames = async () => {
  try {
    const res = await getClassNames()
    if (res.code === 200) {
      classNames.value = res.data
    }
  } catch (e) {}
}

onMounted(() => {
  loadData()
  loadClassNames()
})
</script>

<style lang="scss" scoped>
.students-page {
  max-width: 1400px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
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