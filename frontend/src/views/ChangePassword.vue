<template>
  <div class="change-password-page">
    <div class="page-header">
      <h1 class="page-title">修改密码</h1>
    </div>

    <div class="card">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="password-form">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="form.old_password" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="form.new_password" type="password" show-password placeholder="请输入新密码（至少6位）" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="form.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">提交修改</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="tips">
        <h4>密码修改规则</h4>
        <ul>
          <li>密码长度至少 6 位</li>
          <li>建议使用字母、数字和符号组合</li>
          <li>密码不要与其他网站相同</li>
          <li>修改成功后需要重新登录</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changePassword } from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirm = (rule, value, callback) => {
  if (value !== form.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const resetForm = () => {
  Object.assign(form, { old_password: '', new_password: '', confirm_password: '' })
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  try { await formRef.value.validate() } catch { return }

  submitting.value = true
  try {
    const res = await changePassword({
      old_password: form.old_password,
      new_password: form.new_password
    })
    if (res.code === 200) {
      ElMessage.success('密码修改成功，请重新登录')
      setTimeout(() => {
        userStore.logout()
        router.push('/login')
      }, 1500)
    }
  } catch (e) {
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.change-password-page { max-width: 1400px; }

.page-header {
  margin-bottom: 20px;
  .page-title { font-size: 24px; font-weight: 600; color: #1e293b; margin: 0; }
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  max-width: 600px;
}

.password-form {
  max-width: 500px;
}

.tips {
  margin-top: 24px;
  padding: 16px 20px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;

  h4 {
    font-size: 14px;
    font-weight: 600;
    color: #1e40af;
    margin: 0 0 12px;
  }

  ul {
    padding-left: 18px;
    margin: 0;
    li { font-size: 13px; color: #475569; line-height: 1.8; }
  }
}
</style>