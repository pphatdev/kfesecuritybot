<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-(--text-heading) tracking-tight">Bot Settings</h1>
        <p class="text-sm text-(--text-muted) mt-1">Configure automated rate limiting, delays, and anti-spam controls per group.</p>
      </div>
    </div>

    <!-- Error / Success Banners -->
    <div v-if="error" class="bg-danger-subtle text-danger px-4 py-3 rounded-lg text-sm border border-danger/20 flex items-start gap-3 shadow-sm">
      <IconAlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
      <span>{{ error }}</span>
    </div>
    <div v-if="success" class="bg-success-subtle text-success px-4 py-3 rounded-lg text-sm border border-success/20 flex items-start gap-3 shadow-sm">
      <IconCheck class="w-5 h-5 shrink-0 mt-0.5" />
      <span>{{ success }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="flex flex-col items-center justify-center py-12 text-(--text-muted)">
      <IconLoader class="w-8 h-8 animate-spin mb-3" />
      <span class="text-sm font-medium">Loading settings...</span>
    </div>

    <!-- Settings Form -->
    <div v-else class="space-y-6">
      
      <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) overflow-hidden">
        
        <div class="p-5 sm:p-6 border-b border-(--border-color) bg-(--bg-layout)/50 flex items-start justify-between">
          <div>
            <h2 class="text-lg font-semibold text-(--text-heading) flex items-center gap-2">
              <IconShieldCheck class="w-5 h-5 text-primary" />
              Per-Group Rate Limiting (Slow Mode)
            </h2>
            <p class="text-xs text-(--text-muted) mt-1 ml-7">Enforce a global delay between consecutive messages to prevent rapid-fire spam for specific groups.</p>
          </div>
        </div>

        <div class="p-5 sm:p-6 space-y-6">
          <form @submit.prevent="saveSettings">
            <div class="space-y-6">
              
              <div v-if="groups.length === 0" class="text-center py-8 text-(--text-muted) border border-dashed border-(--border-color) rounded-xl">
                <IconUsers class="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p class="text-sm">The bot is not tracking any groups yet.</p>
              </div>

              <!-- Group Sliders -->
              <div v-for="group in groups" :key="group.id" class="p-4 rounded-xl border border-(--border-color) bg-(--bg-layout)/30 hover:bg-(--bg-layout)/60 transition-colors">
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold shadow-sm ring-1 ring-primary/20">
                      {{ (group.title || '?').charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <div class="font-semibold text-(--text-heading) text-sm">{{ group.title }}</div>
                      <div class="text-xs text-(--text-muted)">ID: {{ group.id }}</div>
                    </div>
                  </div>
                  
                  <span class="text-sm font-bold bg-(--bg-card) px-3 py-1 rounded-full border border-(--border-color) shadow-sm" :class="getGroupDelay(group.id) > 0 ? 'text-primary' : 'text-(--text-muted)'">
                    {{ getGroupDelay(group.id) > 0 ? `${getGroupDelay(group.id)} Seconds` : 'Disabled' }}
                  </span>
                </div>
                
                <input 
                  type="range" 
                  min="0" 
                  max="60" 
                  step="1"
                  :value="getGroupDelay(group.id)"
                  @input="(e) => setGroupDelay(group.id, e.target.value)"
                  class="w-full h-2 bg-(--border-color) rounded-lg appearance-none cursor-pointer accent-primary"
                />
                
                <div class="flex justify-between items-center text-xs text-(--text-muted) mt-2 font-mono">
                  <span>0s</span>
                  <span>15s</span>
                  <span>30s</span>
                  <span>45s</span>
                  <span>60s</span>
                </div>
              </div>
              
              <p v-if="groups.length > 0" class="text-[13px] text-(--text-muted) bg-(--bg-layout) p-3 rounded-lg border border-(--border-color)">
                <strong>How it works:</strong> The bot will silently delete extra messages sent by a user if they type faster than the group's configured delay. 
              </p>

              <!-- Action Buttons -->
              <div class="pt-6 border-t border-(--border-color) flex justify-end">
                <button 
                  type="submit" 
                  :disabled="saving"
                  class="px-5 py-2.5 bg-primary text-white text-sm font-semibold rounded-lg hover:bg-primary-hover focus:ring-4 focus:ring-primary/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
                >
                  <IconDeviceFloppy v-if="!saving" class="w-4 h-4" />
                  <IconLoader v-else class="w-4 h-4 animate-spin" />
                  {{ saving ? 'Saving...' : 'Save Settings' }}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect, onMounted } from 'vue'
import { 
  IconAlertCircle, 
  IconCheck, 
  IconLoader, 
  IconShieldCheck,
  IconDeviceFloppy,
  IconUsers
} from '@tabler/icons-vue'

const groupDelays = ref({})
const groups = ref([])

const error = ref('')
const success = ref('')
const saving = ref(false)

const { data: settingsData, pending } = await useFetch('/api/settings')
const { data: groupsData } = await useFetch('/api/groups')

watchEffect(() => {
  if (settingsData.value && settingsData.value.group_delays) {
    // Clone the group delays object to avoid mutating the prop directly
    groupDelays.value = { ...settingsData.value.group_delays }
  }
  
  if (groupsData.value && groupsData.value.groups) {
    // We only want to show actual groups/supergroups for slow mode
    groups.value = groupsData.value.groups.filter(item => item.type === 'Group/Channel')
  }
})

const getGroupDelay = (chatId) => {
  return groupDelays.value[chatId] || 0
}

const setGroupDelay = (chatId, value) => {
  groupDelays.value[chatId] = parseInt(value) || 0
}

const saveSettings = async () => {
  error.value = ''
  success.value = ''
  saving.value = true
  
  try {
    const res = await $fetch('/api/settings', {
      method: 'PUT',
      body: {
        group_delays: groupDelays.value
      }
    })
    
    if (res.success) {
      success.value = 'Per-group settings saved successfully!'
      setTimeout(() => success.value = '', 3000)
    }
  } catch (err) {
    error.value = err.data?.statusMessage || err.message || 'Failed to save settings.'
  } finally {
    saving.value = false
  }
}
</script>
