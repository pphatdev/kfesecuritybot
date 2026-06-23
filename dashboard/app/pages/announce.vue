<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-(--text-heading) tracking-tight">Announcements</h1>
        <p class="text-sm text-(--text-muted) mt-1">Broadcast messages to your monitored groups, channels, and private users.</p>
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

    <form @submit.prevent="sendAnnouncement" class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- Left Column: Compose Message -->
      <div class="lg:col-span-8 space-y-6">
        <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) p-5 sm:p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-(--text-heading) flex items-center gap-2">
              <IconMessageDots class="w-5 h-5 text-primary" />
              Compose Message
            </h2>
          </div>

          <!-- Templates Quick Picks -->
          <div class="mb-5">
            <label class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider mb-3">Quick Templates</label>
            <div class="flex flex-wrap gap-2">
              <button 
                v-for="tpl in templates" 
                :key="tpl.name" 
                type="button"
                @click="message = tpl.content"
                class="flex items-center gap-1.5 px-3 py-1.5 bg-(--bg-layout) border border-(--border-color) hover:border-primary hover:text-primary text-xs font-medium rounded-full transition-all text-(--text-body) shadow-sm"
              >
                <IconTemplate class="w-3.5 h-3.5 opacity-70" />
                {{ tpl.name }}
              </button>
            </div>
          </div>

          <!-- Textarea -->
          <div class="space-y-2">
            <label for="message" class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Message Body</label>
            <textarea 
              id="message" 
              v-model="message" 
              rows="8"
              placeholder="Enter your announcement here... HTML formatting (<b>, <i>, <a>, <code>) is fully supported."
              class="w-full bg-(--bg-layout) border border-(--border-color) rounded-lg px-4 py-3 text-sm text-(--text-body) placeholder:text-(--text-muted) focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all shadow-inner"
              required
            ></textarea>
            <div class="flex justify-between items-center text-xs text-(--text-muted) px-1">
              <span>Supports Telegram HTML syntax</span>
              <span :class="{'text-danger font-medium': message.length > 4000}">{{ message.length }} / 4000</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Select Recipients & Actions -->
      <div class="lg:col-span-4 space-y-6">
        
        <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) flex flex-col h-[500px]">
          <div class="p-5 border-b border-(--border-color) shrink-0">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-lg font-semibold text-(--text-heading) flex items-center gap-2">
                <IconUsers class="w-5 h-5 text-primary" />
                Recipients
              </h2>
              <span class="bg-primary-subtle text-primary text-xs font-bold px-2 py-0.5 rounded-full">
                {{ selectedGroups.length }} Selected
              </span>
            </div>

            <!-- Search / Filter -->
            <div class="relative">
              <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-(--text-muted)" />
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search recipients..." 
                class="w-full bg-(--bg-layout) border border-(--border-color) rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
              />
            </div>
          </div>

          <!-- Recipient List -->
          <div class="flex-1 overflow-y-auto p-2">
            <div v-if="pending" class="flex flex-col items-center justify-center h-full text-(--text-muted)">
              <IconLoader class="w-6 h-6 animate-spin mb-2" />
              <span class="text-sm">Loading...</span>
            </div>
            
            <div v-else-if="filteredGroups.length === 0" class="flex flex-col items-center justify-center h-full text-(--text-muted) px-4 text-center">
              <IconGhost class="w-8 h-8 mb-2 opacity-50" />
              <span class="text-sm">{{ searchQuery ? 'No recipients found.' : 'No recipients tracked yet.' }}</span>
            </div>

            <div v-else class="space-y-1">
              <label 
                v-for="group in filteredGroups" 
                :key="group.id"
                class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all hover:bg-(--bg-layout) group/item"
                :class="{'bg-primary-subtle/30': selectedGroups.includes(group.id)}"
              >
                <div class="relative flex items-center justify-center">
                  <input 
                    type="checkbox" 
                    :value="group.id" 
                    v-model="selectedGroups"
                    class="peer sr-only"
                  />
                  <div class="w-5 h-5 rounded border-2 border-(--border-color) peer-checked:bg-primary peer-checked:border-primary flex items-center justify-center transition-colors">
                    <IconCheck class="w-3.5 h-3.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity" stroke-width="3" />
                  </div>
                </div>
                
                <div class="flex flex-col overflow-hidden flex-1">
                  <span class="text-sm font-medium text-(--text-heading) truncate group-hover/item:text-primary transition-colors">{{ group.title }}</span>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span class="text-[10px] font-bold tracking-widest uppercase" :class="group.type === 'Private Chat' ? 'text-blue-500' : 'text-emerald-500'">
                      {{ group.type }}
                    </span>
                    <span class="text-xs text-(--text-muted) truncate font-mono opacity-60">{{ group.id }}</span>
                  </div>
                </div>
              </label>
            </div>
          </div>
          
          <div class="p-4 border-t border-(--border-color) bg-(--bg-layout)/50 shrink-0">
             <button type="button" @click="toggleSelectAll" class="w-full py-2 text-sm font-semibold text-(--text-heading) hover:bg-(--bg-layout) border border-(--border-color) rounded-lg transition-colors">
                {{ allFilteredSelected ? 'Deselect All Shown' : 'Select All Shown' }}
              </button>
          </div>
        </div>

        <!-- Action Card -->
        <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) p-5">
           <button 
              type="submit" 
              :disabled="sending || !message.trim() || selectedGroups.length === 0"
              class="w-full py-3.5 bg-primary text-white text-sm font-bold rounded-lg hover:bg-primary-hover focus:ring-4 focus:ring-primary/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-md hover:shadow-lg disabled:shadow-none"
            >
              <IconSend v-if="!sending" class="w-5 h-5" />
              <IconLoader v-else class="w-5 h-5 animate-spin" />
              {{ sending ? 'Broadcasting...' : 'Send Broadcast' }}
            </button>
            <p class="text-[11px] text-center text-(--text-muted) mt-3 leading-relaxed">
              Message will be immediately dispatched to <b>{{ selectedGroups.length }}</b> recipients. This action cannot be undone.
            </p>
        </div>

      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  IconAlertCircle, 
  IconCheck, 
  IconLoader, 
  IconSend, 
  IconMessageDots, 
  IconUsers, 
  IconTemplate, 
  IconSearch, 
  IconGhost 
} from '@tabler/icons-vue'

