<template>
  <div class="home-page" ref="containerRef">
    <nav class="navbar" :class="{ scrolled: isScrolled }">
      <div class="nav-content">
        <div class="nav-logo">
          <span class="logo-icon">🎓</span>
          <span class="logo-text neon-text">SchoolManager</span>
        </div>
        <div class="nav-links">
          <a href="#hero" class="nav-link" @click.prevent="scrollTo('hero')">首页</a>
          <a href="#skills" class="nav-link" @click.prevent="scrollTo('skills')">技能</a>
          <a href="#works" class="nav-link" @click.prevent="scrollTo('works')">作品</a>
          <a href="#contact" class="nav-link" @click.prevent="scrollTo('contact')">联系</a>
        </div>
        <div class="nav-user">
          <div class="user-info">
            <el-avatar :size="36" :style="{ background: userAvatar }">
              {{ userStore.userInfo?.real_name?.[0] || userStore.userInfo?.username?.[0] || 'U' }}
            </el-avatar>
            <div class="user-detail">
              <span class="user-name">{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</span>
              <span class="user-role">{{ roleText }}</span>
            </div>
          </div>
          <el-dropdown @command="handleCommand">
            <el-button class="user-menu-btn" :icon="Setting" circle />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <span style="color: #FF00E5">退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button class="logout-btn" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出</span>
          </el-button>
        </div>
      </div>
    </nav>

    <section id="hero" class="hero-section">
      <div class="hero-particles">
        <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></div>
      </div>
      <div class="hero-content">
        <div class="hero-badge fade-in-up">
          <span class="pulse-dot"></span>
          <span>Welcome Back</span>
        </div>
        <h1 class="hero-name fade-in-up" :style="{ animationDelay: '0.1s' }">
          <span class="neon-text">{{ userStore.userInfo?.real_name || '用户' }}</span>
        </h1>
        <h2 class="hero-title fade-in-up" :style="{ animationDelay: '0.3s' }">
          <span>{{ dynamicText }}</span><span class="cursor">|</span>
        </h2>
        <p class="hero-desc fade-in-up" :style="{ animationDelay: '0.5s' }">
          欢迎回到校园信息管理系统，让我们一起开启今天的学习之旅
        </p>
        <div class="hero-actions fade-in-up" :style="{ animationDelay: '0.7s' }">
          <button class="btn-neon" @click="scrollTo('skills')">
            <span>探索功能</span>
            <el-icon class="btn-icon"><ArrowRight /></el-icon>
          </button>
          <button class="btn-ghost" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </button>
        </div>
      </div>
      <div class="scroll-indicator">
        <span>向下滚动</span>
        <div class="scroll-arrow"></div>
      </div>
    </section>

    <section id="user-info" class="user-section">
      <div class="container">
        <h2 class="section-title fade-in-view">个人信息</h2>
        <div class="user-info-card fade-in-view">
          <div class="user-avatar-large">
            <el-avatar :size="100" :style="{ background: userAvatar }">
              <span style="font-size: 36px; font-weight: 600">{{ (userStore.userInfo?.real_name || userStore.userInfo?.username)?.[0] }}</span>
            </el-avatar>
          </div>
          <div class="user-details">
            <div class="detail-item">
              <span class="label">用户名</span>
              <span class="value">{{ userStore.userInfo?.username }}</span>
            </div>
            <div class="detail-item">
              <span class="label">姓名</span>
              <span class="value">{{ userStore.userInfo?.real_name || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">邮箱</span>
              <span class="value">{{ userStore.userInfo?.email || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">手机号</span>
              <span class="value">{{ userStore.userInfo?.phone || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">角色</span>
              <span class="value role-tag">{{ roleText }}</span>
            </div>
            <div class="detail-item">
              <span class="label">状态</span>
              <span class="value">
                <el-tag :type="userStore.userInfo?.status === 1 ? 'success' : 'danger'" effect="dark" round>
                  {{ userStore.userInfo?.status === 1 ? '正常' : '禁用' }}
                </el-tag>
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="skills" class="skills-section">
      <div class="container">
        <h2 class="section-title fade-in-view">核心功能</h2>
        <p class="section-subtitle fade-in-view">系统提供的六大核心功能模块</p>
        <div class="skills-grid">
          <div v-for="(skill, index) in skills" :key="skill.title" 
               class="skill-card fade-in-view" 
               :style="{ animationDelay: `${index * 0.1}s` }">
            <div class="skill-front">
              <div class="skill-icon" :style="{ background: skill.color }">
                <el-icon :size="32"><component :is="skill.icon" /></el-icon>
              </div>
              <h3>{{ skill.title }}</h3>
              <p>{{ skill.desc }}</p>
            </div>
            <div class="skill-back">
              <h3>{{ skill.title }}</h3>
              <ul>
                <li v-for="detail in skill.details" :key="detail">{{ detail }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="works" class="works-section">
      <div class="container">
        <h2 class="section-title fade-in-view">数据管理</h2>
        <p class="section-subtitle fade-in-view">高效管理学员、成绩、科目数据</p>
        <div class="works-grid">
          <div v-for="(work, index) in works" :key="work.title" 
               class="work-card fade-in-view"
               :style="{ animationDelay: `${index * 0.15}s` }"
               @click="handleWorkClick(work)">
            <div class="work-cover" :style="{ background: work.bg }">
              <el-icon :size="48"><component :is="work.icon" /></el-icon>
            </div>
            <div class="work-info">
              <h3>{{ work.title }}</h3>
              <p>{{ work.desc }}</p>
              <span class="work-tag">查看详情</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="contact" class="contact-section">
      <div class="container">
        <h2 class="section-title fade-in-view">联系支持</h2>
        <p class="section-subtitle fade-in-view">有任何问题？随时联系我们</p>
        <div class="contact-content fade-in-view">
          <div class="contact-info">
            <div class="info-item">
              <el-icon :size="24"><Message /></el-icon>
              <div>
                <h4>邮箱支持</h4>
                <p>support@school.edu.cn</p>
              </div>
            </div>
            <div class="info-item">
              <el-icon :size="24"><Phone /></el-icon>
              <div>
                <h4>电话支持</h4>
                <p>400-888-0000</p>
              </div>
            </div>
            <div class="info-item">
              <el-icon :size="24"><LocationInformation /></el-icon>
              <div>
                <h4>办公地址</h4>
                <p>北京市海淀区学院路1号</p>
              </div>
            </div>
            <div class="social-icons">
              <a v-for="social in socials" :key="social.name" href="#" class="social-icon" :title="social.name">
                <el-icon :size="20"><component :is="social.icon" /></el-icon>
              </a>
            </div>
          </div>
          <div class="contact-form">
            <el-form :model="contactForm" class="form">
              <el-form-item>
                <el-input v-model="contactForm.name" placeholder="您的姓名" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="contactForm.email" placeholder="电子邮箱" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="contactForm.message" type="textarea" :rows="4" placeholder="留言内容" size="large" />
              </el-form-item>
              <el-button type="primary" size="large" class="submit-btn" @click="handleSubmit">
                发送消息
              </el-button>
            </el-form>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer">
      <p>© 2024 校园信息管理系统. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, Bell, DataAnalysis, Notebook, Histogram,
  Setting, ArrowRight, SwitchButton, Message, Phone, LocationInformation,
  Share, ChatDotRound, Link, Monitor
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const isScrolled = ref(false)
const containerRef = ref(null)

const roleText = computed(() => {
  return userStore.userInfo?.role === 'admin' ? '管理员' : '学员'
})

const userAvatar = computed(() => {
  return userStore.userInfo?.role === 'admin'
    ? 'linear-gradient(135deg, #00F5FF, #0066FF)'
    : 'linear-gradient(135deg, #FF00E5, #7B2CBF)'
})

const dynamicText = ref('')
const textList = [
  '全栈开发者',
  '数据管理者',
  '系统维护者',
  '技术创新者'
]
let textIndex = 0
let charIndex = 0
let isDeleting = false

const typeText = () => {
  const currentText = textList[textIndex]
  if (isDeleting) {
    dynamicText.value = currentText.substring(0, charIndex - 1)
    charIndex--
  } else {
    dynamicText.value = currentText.substring(0, charIndex + 1)
    charIndex++
  }

  if (!isDeleting && charIndex === currentText.length) {
    isDeleting = true
    setTimeout(typeText, 2000)
  } else if (isDeleting && charIndex === 0) {
    isDeleting = false
    textIndex = (textIndex + 1) % textList.length
    setTimeout(typeText, 500)
  } else {
    setTimeout(typeText, isDeleting ? 50 : 100)
  }
}

const skills = [
  { title: '用户管理', desc: '系统用户与权限控制', icon: markRaw(User), color: 'linear-gradient(135deg, #00F5FF, #0066FF)', details: ['账号管理', '权限分配', '角色设置'] },
  { title: '数据统计', desc: '学员成绩数据分析', icon: markRaw(DataAnalysis), color: 'linear-gradient(135deg, #FF00E5, #FF6B6B)', details: ['成绩分析', '数据可视化', '报表导出'] },
  { title: '学籍管理', desc: '学员信息全生命周期', icon: markRaw(Notebook), color: 'linear-gradient(135deg, #7B2CBF, #9D4EDD)', details: ['入学登记', '学籍变更', '毕业管理'] },
  { title: '成绩管理', desc: '成绩录入与审核', icon: markRaw(Histogram), color: 'linear-gradient(135deg, #00F5FF, #00C9A7)', details: ['成绩录入', '等级评定', '排名统计'] },
  { title: '科目管理', desc: '课程与科目配置', icon: markRaw(Monitor), color: 'linear-gradient(135deg, #FF00E5, #FF6347)', details: ['科目设置', '学分管理', '学时配置'] },
  { title: '系统通知', desc: '消息通知与提醒', icon: markRaw(Bell), color: 'linear-gradient(135deg, #FFD700, #FF8C00)', details: ['消息推送', '系统公告', '待办提醒'] }
]

const works = [
  { title: '学员档案', desc: '管理所有学员基本信息', icon: markRaw(User), bg: 'linear-gradient(135deg, #00F5FF22, #0066FF22)' },
  { title: '成绩查询', desc: '查看学员成绩与排名', icon: markRaw(Histogram), bg: 'linear-gradient(135deg, #FF00E522, #FF6B6B22)' },
  { title: '科目设置', desc: '配置课程与学分', icon: markRaw(Notebook), bg: 'linear-gradient(135deg, #7B2CBF22, #9D4EDD22)' },
  { title: '数据报表', desc: '统计分析与报表生成', icon: markRaw(DataAnalysis), bg: 'linear-gradient(135deg, #00C9A722, #00F5FF22)' }
]

const socials = [
  { name: 'GitHub', icon: markRaw(Share) },
  { name: '微信', icon: markRaw(ChatDotRound) },
  { name: '微博', icon: markRaw(Link) }
]

const contactForm = ref({
  name: '',
  email: '',
  message: ''
})

const getParticleStyle = (i) => {
  const size = Math.random() * 4 + 2
  const left = `${Math.random() * 100}%`
  const top = `${Math.random() * 100}%`
  const delay = `${Math.random() * 5}s`
  const duration = `${Math.random() * 10 + 10}s`
  return {
    width: `${size}px`,
    height: `${size}px`,
    left,
    top,
    animationDelay: delay,
    animationDuration: duration
  }
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

const scrollTo = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (e) {
    // 用户取消
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'profile') {
    scrollTo('user-info')
  }
}

const handleWorkClick = (work) => {
  ElMessage.info(`${work.title}功能开发中...`)
}

const handleSubmit = () => {
  ElMessage.success('消息已发送，感谢您的反馈！')
  contactForm.value = { name: '', email: '', message: '' }
}

const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
}

let observer = null

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  typeText()

  nextTick(() => {
    const elements = document.querySelectorAll('.fade-in-view')
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      })
    }, observerOptions)
    elements.forEach(el => observer.observe(el))
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 16px 0;
  transition: all 0.3s ease;

  &.scrolled {
    background: rgba(10, 10, 10, 0.9);
    backdrop-filter: blur(20px);
    box-shadow: 0 2px 30px rgba(0, 245, 255, 0.1);
  }
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 8px;

  .logo-icon {
    font-size: 28px;
  }

  .logo-text {
    font-size: 20px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
  }
}

.nav-links {
  display: flex;
  gap: 32px;

  .nav-link {
    color: rgba(255, 255, 255, 0.7);
    text-decoration: none;
    font-size: 15px;
    transition: color 0.3s ease;
    cursor: pointer;

    &:hover {
      color: var(--color-primary);
    }
  }
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 16px;

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 16px 6px 6px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 50px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .user-detail {
    display: flex;
    flex-direction: column;

    .user-name {
      font-size: 14px;
      font-weight: 500;
    }

    .user-role {
      font-size: 12px;
      color: var(--color-primary);
    }
  }

  .user-menu-btn {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: rgba(255, 255, 255, 0.7) !important;
  }

  .logout-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: transparent;
    border: 1px solid var(--color-secondary);
    color: var(--color-secondary);
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      background: rgba(255, 0, 229, 0.1);
      box-shadow: 0 0 15px rgba(255, 0, 229, 0.3);
    }
  }
}

.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: radial-gradient(ellipse at top, rgba(0, 245, 255, 0.1) 0%, transparent 50%),
              radial-gradient(ellipse at bottom right, rgba(255, 0, 229, 0.1) 0%, transparent 50%),
              var(--bg-primary);
}

.hero-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.particle {
  position: absolute;
  background: var(--color-primary);
  border-radius: 50%;
  opacity: 0.3;
  animation: particle-float linear infinite;
}

@keyframes particle-float {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-100vh) rotate(720deg);
    opacity: 0;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
  padding: 0 24px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid rgba(0, 245, 255, 0.3);
  border-radius: 50px;
  color: var(--color-primary);
  font-size: 14px;
  margin-bottom: 32px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.hero-name {
  font-size: 72px;
  font-weight: 700;
  margin: 0 0 16px;
  line-height: 1.1;
}

.hero-title {
  font-size: 36px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 24px;
  min-height: 50px;

  .cursor {
    display: inline-block;
    margin-left: 4px;
    animation: blink 1s infinite;
    color: var(--color-primary);
  }
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.hero-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 40px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-icon {
  margin-left: 8px;
  transition: transform 0.3s ease;
}

.btn-neon:hover .btn-icon {
  transform: translateX(4px);
}

.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  letter-spacing: 2px;

  .scroll-arrow {
    width: 2px;
    height: 40px;
    background: linear-gradient(to bottom, var(--color-primary), transparent);
    margin: 12px auto 0;
    animation: scroll-down 2s infinite;
  }
}

@keyframes scroll-down {
  0% { transform: scaleY(0); transform-origin: top; }
  50% { transform: scaleY(1); transform-origin: top; }
  51% { transform: scaleY(1); transform-origin: bottom; }
  100% { transform: scaleY(0); transform-origin: bottom; }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.section-title {
  font-size: 42px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 16px;
}

.section-subtitle {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 16px;
  margin-bottom: 60px;
}

.user-section {
  padding: 100px 0 80px;
  background: var(--bg-secondary);
}

.user-info-card {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 60px;
  padding: 48px;
  background: var(--bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.user-avatar-large {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.user-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px 40px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .label {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .value {
    font-size: 16px;
    font-weight: 500;
    color: #fff;

    &.role-tag {
      color: var(--color-primary);
    }
  }
}

.skills-section {
  padding: 100px 0;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.skill-card {
  height: 220px;
  perspective: 1000px;
  cursor: pointer;

  .skill-front, .skill-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    transition: transform 0.6s;
    padding: 32px;
    background: var(--bg-tertiary);
    border: 1px solid var(--color-border);
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  .skill-back {
    transform: rotateY(180deg);
    background: linear-gradient(135deg, rgba(0, 245, 255, 0.1), rgba(255, 0, 229, 0.1));
    border-color: var(--color-primary);

    h3 {
      color: var(--color-primary);
      margin-bottom: 16px;
    }

    ul {
      list-style: none;
      padding: 0;

      li {
        padding: 6px 0;
        color: rgba(255, 255, 255, 0.8);
        font-size: 14px;
      }
    }
  }

  &:hover {
    .skill-front {
      transform: rotateY(-180deg);
    }

    .skill-back {
      transform: rotateY(0deg);
    }
  }

  .skill-icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    margin-bottom: 20px;
  }

  h3 {
    font-size: 20px;
    margin: 0 0 8px;
  }

  p {
    color: rgba(255, 255, 255, 0.5);
    font-size: 14px;
    margin: 0;
  }
}

.works-section {
  padding: 100px 0;
  background: var(--bg-secondary);
}

.works-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.work-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-8px);
    border-color: var(--color-primary);
    box-shadow: 0 20px 40px rgba(0, 245, 255, 0.2);

    .work-cover {
      transform: scale(1.1);
    }
  }

  .work-cover {
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-primary);
    transition: transform 0.3s ease;
  }

  .work-info {
    padding: 24px;

    h3 {
      font-size: 18px;
      margin: 0 0 8px;
    }

    p {
      color: rgba(255, 255, 255, 0.5);
      font-size: 14px;
      margin: 0 0 16px;
    }

    .work-tag {
      color: var(--color-primary);
      font-size: 13px;
    }
  }
}

.contact-section {
  padding: 100px 0;
}

.contact-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  max-width: 900px;
  margin: 0 auto;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 24px;

  .info-item {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 20px;
    background: var(--bg-tertiary);
    border: 1px solid var(--color-border);
    border-radius: 16px;

    .el-icon {
      color: var(--color-primary);
    }

    h4 {
      font-size: 16px;
      margin: 0 0 4px;
    }

    p {
      color: rgba(255, 255, 255, 0.5);
      margin: 0;
      font-size: 14px;
    }
  }

  .social-icons {
    display: flex;
    gap: 12px;
    margin-top: 16px;

    .social-icon {
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-tertiary);
      border: 1px solid var(--color-border);
      border-radius: 50%;
      color: rgba(255, 255, 255, 0.6);
      text-decoration: none;
      transition: all 0.3s ease;

      &:hover {
        color: var(--color-primary);
        border-color: var(--color-primary);
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
      }
    }
  }
}

.contact-form {
  .form {
    :deep(.el-input__wrapper) {
      background: var(--bg-tertiary);
      border: 1px solid var(--color-border);
      border-radius: 12px;
      box-shadow: none;
    }

    :deep(.el-input__inner) {
      color: #fff;

      &::placeholder {
        color: rgba(255, 255, 255, 0.4);
      }
    }
  }
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  background: var(--gradient-neon);
  border: none;
  color: var(--bg-primary);
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 245, 255, 0.4);
  }
}

.footer {
  padding: 40px 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.fade-in-view {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.6s ease, transform 0.6s ease;

  &.is-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .nav-user .user-detail {
    display: none;
  }

  .hero-name {
    font-size: 42px;
  }

  .hero-title {
    font-size: 24px;
  }

  .user-info-card {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 32px 24px;
  }

  .contact-content {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 32px;
  }
}
</style>