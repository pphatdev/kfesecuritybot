<template>
  <div class="dashboard-overview">
    <!-- Quick Stats Grid -->
    <div class="stats-grid">
      <!-- Total Messages -->
      <div class="stat-card card-scanned">
        <div class="stat-header">
          <div class="stat-icon message-icon">
            <IconMail class="icon" />
          </div>
          <span class="trend-badge">Active Scan</span>
        </div>
        <div class="stat-info">
          <h3>Total Messages Scanned</h3>
          <p class="stat-value">{{ stats?.total_messages_scanned || 0 }}</p>
        </div>
        <div class="card-progress">
          <div class="progress-bar progress-scanned" style="width: 100%;"></div>
        </div>
      </div>
      
      <!-- Harmonized Blocked Count -->
      <div class="stat-card card-blocked">
        <div class="stat-header">
          <div class="stat-icon block-icon">
            <IconShield class="icon" />
          </div>
          <span class="trend-badge alarm">AI Moderated</span>
        </div>
        <div class="stat-info">
          <h3>Harmful Content Blocked</h3>
          <p class="stat-value">{{ stats?.spam_toxic_blocked || 0 }}</p>
        </div>
        <div class="card-progress">
          <div class="progress-bar progress-blocked" :style="{ width: getBlockedRatio + '%' }"></div>
        </div>
      </div>
      
      <!-- Repeat Offenders -->
      <div class="stat-card card-offenders">
        <div class="stat-header">
          <div class="stat-icon user-icon">
            <IconAlertTriangle class="icon" />
          </div>
          <span class="trend-badge warning">Watchlist</span>
        </div>
        <div class="stat-info">
          <h3>Repeat Offenders</h3>
          <p class="stat-value">{{ Object.keys(stats?.violations || {}).length }}</p>
        </div>
        <div class="card-progress">
          <div class="progress-bar progress-offenders" style="width: 40%;"></div>
        </div>
      </div>
    </div>
    
    <!-- Recent Bot Activity -->
    <div class="recent-activity">
      <div class="activity-header">
        <div class="title-wrap">
          <h2>Recent Activity</h2>
          <p class="subtitle">Live log of message moderation strikes</p>
        </div>
        <span class="status-indicator" :class="{ scanning: !pending }">
          <span class="dot"></span>
          {{ pending ? 'Loading...' : 'Live Monitoring' }}
        </span>
      </div>
      
      <div class="activity-container">
        <div v-if="!stats?.recent_activity?.length" class="empty-state">
          <IconMessage class="icon empty-icon" />
          <p>No activity yet. Waiting for chat messages...</p>
        </div>
        
        <TransitionGroup name="list" tag="ul" class="activity-list" v-else>
          <li class="activity-item" v-for="(activity, idx) in stats.recent_activity" :key="idx">
            <div class="activity-time-wrap">
              <span class="activity-time">{{ activity.time }}</span>
            </div>
            
            <div class="activity-badge-wrap">
              <span :class="['activity-badge', activity.type]">{{ activity.type }}</span>
            </div>
            
            <div class="activity-content">
              <span class="activity-text" v-html="activity.text"></span>
            </div>
          </li>
        </TransitionGroup>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { IconMail, IconShield, IconAlertTriangle, IconMessage } from '@tabler/icons-vue'

const { data: stats, pending, refresh } = useFetch('/api/stats')

let pollInterval

onMounted(() => {
  // Poll every 3 seconds for real-time updates
  pollInterval = setInterval(() => {
    refresh()
  }, 3000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

const getBlockedRatio = computed(() => {
  const scanned = stats.value?.total_messages_scanned || 0
  const blocked = stats.value?.spam_toxic_blocked || 0
  if (scanned === 0) return 0
  return Math.min(100, Math.round((blocked / scanned) * 100))
})
</script>

<style scoped>
.dashboard-overview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 160px;
  background-color: var(--color-bg-surface) !important;
  backdrop-filter: var(--glass-backdrop);
  -webkit-backdrop-filter: var(--glass-backdrop);
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: var(--transition-smooth);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
  border-color: rgba(255, 255, 255, 0.15) !important;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  background-color: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.5);
}

.message-icon {
  color: var(--color-primary) !important;
}

.block-icon {
  color: var(--color-secondary) !important;
}

.user-icon {
  color: var(--color-accent) !important;
}

.trend-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  background-color: rgba(34, 197, 94, 0.15);
  color: #4ADE80;
}

.trend-badge.alarm {
  background-color: rgba(239, 68, 68, 0.15);
  color: #FCA5A5;
}

.trend-badge.warning {
  background-color: rgba(234, 179, 8, 0.15);
  color: #FDE047;
}

.stat-info h3 {
  margin: 0 0 6px 0;
  font-size: 0.85rem;
  color: var(--color-text-light);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  margin: 0;
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--color-primary);
  line-height: 1.1;
}

.card-progress {
  height: 6px;
  background-color: rgba(255, 255, 255, 0.1) !important;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 20px;
}

.progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease-in-out;
}

.progress-scanned {
  background-color: var(--color-primary) !important;
}

.progress-blocked {
  background-color: var(--color-secondary) !important;
}

.progress-offenders {
  background-color: var(--color-accent) !important;
}

.recent-activity {
  padding: 24px;
  background-color: var(--color-bg-surface) !important;
  backdrop-filter: var(--glass-backdrop);
  -webkit-backdrop-filter: var(--glass-backdrop);
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.activity-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.subtitle {
  margin: 4px 0 0 0;
  color: var(--color-text-light);
  font-size: 0.85rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-white);
  background: rgba(0, 0, 0, 0.3);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.status-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-text-light);
}

.status-indicator.scanning .dot {
  background-color: var(--color-secondary-light);
  box-shadow: 0 0 8px var(--color-secondary-light);
  animation: pulse 1.5s infinite alternate;
}

@keyframes pulse {
  from { opacity: 0.4; }
  to { opacity: 1; }
}

.activity-container {
  max-height: 480px;
  overflow-y: auto;
  padding-right: 8px;
}

.empty-state {
  text-align: center;
  padding: 64px 32px;
  color: var(--color-text-light);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  color: var(--color-disabled-text) !important;
}

.activity-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  background-color: rgba(0, 0, 0, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.05) !important;
  transition: var(--transition-smooth);
}

.activity-item:hover {
  transform: translateY(-2px);
  background-color: rgba(255, 255, 255, 0.03) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.activity-time-wrap {
  width: 90px;
  flex-shrink: 0;
}

.activity-time {
  font-size: 0.85rem;
  color: var(--color-text-light);
  font-weight: 500;
}

.activity-badge-wrap {
  width: 80px;
  flex-shrink: 0;
}

.activity-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  display: inline-block;
  text-align: center;
  width: 100%;
}

.activity-badge.toxic {
  background-color: rgba(239, 68, 68, 0.15);
  color: #FCA5A5;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.activity-badge.spam {
  background-color: rgba(249, 115, 22, 0.15);
  color: #FDBA74;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.activity-badge.action {
  background-color: rgba(34, 197, 94, 0.15);
  color: #86EFAC;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.activity-content {
  flex: 1;
  font-size: 0.95rem;
  color: var(--color-text-body);
}

/* Animations */
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-15px);
}
</style>
