<template>
  <div class="login-page">
    <div class="login-left">
      <div class="brand-section">
        <div class="brand-logo">
          <el-icon :size="48" color="#3b82f6"><Reading /></el-icon>
        </div>
        <h1 class="brand-title">学员管理系统</h1>
        <p class="brand-subtitle">School Management System</p>

        <div class="brand-features">
          <div class="feature-item">
            <div class="feature-icon feature-blue">
              <el-icon :size="20"><DataAnalysis /></el-icon>
            </div>
            <div class="feature-text">
              <h4>数据看板</h4>
              <p>实时数据统计与分析</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon feature-green">
              <el-icon :size="20"><User /></el-icon>
            </div>
            <div class="feature-text">
              <h4>学员管理</h4>
              <p>完整的学员信息管理</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon feature-orange">
              <el-icon :size="20"><Histogram /></el-icon>
            </div>
            <div class="feature-text">
              <h4>成绩分析</h4>
              <p>多维度成绩统计查询</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="login-form-wrapper">
        <div class="form-header">
          <h2>欢迎登录</h2>
          <p>请输入您的账号信息</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              clearable
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>

          <el-form-item prop="captcha">
            <div class="captcha-wrapper">
              <el-input
                v-model="form.captcha"
                placeholder="请输入验证码"
                size="large"
                :prefix-icon="Key"
                class="captcha-input"
                maxlength="4"
              />
              <div class="captcha-img" @click="refreshCaptcha">
                <img v-if="captchaImg" :src="captchaImg" alt="验证码" />
                <div v-else class="captcha-loading">加载中...</div>
              </div>
            </div>
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            <span>登 录</span>
          </el-button>

          <div class="login-tips">
            <span>测试账号：admin / student001</span>
            <span class="tips-divider">|</span>
            <span>密码：123456</span>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Key, Reading, DataAnalysis, Histogram } from '@element-plus/icons-vue'
import { login as loginApi, getCaptcha } from '../api/auth'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const captchaImg = ref('')
const captchaKey = ref('')

const form = reactive({
  username: '',
  password: '',
  captcha: '',
  captcha_key: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ]
}

const refreshCaptcha = async () => {
  try {
    const res = await getCaptcha()
    if (res.code === 200) {
      captchaImg.value = res.data.captcha_img
      captchaKey.value = res.data.captcha_key
      form.captcha_key = res.data.captcha_key
    }
  } catch (e) {
    console.error('获取验证码失败', e)
  }
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const res = await loginApi({
        username: form.username,
        password: form.password,
        captcha: form.captcha,
        captcha_key: captchaKey.value
      })

      if (res.code === 200) {
        userStore.setToken(res.data.token)
        userStore.setUserInfo(res.data.user)
        ElMessage.success('登录成功，欢迎回来！')
        router.push('/')
      }
    } catch (e) {
      refreshCaptcha()
      form.captcha = ''
    } finally {
      loading.value = false
    }
  })
}

onMounted(() => {
  refreshCaptcha()
})
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  background: #fff;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 50%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  top: -200px;
  right: -200px;
}

.login-left::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  bottom: -100px;
  left: -100px;
}

.brand-section {
  position: relative;
  z-index: 1;
  color: #fff;
  max-width: 420px;
}

.brand-logo {
  width: 72px;
  height: 72px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28px;
  backdrop-filter: blur(10px);
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.brand-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 48px;
  letter-spacing: 2px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.feature-blue {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.feature-green {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.feature-orange {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.feature-text {
  h4 {
    font-size: 15px;
    font-weight: 600;
    margin: 0 0 2px;
    color: #fff;
  }

  p {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.75);
    margin: 0;
  }
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background: #f8fafc;
}

.login-form-wrapper {
  width: 100%;
  max-width: 420px;
}

.form-header {
  margin-bottom: 40px;

  h2 {
    font-size: 28px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px;
  }

  p {
    font-size: 15px;
    color: #64748b;
    margin: 0;
  }
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;
  }

  :deep(.el-input__wrapper) {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    box-shadow: none;
    padding: 4px 16px;
    transition: all 0.3s ease;
  }

  :deep(.el-input__wrapper:hover) {
    border-color: #3b82f6;
  }

  :deep(.el-input__wrapper.is-focus) {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  :deep(.el-input__inner) {
    color: #1e293b;
    font-size: 15px;

    &::placeholder {
      color: #94a3b8;
    }
  }

  :deep(.el-input__prefix-inner) {
    color: #64748b;
  }
}

.captcha-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
}

.captcha-input {
  flex: 1;
}

.captcha-img {
  width: 120px;
  height: 40px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  flex-shrink: 0;

  &:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .captcha-loading {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f1f5f9;
    color: #94a3b8;
    font-size: 12px;
  }
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  margin-top: 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  border: none;
  color: #fff;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
}

.login-tips {
  margin-top: 24px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;

  .tips-divider {
    margin: 0 12px;
    color: #cbd5e1;
  }
}

@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }

  .login-left {
    padding: 40px 32px;
  }

  .brand-features {
    display: none;
  }

  .login-right {
    padding: 40px 24px;
  }
}
</style>