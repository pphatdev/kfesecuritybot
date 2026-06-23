<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-(--text-heading) tracking-tight">Bot Settings</h1>
        <p class="text-sm text-(--text-muted) mt-1">Manage rate limits and authorized dashboard administrators.</p>
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

    <!-- Modern Segmented Tabs -->
    <div class="bg-(--bg-card) p-1.5 rounded-xl border border-(--border-color) inline-flex flex-wrap gap-1 shadow-(--shadow-sm)">
      <button 
        @click="activeTab = 'rate-limits'"
        class="px-5 py-2 text-sm font-semibold rounded-lg transition-all flex items-center gap-2 duration-200"
        :class="activeTab === 'rate-limits' ? 'bg-primary text-white shadow-md transform scale-[1.02]' : 'text-(--text-muted) hover:text-(--text-heading) hover:bg-(--bg-layout)/50'"
      >
        <IconShieldCheck class="w-4 h-4" />
        Rate Limiting
      </button>
      <button 
        @click="activeTab = 'admins'"
        class="px-5 py-2 text-sm font-semibold rounded-lg transition-all flex items-center gap-2 duration-200"
        :class="activeTab === 'admins' ? 'bg-primary text-white shadow-md transform scale-[1.02]' : 'text-(--text-muted) hover:text-(--text-heading) hover:bg-(--bg-layout)/50'"
      >
        <IconShieldLock class="w-4 h-4" />
        Administrators
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="pendingSettings || pendingAdmins" class="flex flex-col items-center justify-center py-12 text-(--text-muted)">
      <IconLoader class="w-8 h-8 animate-spin mb-3" />
      <span class="text-sm font-medium">Loading settings...</span>
    </div>

    <!-- Rate Limiting Tab Content -->
    <div v-else-if="activeTab === 'rate-limits'" class="space-y-6">
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
                  :disabled="savingSettings"
                  class="px-5 py-2.5 bg-primary text-white text-sm font-semibold rounded-lg hover:bg-primary-hover focus:ring-4 focus:ring-primary/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
                >
                  <IconDeviceFloppy v-if="!savingSettings" class="w-4 h-4" />
                  <IconLoader v-else class="w-4 h-4 animate-spin" />
                  {{ savingSettings ? 'Saving...' : 'Save Settings' }}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Administrators Tab Content -->
    <div v-else-if="activeTab === 'admins'" class="space-y-6">
      <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) overflow-hidden">
        
        <div class="p-5 sm:p-6 border-b border-(--border-color) bg-(--bg-layout)/50 flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-(--text-heading) flex items-center gap-2">
              <IconShieldLock class="w-5 h-5 text-primary" />
              Authorized Users
            </h2>
            <p class="text-xs text-(--text-muted) mt-1 ml-7">These users can log in using Telegram OTP.</p>
          </div>
        </div>

        <div v-if="admins.length === 0" class="text-center py-12 text-(--text-muted)">
          <IconUsers class="w-12 h-12 mx-auto mb-3 opacity-20" />
          <p class="text-sm">No administrators found.</p>
        </div>

        <ul v-else class="divide-y divide-(--border-color)">
          <li v-for="admin in admins" :key="admin.id" class="flex items-center justify-between p-4 sm:p-5 hover:bg-(--bg-layout)/30 transition-colors">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold shadow-sm ring-1 ring-primary/20">
                <IconUser class="w-5 h-5" />
              </div>
              <div>
                <div class="font-semibold text-(--text-heading) text-sm flex items-center gap-2">
                  {{ admin.label }}
                  <span v-if="admin.source === 'env'" class="text-[10px] uppercase font-bold bg-amber-500/10 text-amber-500 px-2 py-0.5 rounded-full border border-amber-500/20">Super Admin</span>
                </div>
                <div class="text-xs text-(--text-muted) mt-0.5 font-mono">{{ admin.type === 'user_id' ? 'ID' : 'Username' }}</div>
              </div>
            </div>
            
            <div class="flex items-center gap-3">
              <button 
                v-if="admin.source === 'json'"
                @click="confirmRemoveAdmin(admin)"
                :disabled="removingAdmin === admin.id"
                class="p-2 text-(--text-muted) hover:text-danger hover:bg-danger-subtle rounded-lg transition-colors focus:ring-2 focus:ring-danger/20 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Revoke Access"
              >
                <IconLoader v-if="removingAdmin === admin.id" class="w-5 h-5 animate-spin" />
                <IconTrash v-else class="w-5 h-5" />
              </button>
              <span v-else class="text-xs text-(--text-muted) px-2 italic">Managed in .env</span>
            </div>
          </li>
        </ul>
        
        <div class="p-4 bg-(--bg-layout) border-t border-(--border-color)">
          <p class="text-[13px] text-(--text-muted) flex items-start gap-2">
            <IconInfoCircle class="w-4 h-4 shrink-0 mt-0.5" />
            <span>To add a new admin, use the Telegram command <code>/adduser @username</code> in a chat where the bot is present. Only existing admins can use this command.</span>
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watchEffect } from 'vue'
import { 
  IconAlertCircle, 
  IconCheck, 
  IconLoader, 
  IconShieldCheck,
  IconShieldLock,
  IconDeviceFloppy,
  IconUsers,
  IconUser,
  IconTrash,
  IconInfoCircle
} from '@tabler/icons-vue'

const activeTab = ref('rate-limits')

const error = ref('')
const success = ref('')

// Rate Limits State
const groupDelays = ref({})
const groups = ref([])
const savingSettings = ref(false)

// Admins State
const removingAdmin = ref(null)

const { data: settingsData, pending: pendingSettings } = await useFetch('/api/settings')
const { data: groupsData } = await useFetch('/api/groups')
const { data: adminsData, pending: pendingAdmins, refresh: refreshAdmins } = await useFetch('/api/admins')

const admins = computed(() => adminsData.value?.admins || [])

watchEffect(() => {
  if (settingsData.value && settingsData.value.group_delays) {
    groupDelays.value = { ...settingsData.value.group_delays }
  }
  
  if (groupsData.value && groupsData.value.groups) {
    groups.value = groupsData.value.groups.filter(item => item.type === 'Group/Channel')
  }
})

// Rate Limiting Logic
const getGroupDelay = (chatId) => groupDelays.value[chatId] || 0
const setGroupDelay = (chatId, value) => groupDelays.value[chatId] = parseInt(value) || 0

const saveSettings = async () => {
  error.value = ''
  success.value = ''
  savingSettings.value = true
  
  try {
    const res = await $fetch('/api/settings', {
      method: 'PUT',
      body: { group_delays: groupDelays.value }
    })
    
    if (res.success) {
      success.value = 'Per-group settings saved successfully!'
      setTimeout(() => success.value = '', 3000)
    }
  } catch (err) {
    error.value = err.data?.statusMessage || err.message || 'Failed to save settings.'
  } finally {
    savingSettings.value = false
  }
}

// Admins Logic
const confirmRemoveAdmin = async (admin) => {
  if (!confirm(`Are you sure you want to revoke dashboard access for ${admin.label}?`)) return
  
  error.value = ''
  success.value = ''
  removingAdmin.value = admin.id
  
  try {
    await $fetch('/api/admins', {
      method: 'DELETE',
      body: {
        target: admin.target,
        type: admin.type
      }
    })
    success.value = `Access revoked for ${admin.label}`
    await refreshAdmins()
    setTimeout(() => success.value = '', 3000)
  } catch (err) {
    error.value = err.data?.statusMessage || 'Failed to revoke access'
  } finally {
    removingAdmin.value = null
  }
}
</script>
