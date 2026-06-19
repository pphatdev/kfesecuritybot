<template>
  <div class="violations-view">
    <div class="card">
      <div class="card-header">
        <h2>⚠️ User Strike Tracking <span v-if="pending" style="font-size: 0.8rem; font-weight: normal; color: var(--color-text-light)">(Live...)</span></h2>
        <p class="subtitle">Users with 4+ strikes will automatically trigger the "ជោរម្លេះ?" warning.</p>
      </div>
      
      <div v-if="!Object.keys(stats?.violations || {}).length" style="padding: 24px; color: var(--color-text-light);">
        No user violations recorded yet.
      </div>
      
      <table class="data-table" v-else>
        <thead>
          <tr>
            <th>User</th>
            <th>Strikes</th>
            <th>Status</th>
            <th>Last Violation</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(vData, userId) in stats.violations" :key="userId" :class="getRowClass(vData.strikes)">
            <td>
              <div class="user-info">
                <span class="avatar">{{ vData.username.substring(0, 2).toUpperCase() }}</span>
                <div>
                  <strong>@{{ vData.username }}</strong>
                  <span class="user-id">ID: {{ userId }}</span>
                </div>
              </div>
            </td>
            <td>
              <span :class="['strike-count', getStrikeColor(vData.strikes)]">{{ vData.strikes }} Strike{{ vData.strikes > 1 ? 's' : '' }}</span>
            </td>
            <td>
              <span :class="['badge', getBadgeColor(vData.strikes)]">{{ getBadgeText(vData.strikes) }}</span>
            </td>
            <td>{{ vData.last_violation }}</td>
            <td>
              <button class="btn-action" @click="resetStrikes(userId, vData.username)">Reset</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

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
  if (strikes >= 4) return 'Critical'
  if (strikes >= 2) return 'Warning'
  return 'Safe'
}

async function resetStrikes(userId, username) {
  if (!confirm(`Are you sure you want to reset strikes for @${username}?`)) return
  
  try {
    await $fetch('/api/violations', {
      method: 'DELETE',
      body: { userId }
    })
    await refresh()
  } catch (err) {
    alert('Failed to reset strikes: ' + err.message)
  }
}
</script>

<style scoped>
.card {
  background-color: var(--color-bg-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.card-header {
  padding: 24px;
  border-bottom: 1px solid var(--color-border);
}

.card-header h2 {
  margin: 0 0 8px 0;
  font-size: 1.25rem;
}

.subtitle {
  margin: 0;
  color: var(--color-text-light);
  font-size: 0.9rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 16px 24px;
  color: var(--color-text-light);
  font-weight: 500;
  font-size: 0.875rem;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-app);
}

.data-table td {
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table tbody tr:hover {
  background-color: var(--color-bg-app);
}

.danger-row {
  background-color: #fff8f8;
}

.warning-row {
  background-color: #fffcf5;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
}

.user-id {
  display: block;
  font-size: 0.8rem;
  color: var(--color-text-light);
}

.strike-count {
  font-weight: 600;
}

.strike-count.high { color: #c62828; }
.strike-count.medium { color: #ef6c00; }
.strike-count.low { color: var(--color-secondary); }

.badge {
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.red { background-color: #ffebee; color: #c62828; }
.badge.orange { background-color: #fff3e0; color: #ef6c00; }
.badge.green { background-color: #e8f5e9; color: #2e7d32; }

.btn-action {
  padding: 6px 12px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-action:hover {
  background-color: var(--color-bg-app);
  border-color: var(--color-text-light);
}
</style>
