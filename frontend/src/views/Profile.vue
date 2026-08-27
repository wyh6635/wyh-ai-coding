<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">个人信息</h1>
    </div>

    <div class="profile-layout">
      <div class="profile-card">
        <div class="avatar-section">
          <el-avatar :size="80" class="profile-avatar">
            {{ profileForm.real_name?.[0] || profileForm.username?.[0] || 'U' }}
          </el-avatar>
          <h2 class="user-name">{{ profileForm.real_name || profileForm.username }}</h2>
          <el-tag :type="profileForm.role === 'admin' ? 'primary' : 'success'" effect="dark">
            {{ profileForm.role === 'admin' ? '管理员' : '学员' }}
          </el-tag>
          <p class="user-id">ID: {{ profileForm.id }}</p>
          <p class="register-time" v-if="profileForm.created_at">注册于 {{ profileForm.created_at }}</p>
        </div>
      </div>

      <div class="profile-edit-card">
        <div class="card-header">
          <h3>基本信息</h3>
        </div>
        <el-form
          ref="formRef"
          :model="profileForm"
          :rules="rules"
          label-width="100px"
          class="profile-form"
        >
          <el-form-item label="用户名">
            <el-input v-model="profileForm.username" disabled />
            <div class="form-tip">用户名不可修改</div>
          </el-form-item>
          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="profileForm.real_name" placeholder="请输入真实姓名" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱地址" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="profileForm.phone" placeholder="请输入11位手机号" maxlength="11" />
          </el-form-item>
          <el-form-item label="角色">
            <el-input v-model="roleText" disabled />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="submitting" @click="handleSave">保存修改</el-button>
            <el-button @click="loadProfile">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div class="tips-card">
      <div class="tips-header">
        <el-icon :size="18"><InfoFilled /></el-icon>
        <span>温馨提示</span>
      </div>
      <ul>
        <li>用户名创建后不可修改</li>
        <li>邮箱和手机号建议填写，便于找回密码</li>
        <li>如需修改密码，请点击右上角用户头像 -> 修改密码</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { getProfile, updateProfile } from '../api'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const formRef = ref(null)
const submitting = ref(false)

const profileForm = reactive({
  id: null,
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role: '',
  created_at: ''
})

const roleText = computed(() => profileForm.role === 'admin' ? '管理员' : '学员')

const rules = {
  real_name: [
    { max: 50, message: '姓名长度不能超过50个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: ['blur', 'change'] }
  ]
}

const loadProfile = async () => {
  try {
    const res = await getProfile()
    if (res.code === 200) {
      Object.assign(profileForm, res.data)
    }
  } catch (e) {}
}

const handleSave = async () => {
  try { await formRef.value.validate() } catch { return }

  submitting.value = true
  try {
    const res = await updateProfile({
      real_name: profileForm.real_name,
      email: profileForm.email,
      phone: profileForm.phone
    })
    if (res.code === 200) {
      ElMessage.success('保存成功')
      if (res.data) {
        Object.assign(profileForm, res.data)
        userStore.setUserInfo(res.data)
      }
    }
  } catch (e) {} finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style lang="scss" scoped>
.profile-page {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 24px;
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

.profile-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

.profile-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  height: fit-content;
}

.avatar-section {
  text-align: center;

  .profile-avatar {
    background: linear-gradient(135deg, #3b82f6, #60a5fa);
    color: #fff;
    font-weight: 600;
    font-size: 28px;
    margin-bottom: 16px;
  }

  .user-name {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 8px;
  }

  .user-id {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 12px;
  }

  .register-time {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 4px;
  }
}

.profile-edit-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

.profile-form {
  max-width: 500px;
}

.form-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.tips-card {
  margin-top: 24px;
  padding: 16px 20px;
  background: #f0f9ff;
  border-radius: 12px;
  border-left: 4px solid #3b82f6;

  .tips-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #1e40af;
    margin-bottom: 8px;
  }

  ul {
    padding-left: 20px;
    margin: 0;
    li {
      font-size: 13px;
      color: #475569;
      line-height: 1.8;
    }
  }
}
</style>