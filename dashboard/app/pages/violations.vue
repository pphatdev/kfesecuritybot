<template>
  <div class="flex flex-col gap-6">
    <div class="glass-card rounded-xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
      <!-- Header -->
      <div class="px-6 py-5 border-b border-(--border-color) bg-(--bg-card) flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 class="text-[16px] font-semibold text-(--text-heading) flex items-center gap-2">
            <IconAlertTriangle class="w-5 h-5 text-warning" />
            User Strike Tracking
          </h2>
          <p class="text-[13px] text-(--text-muted) mt-1">Moderation record. Users with 4+ strikes trigger the public warning callout.</p>
        </div>
        
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-500/5 border border-(--border-color)">
          <span class="relative flex h-2 w-2">
            <span v-if="!pending" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2" :class="pending ? 'bg-(--text-muted)' : 'bg-success'"></span>
          </span>
          <span class="text-[11px] font-semibold uppercase tracking-wider text-(--text-muted)">
            {{ pending ? 'Syncing...' : 'Live Monitoring' }}
          </span>
        </div>
      </div>
      
      <!-- Content -->
      <div class="bg-(--bg-card)">
        <div v-if="!stats || !Object.keys(stats.violations || {}).length" class="flex flex-col items-center justify-center py-20 text-(--text-muted)">
          <IconShield class="w-16 h-16 mb-4 opacity-20" />
          <p class="text-sm font-medium">No user violations recorded. Chat members are behaving well!</p>
        </div>
        
        <div class="w-full overflow-x-auto" v-else>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-slate-500/5 border-b border-(--border-color)">
                <th class="py-3 px-6 text-xs font-semibold text-(--text-muted) uppercase tracking-wider whitespace-nowrap">User / Identity</th>
                <th class="py-3 px-6 text-xs font-semibold text-(--text-muted) uppercase tracking-wider whitespace-nowrap">Strikes Logged</th>
                <th class="py-3 px-6 text-xs font-semibold text-(--text-muted) uppercase tracking-wider whitespace-nowrap">Threat Level</th>
                <th class="py-3 px-6 text-xs font-semibold text-(--text-muted) uppercase tracking-wider whitespace-nowrap">Last Violation Time</th>
                <th class="py-3 px-6 text-xs font-semibold text-(--text-muted) uppercase tracking-wider text-right whitespace-nowrap">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-(--border-color)">
              <tr v-for="(vData, userId) in stats.violations" :key="userId" 
                  class="transition-colors hover:bg-slate-500/5 group"
                  :class="getRowClass(vData.strikes)">
                
                <!-- User Profile -->
                <td class="py-4 px-6 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full text-white flex items-center justify-center font-bold text-sm shadow-sm shrink-0" :style="getAvatarStyle(vData.username)">
                      {{ vData.username.substring(0, 2).toUpperCase() }}
                    </div>
                    <div class="flex flex-col">
                      <span class="text-sm font-semibold text-primary">@{{ vData.username }}</span>
                      <span class="text-xs text-(--text-muted) font-mono mt-0.5">ID: {{ userId }}</span>
                    </div>
                  </div>
                </td>
                
                <!-- Strike Count -->
                <td class="py-4 px-6 whitespace-nowrap">
                  <div class="flex flex-col gap-1.5 w-32">
                    <span :class="['text-sm font-bold', getStrikeColor(vData.strikes)]">
                      {{ vData.strikes }} Strike{{ vData.strikes > 1 ? 's' : '' }}
                    </span>
                    <div class="h-1.5 w-full bg-slate-500/10 rounded-full overflow-hidden">
                      <div :class="['h-full rounded-full transition-all duration-500', getStrikeBg(vData.strikes)]" 
                           :style="{ width: Math.min(100, (vData.strikes / 4) * 100) + '%' }"></div>
                    </div>
                  </div>
                </td>
                
                <!-- Status Badge -->
                <td class="py-4 px-6 whitespace-nowrap">
                  <span :class="['inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider border', getBadgeClass(vData.strikes)]">
                    {{ getBadgeText(vData.strikes) }}
                  </span>
                </td>
                
                <!-- Time -->
                <td class="py-4 px-6 whitespace-nowrap text-sm text-(--text-body)">
                  {{ vData.last_violation || 'N/A' }}
                </td>
                
                <!-- Actions -->
                <td class="py-4 px-6 whitespace-nowrap text-right">
                  <button 
                    @click="resetStrikes(userId, vData.username)"
                    class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-(--text-muted) hover:text-(--text-heading) hover:bg-slate-500/10 border border-transparent hover:border-(--border-color) transition-all"
                    title="Clear strikes"
                  >
                    <span>Reset</span>
                    <IconRefresh class="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Custom Modal/Alert Dialog -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="modal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div class="bg-(--bg-card) border border-(--border-color) rounded-2xl shadow-(--shadow-lg) max-w-md w-full overflow-hidden p-6 space-y-4 transform scale-100 transition-all select-none">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0" :class="modal.type === 'danger' ? 'bg-danger-subtle text-danger' : modal.type === 'warning' ? 'bg-warning-subtle text-warning' : 'bg-success-subtle text-success'">
              <IconAlertTriangle class="w-5 h-5" v-if="modal.type === 'danger'" />
              <IconAlertCircle class="w-5 h-5" v-else-if="modal.type === 'warning'" />
              <IconCheck class="w-5 h-5" v-else />
            </div>
            <div class="space-y-1 flex-1">
              <h3 class="text-base font-semibold text-(--text-heading)">{{ modal.title }}</h3>
              <p class="text-sm text-(--text-muted) leading-relaxed">{{ modal.message }}</p>
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button 
              v-if="modal.isConfirm"
              type="button" 
              @click="closeModal(false)"
              class="px-4 py-2 border border-(--border-color) hover:bg-(--bg-layout) rounded-lg text-sm font-semibold text-(--text-body) hover:text-(--text-heading) transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button 
              type="button" 
              @click="closeModal(true)"
              class="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all cursor-pointer shadow-md hover:shadow-lg"
              :class="modal.type === 'danger' ? 'bg-danger hover:bg-danger/90' : 'bg-primary hover:bg-primary-hover'"
            >
              {{ modal.isConfirm ? 'Confirm' : 'OK' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { IconAlertTriangle, IconShield, IconRefresh, IconAlertCircle, IconCheck } from '@tabler/icons-vue'

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
  if (strikes >= 4) return 'bg-red-500/5 hover:bg-red-500/10'
  if (strikes >= 2) return 'bg-amber-500/5 hover:bg-amber-500/10'
  return ''
}

function getStrikeColor(strikes) {
  if (strikes >= 4) return 'text-red-400'
  if (strikes >= 2) return 'text-amber-400'
  return 'text-emerald-400'
}

function getStrikeBg(strikes) {
  if (strikes >= 4) return 'bg-red-400'
  if (strikes >= 2) return 'bg-amber-400'
  return 'bg-emerald-400'
}

function getBadgeClass(strikes) {
  if (strikes >= 4) return 'bg-red-500/10 text-red-500 border-red-500/20'
  if (strikes >= 2) return 'bg-amber-500/10 text-amber-500 border-amber-500/20'
  return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
}

function getBadgeText(strikes) {
  if (strikes >= 4) return 'Critical Threat'
  if (strikes >= 2) return 'Active Warning'
  return 'Monitored / Safe'
}

// Generate a deterministic gradient background based on username for beautiful avatars
function getAvatarStyle(username) {
  if (!username) return {}
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  const c1 = `hsl(${Math.abs(hash) % 360}, 65%, 45%)`
  const c2 = `hsl(${(Math.abs(hash) + 60) % 360}, 65%, 35%)`
  return {
    background: `linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`
  }
}

const modal = ref({
  show: false,
  title: '',
  message: '',
  type: 'warning',
  isConfirm: false,
  onConfirm: null
})

const showModal = (title, message, type = 'warning', isConfirm = false) => {
  return new Promise((resolve) => {
    modal.value = {
      show: true,
      title,
      message,
      type,
      isConfirm,
      onConfirm: (result) => {
        modal.value.show = false
        resolve(result)
      }
    }
  })
}

const closeModal = (result) => {
  if (modal.value.onConfirm) {
    modal.value.onConfirm(result)
  }
}

async function resetStrikes(userId, username) {
  const confirmed = await showModal(
    'Clear Strikes?',
    `Are you sure you want to clear all violation strikes for @${username}?`,
    'warning',
    true
  )
  if (!confirmed) return
  
  try {
    await $fetch(`/api/violations?userId=${userId}`, {
      method: 'DELETE'
    })
    await refresh()
  } catch (err) {
    showModal('Failed to reset strikes', err.message, 'danger', false)
  }
}
</script>