const message = ref('')
const selectedGroups = ref([])
const searchQuery = ref('')
const error = ref('')
const success = ref('')
const sending = ref(false)

const templates = [
  {
    name: 'Announcement',
    content: '📢 <b>Announcement</b>\n\nHello everyone,\n\n[Your message here]\n\nBest regards,\nAdmin Team'
  },
  {
    name: 'Event Invite',
    content: '🎉 <b>You are Invited!</b>\n\nJoin us for our upcoming event:\n📅 <b>Date:</b> [Date]\n⏰ <b>Time:</b> [Time]\n📍 <b>Location:</b> [Link or Place]\n\nWe hope to see you there!'
  },
  {
    name: 'Maintenance',
    content: '⚠️ <b>Maintenance Notice</b>\n\nOur systems will be undergoing scheduled maintenance on [Date] at [Time].\nExpect minor disruptions.\n\nThank you for your patience!'
  },
  {
    name: 'Rules Reminder',
    content: '🛡️ <b>Community Rules Reminder</b>\n\nPlease remember to be respectful and follow our community guidelines. Spam or toxic behavior will be removed automatically.\n\nThank you for helping us keep the chat clean!'
  }
]

const { data, pending, refresh } = await useFetch('/api/groups')

const groups = computed(() => {
  return data.value?.groups || []
})

const filteredGroups = computed(() => {
  if (!searchQuery.value.trim()) return groups.value
  const query = searchQuery.value.toLowerCase()
  return groups.value.filter(g => 
    g.title.toLowerCase().includes(query) || 
    g.id.toString().includes(query) ||
    g.type.toLowerCase().includes(query)
  )
})

const allFilteredSelected = computed(() => {
  if (filteredGroups.value.length === 0) return false
  return filteredGroups.value.every(g => selectedGroups.value.includes(g.id))
})

const toggleSelectAll = () => {
  if (allFilteredSelected.value) {
    // Remove all filtered from selected
    const filteredIds = filteredGroups.value.map(g => g.id)
    selectedGroups.value = selectedGroups.value.filter(id => !filteredIds.includes(id))
  } else {
    // Add all filtered to selected
    const current = new Set(selectedGroups.value)
    filteredGroups.value.forEach(g => current.add(g.id))
    selectedGroups.value = Array.from(current)
  }
}

const sendAnnouncement = async () => {
  if (!message.value.trim() || selectedGroups.value.length === 0) return
  
  error.value = ''
  success.value = ''
  sending.value = true
  
  try {
    const res = await $fetch('/api/announce', {
      method: 'POST',
      body: {
        message: message.value,
        chatIds: selectedGroups.value
      }
    })
    
    if (res.success) {
      message.value = ''
      selectedGroups.value = []
      success.value = `Successfully broadcasted to ${res.sent} recipient(s).`
      if (res.failed > 0) {
        success.value += ` Failed to send to ${res.failed} recipient(s).`
      }
    }
  } catch (err) {
    error.value = err.data?.statusMessage || err.message || 'An error occurred while sending the broadcast.'
  } finally {
    sending.value = false
  }
}
</script>
