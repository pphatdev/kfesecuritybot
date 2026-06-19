<template>
  <div class="dashboard-overview">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon message-icon">📩</div>
        <div class="stat-info">
          <h3>Total Messages Scanned</h3>
          <p class="stat-value">{{ stats?.total_messages_scanned || 0 }}</p>
        </div>
      </div>
      
      <div class="stat-card highlight-card">
        <div class="stat-icon block-icon">🛡️</div>
        <div class="stat-info">
          <h3>Spam/Toxic Blocked</h3>
          <p class="stat-value">{{ stats?.spam_toxic_blocked || 0 }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon user-icon">⚠️</div>
        <div class="stat-info">
          <h3>Repeat Offenders</h3>
          <p class="stat-value">{{ Object.keys(stats?.violations || {}).length }}</p>
        </div>
      </div>
    </div>
    
    <div class="recent-activity">
      <h2>Recent Bot Activity <span v-if="pending" style="font-size: 0.8rem; font-weight: normal; color: var(--color-text-light)">(Live...)</span></h2>
      <div class="card">
        <div v-if="!stats?.recent_activity?.length" style="padding: 24px; color: var(--color-text-light);">
          No activity yet. Waiting for messages...
        </div>
        <ul class="activity-list" v-else>
          <li class="activity-item" v-for="(activity, idx) in stats.recent_activity" :key="idx">
            <span class="activity-time">{{ activity.time }}</span>
            <span :class="['activity-badge', activity.type]">{{ activity.type }}</span>
            <span class="activity-text" v-html="activity.text"></span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

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
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background-color: var(--color-bg-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.highlight-card {
  border-color: var(--color-active);
  background-color: rgba(6, 115, 2, 0.02);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  background-color: var(--color-bg-app);
}

.highlight-card .stat-icon {
  background-color: rgba(6, 115, 2, 0.1);
}

.stat-info h3 {
  margin: 0 0 4px 0;
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
}

.highlight-card .stat-value {
  color: var(--color-active);
}

.card {
  background-color: var(--color-bg-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.recent-activity h2 {
  font-size: 1.25rem;
  margin-bottom: 16px;
}

.activity-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.activity-item {
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 16px;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  color: var(--color-text-light);
  font-size: 0.875rem;
  width: 80px;
}

.activity-badge {
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.activity-badge.toxic {
  background-color: #ffebee;
  color: #c62828;
}

.activity-badge.spam {
  background-color: #fff3e0;
  color: #ef6c00;
}

.activity-badge.action {
  background-color: #e3f2fd;
  color: #1565c0;
}

.activity-text {
  color: var(--color-text-body);
}
</style>
