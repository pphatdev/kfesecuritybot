<template>
  <div class="flex flex-col gap-6">
    <!-- Quick Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <!-- Total Messages Scanned -->
      <div class="glass-card rounded-xl p-5 relative overflow-hidden group">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Total Messages Scanned</h3>
            <p class="text-3xl font-bold text-(--text-heading) mt-1 font-mono">{{ stats?.total_messages_scanned || 0 }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary-subtle flex items-center justify-center text-primary">
            <IconMail class="w-5 h-5" />
          </div>
        </div>
        <div class="flex items-center gap-2 mt-4">
          <span class="inline-flex items-center gap-1.5 px-2 py-1 text-[11px] font-semibold rounded bg-success-subtle text-success uppercase tracking-wider">
            <span class="w-1.5 h-1.5 rounded-full bg-success animate-pulse"></span>
            Active Scan
          </span>
          <span class="text-xs text-(--text-muted)">Live monitoring</span>
        </div>
        <!-- Decorative subtle background -->
        <div class="absolute -bottom-6 -right-6 w-24 h-24 bg-primary-subtle rounded-full blur-2xl opacity-50 group-hover:opacity-100 transition-opacity"></div>
      </div>
      
      <!-- Harmful Content Blocked -->
      <div class="glass-card rounded-xl p-5 relative overflow-hidden group">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Harmful Content Blocked</h3>
            <p class="text-3xl font-bold text-(--text-heading) mt-1 font-mono">{{ stats?.spam_toxic_blocked || 0 }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-secondary-subtle flex items-center justify-center text-secondary">
            <IconShield class="w-5 h-5" />
          </div>
        </div>
        <div class="flex items-center gap-2 mt-4">
          <span class="inline-flex items-center gap-1.5 px-2 py-1 text-[11px] font-semibold rounded bg-info-subtle text-info uppercase tracking-wider">
            AI Moderated
          </span>
          <span class="text-xs text-(--text-muted)">{{ getBlockedRatio }}% block rate</span>
        </div>
        <!-- Decorative subtle background -->
        <div class="absolute -bottom-6 -right-6 w-24 h-24 bg-secondary-subtle rounded-full blur-2xl opacity-50 group-hover:opacity-100 transition-opacity"></div>
      </div>
      
      <!-- Repeat Offenders -->
      <div class="glass-card rounded-xl p-5 relative overflow-hidden group">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Repeat Offenders</h3>
            <p class="text-3xl font-bold text-danger mt-1 font-mono">{{ Object.keys(stats?.violations || {}).length }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-danger-subtle flex items-center justify-center text-danger">
            <IconAlertTriangle class="w-5 h-5" />
          </div>
        </div>
        <div class="flex items-center gap-2 mt-4">
          <span class="inline-flex items-center gap-1.5 px-2 py-1 text-[11px] font-semibold rounded bg-warning-subtle text-warning uppercase tracking-wider">
            Watchlist
          </span>
          <span class="text-xs text-(--text-muted)">Users with strikes</span>
        </div>
        <!-- Decorative subtle background -->
        <div class="absolute -bottom-6 -right-6 w-24 h-24 bg-danger-subtle rounded-full blur-2xl opacity-50 group-hover:opacity-100 transition-opacity"></div>
      </div>

    </div>
    
    <!-- Recent Bot Activity -->
    <div class="glass-card rounded-xl overflow-hidden flex flex-col flex-1 min-h-[400px]">
      <div class="px-6 py-5 border-b border-(--border-color) flex justify-between items-center bg-(--bg-card)">
        <div>
          <h2 class="text-[15px] font-semibold text-(--text-heading)">Recent Activity</h2>
          <p class="text-[13px] text-(--text-muted) mt-1">Live log of message moderation strikes</p>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-500/5 border border-(--border-color)">
          <span class="relative flex h-2 w-2">
            <span v-if="!pending" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2" :class="pending ? 'bg-(--text-muted)' : 'bg-success'"></span>
          </span>
          <span class="text-[11px] font-semibold uppercase tracking-wider text-(--text-muted)">
            {{ pending ? 'Loading...' : 'Live Monitoring' }}
          </span>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 bg-slate-500/5">
        <div v-if="!stats?.recent_activity?.length" class="flex flex-col items-center justify-center h-full text-(--text-muted) opacity-70">
          <IconMessage class="w-12 h-12 mb-4 opacity-50" />
          <p class="text-sm font-medium">No activity yet. Waiting for chat messages...</p>
        </div>
        
        <TransitionGroup name="list" tag="ul" class="flex flex-col gap-3" v-else>
          <li v-for="(activity, idx) in stats.recent_activity" :key="idx" 
              class="glass-card rounded-lg p-3 sm:p-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 hover:shadow-md transition-shadow group relative overflow-hidden">
            
            <div class="w-full sm:w-24 shrink-0 flex items-center">
              <span class="text-[13px] font-mono text-(--text-muted)">{{ activity.time }}</span>
            </div>
            
            <div class="shrink-0 flex items-center">
              <span :class="['inline-flex items-center justify-center px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider rounded border w-20 text-center', getBadgeClass(activity.type)]">
                {{ activity.type }}
              </span>
            </div>
            
            <div class="flex-1 min-w-0">
              <span class="text-[14px] text-(--text-body) block truncate" v-html="activity.text"></span>
            </div>
            
            <!-- Hover action area placeholder if needed -->
            <div class="hidden sm:flex opacity-0 group-hover:opacity-100 transition-opacity">
               <button class="p-1.5 text-(--text-muted) hover:text-primary rounded-md hover:bg-primary-subtle">
                 <IconDotsVertical class="w-4 h-4" />
               </button>
            </div>
          </li>
        </TransitionGroup>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { IconMail, IconShield, IconAlertTriangle, IconMessage, IconDotsVertical } from '@tabler/icons-vue'

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

const getBadgeClass = (type) => {
  const typeLower = type?.toLowerCase() || ''
  if (typeLower === 'toxic') {
    return 'bg-red-500/10 text-red-500 border-red-500/20'
  } else if (typeLower === 'spam') {
    return 'bg-amber-500/10 text-amber-500 border-amber-500/20'
  }
  return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
}
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-15px);
}
</style>
