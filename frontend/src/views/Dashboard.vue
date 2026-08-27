<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">数据看板</h1>
      <p class="page-desc">系统数据概览</p>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="stat-card stat-blue">
          <div class="stat-icon">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.student_total || 0 }}</div>
            <div class="stat-label">学员总数（在读 {{ stats.student_active || 0 }} 人）</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="stat-card stat-green">
          <div class="stat-icon">
            <el-icon :size="28"><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.subject_all || 0 }}</div>
            <div class="stat-label">科目总数（启用 {{ stats.subject_total || 0 }} 个）</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="stat-card stat-orange">
          <div class="stat-icon">
            <el-icon :size="28"><Histogram /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.score_total || 0 }}</div>
            <div class="stat-label">成绩记录总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <div class="stat-card stat-purple">
          <div class="stat-icon">
            <el-icon :size="28"><Calendar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.exam_count || 0 }}</div>
            <div class="stat-label">考试批次数</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :lg="16">
        <div class="card">
          <div class="card-header">
            <h3>各科目平均分</h3>
            <span class="card-subtitle">仅统计启用状态科目</span>
          </div>
          <div class="chart-content">
            <div v-for="item in subjectScores" :key="item.id" class="chart-bar-item">
              <div class="bar-label">
                <span class="subject-name">{{ item.subject_name }}</span>
                <span class="score-value">
                  {{ item.avg_score?.toFixed(1) || '0.0' }} 分
                  <span class="score-count">· {{ item.score_count || 0 }} 条</span>
                </span>
              </div>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{ width: getBarWidth(item.avg_score) }"
                ></div>
              </div>
            </div>
            <el-empty v-if="!subjectScores.length" description="暂无数据" />
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :lg="8">
        <div class="card quick-actions">
          <div class="card-header">
            <h3>快捷操作</h3>
          </div>
          <div class="action-list">
            <div class="action-item" @click="$router.push('/students')">
              <el-icon :size="20" color="#3b82f6"><Plus /></el-icon>
              <span>新增学员</span>
            </div>
            <div class="action-item" @click="$router.push('/subjects')">
              <el-icon :size="20" color="#10b981"><Reading /></el-icon>
              <span>新增科目</span>
            </div>
            <div class="action-item" @click="$router.push('/scores')">
              <el-icon :size="20" color="#f59e0b"><Edit /></el-icon>
              <span>录入成绩</span>
            </div>
            <div class="action-item" @click="$router.push('/query')">
              <el-icon :size="20" color="#8b5cf6"><Search /></el-icon>
              <span>数据查询</span>
            </div>
          </div>

          <div class="tips-section">
            <h4>操作提醒</h4>
            <ul>
              <li>停用科目不参与成绩录入，前台也不显示</li>
              <li>同一学员同一科目同一次仅可录入一条成绩</li>
              <li>已有成绩的学员/科目禁止删除，请改用作废或停用</li>
            </ul>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, Reading, Histogram, Calendar, Plus, Search } from '@element-plus/icons-vue'
import { getDashboardStats, getSubjectScores } from '../api'

const stats = ref({})
const subjectScores = ref([])

const getBarWidth = (score) => {
  const s = score || 0
  return `${Math.min(s, 100)}%`
}

const loadData = async () => {
  try {
    const [statsRes, scoresRes] = await Promise.all([
      getDashboardStats(),
      getSubjectScores()
    ])
    if (statsRes.code === 200) {
      stats.value = statsRes.data
    }
    if (scoresRes.code === 200) {
      subjectScores.value = scoresRes.data
    }
  } catch (e) {
    console.error('加载数据失败', e)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  max-width: 1400px;
}

.page-header {
  margin-bottom: 24px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 4px;
  }

  .page-desc {
    font-size: 14px;
    color: #64748b;
    margin: 0;
  }
}

.stats-row {
  margin-bottom: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #fff;
  flex-shrink: 0;
}

.stat-blue .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.stat-green .stat-icon {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.stat-orange .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.stat-purple .stat-icon {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.content-row {
  margin-top: 24px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 24px;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

.card-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.chart-content {
  min-height: 300px;
}

.chart-bar-item {
  margin-bottom: 20px;

  &:last-child {
    margin-bottom: 0;
  }
}

.bar-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;

  .subject-name {
    font-size: 14px;
    font-weight: 500;
    color: #334155;
  }

  .score-value {
    font-size: 13px;
    color: #64748b;

    .score-count {
      color: #94a3b8;
    }
  }
}

.bar-track {
  height: 20px;
  background: #f1f5f9;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 10px;
  transition: width 0.8s ease;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.action-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
  color: #334155;

  &:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
}

.tips-section {
  background: #fef3c7;
  border-radius: 8px;
  padding: 16px;

  h4 {
    font-size: 13px;
    font-weight: 600;
    color: #92400e;
    margin: 0 0 12px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  ul {
    padding-left: 18px;
    margin: 0;

    li {
      font-size: 12px;
      color: #78350f;
      line-height: 1.8;
    }
  }
}

@media (max-width: 768px) {
  .stat-card {
    padding: 16px;
    gap: 12px;
  }

  .stat-icon {
    width: 44px;
    height: 44px;
  }

  .stat-value {
    font-size: 24px;
  }

  .action-list {
    grid-template-columns: 1fr;
  }
}
</style>