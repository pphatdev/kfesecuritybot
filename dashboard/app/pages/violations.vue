<template>
  <div class="violations-view">
    <div class="card glass-panel">
      <!-- Header -->
      <div class="card-header">
        <div class="title-wrap">
          <h2>
            <IconAlertTriangle class="icon header-icon" />
            User Strike Tracking
          </h2>
          <p class="subtitle">Moderation record. Users with 4+ strikes trigger the public warning callout.</p>
        </div>
        <span class="status-indicator" :class="{ scanning: !pending }">
          <span class="dot"></span>
          {{ pending ? 'Syncing...' : 'Live Monitoring' }}
        </span>
      </div>
      
      <!-- Content -->
      <div class="card-body">
        <div v-if="!stats || !Object.keys(stats.violations || {}).length" class="empty-state">
          <IconShield class="icon empty-icon" />
          <p>No user violations recorded. Chat members are behaving well!</p>
        </div>
        
        <div class="table-container" v-else>
          <table class="data-table">
            <thead>
              <tr>
                <th>User / Identity</th>
                <th>Strikes Logged</th>
                <th>Threat Level</th>
                <th>Last Violation Time</th>
                <th class="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(vData, userId) in stats.violations" :key="userId" :class="getRowClass(vData.strikes)">
                <!-- User Profile -->
                <td>
                  <div class="user-info">
                    <div class="avatar" :style="getAvatarStyle(vData.username)">
                      {{ vData.username.substring(0, 2).toUpperCase() }}
                    </div>
                    <div class="user-meta">
                      <strong class="username">@{{ vData.username }}</strong>
                      <span class="user-id">ID: {{ userId }}</span>
                    </div>
                  </div>
                </td>
                
                <!-- Strike Count -->
                <td>
                  <div class="strike-metric">
                    <span :class="['strike-count', getStrikeColor(vData.strikes)]">
                      {{ vData.strikes }} Strike{{ vData.strikes > 1 ? 's' : '' }}
                    </span>
                    <div class="mini-bar-track">
                      <div :class="['mini-bar', getStrikeColor(vData.strikes)]" :style="{ width: Math.min(100, (vData.strikes / 4) * 100) + '%' }"></div>
                    </div>
                  </div>
                </td>
                
                <!-- Status Badge -->
                <td>
                  <span :class="['badge', getBadgeColor(vData.strikes)]">{{ getBadgeText(vData.strikes) }}</span>
                </td>
                
                <!-- Time -->
                <td class="time-cell">{{ vData.last_violation || 'N/A' }}</td>
                
                <!-- Actions -->
                <td class="text-right">
                  <button class="btn-action" @click="resetStrikes(userId, vData.username)" title="Clear strikes">
                    <span class="btn-text">Reset Strikes</span>
                    <IconRefresh class="icon btn-icon" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { IconAlertTriangle, IconShield, IconRefresh } from '@tabler/icons-vue'

const { data: stats, pending, refresh } = useFetch('/api/stats')

let pollInterval

onMounted(() => {
  pollInterval = setInterval(() => {
    refresh()
  }, 3000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

function getRowClass(strikes) {
  if (strikes >= 4) return 'danger-row'
  if (strikes >= 2) return 'warning-row'
  return ''
}

function getStrikeColor(strikes) {
  if (strikes >= 4) return 'high'
  if (strikes >= 2) return 'medium'
  return 'low'
}

function getBadgeColor(strikes) {
  if (strikes >= 4) return 'red'
  if (strikes >= 2) return 'orange'
  return 'green'
}

function getBadgeText(strikes) {
  if (strikes >= 4) return 'Critical Threat'
  if (strikes >= 2) return 'Active Warning'
  return 'Monitored / Safe'
}

// Generate a deterministic gradient background based on username for beautiful avatars
function getAvatarStyle(username) {
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  const c1 = `hsl(${hash % 360}, 65%, 45%)`
  const c2 = `hsl(${(hash + 60) % 360}, 65%, 35%)`
  return {
    background: `linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`,
    boxShadow: `0 4px 10px rgba(0, 0, 0, 0.1)`
  }
}

async function resetStrikes(userId, username) {
  if (!confirm(`Are you sure you want to clear all violation strikes for @${username}?`)) return
  
  try {
    await $fetch(`/api/violations?userId=${userId}`, {
      method: 'DELETE'
    })
    await refresh()
  } catch (err) {
    alert('Failed to reset strikes: ' + err.message)
  }
}
</script>

<style scoped>
.violations-view {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.card {
  overflow: hidden;
}

.card-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
}

.card-header h2 {
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

.card-body {
  padding: 0;
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

.header-icon {
  color: var(--color-accent) !important;
  margin-right: 8px;
  vertical-align: middle;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 14px 24px;
  color: var(--color-text-light);
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--color-border);
  background-color: rgba(0, 0, 0, 0.2);
}

.data-table td {
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
  transition: var(--transition-smooth);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table tbody tr {
  transition: var(--transition-smooth);
}

.data-table tbody tr:hover td {
  background-color: rgba(255, 255, 255, 0.03);
}

.danger-row td {
  background-color: rgba(239, 68, 68, 0.05);
}

.warning-row td {
  background-color: rgba(234, 179, 8, 0.05);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  color: var(--color-text-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  color: var(--color-primary);
  font-size: 0.95rem;
}

.user-id {
  font-size: 0.75rem;
  color: var(--color-text-light);
  font-family: monospace;
}

.strike-metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 140px;
}

.strike-count {
  font-size: 0.9rem;
  font-weight: 700;
}

.strike-count.high { color: #FCA5A5; }
.strike-count.medium { color: #FDBA74; }
.strike-count.low { color: #86EFAC; }

.mini-bar-track {
  height: 4px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.mini-bar {
  height: 100%;
  border-radius: 2px;
}

.mini-bar.high { background-color: #FCA5A5; }
.mini-bar.medium { background-color: #FDBA74; }
.mini-bar.low { background-color: #86EFAC; }

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  text-align: center;
}

.badge.red { background-color: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge.orange { background-color: rgba(249, 115, 22, 0.15); color: #FDBA74; border: 1px solid rgba(249, 115, 22, 0.3); }
.badge.green { background-color: rgba(34, 197, 94, 0.15); color: #86EFAC; border: 1px solid rgba(34, 197, 94, 0.3); }

.time-cell {
  font-size: 0.9rem;
  color: var(--color-text-body);
}

.text-right {
  text-align: right;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-white);
  transition: var(--transition-smooth);
}

.btn-action:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--color-text-white);
  transform: translateY(-1px);
}

.btn-action:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 0.95rem;
}
</style>
