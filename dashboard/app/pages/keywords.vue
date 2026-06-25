<template>
  <div class="flex flex-col gap-6">
    <KeywordSearch 
      v-model="searchQuery" 
      :show-add-form="showAddForm" 
      @toggle-form="showAddForm = !showAddForm" 
    />

    <KeywordForm 
      v-if="showAddForm" 
      @add-keyword="handleAddKeyword" 
    />
    
    <KeywordTabs 
      v-if="!pending" 
      :keywords="keywords" 
      :active-tab="activeTab"
    />

    <div v-if="!pending" class="glass-card rounded-xl overflow-hidden min-h-[400px] flex flex-col">
      <KeywordList
        v-if="activeTab === 'spam'"
        :items="filteredSpam"
        title="Spam Detection Filter"
        description="These pattern matches trigger automatic deletion to filter promos and spam scripts."
        color-class="bg-warning"
        item-class="border-amber-500/30 bg-amber-500/10 text-amber-500"
        btn-class="text-amber-500/70 hover:text-amber-500 hover:bg-amber-500/20"
        :icon="IconBan"
        empty-message="No matching spam keywords found."
        @delete="w => deleteKeyword(w, 'spam')"
        @edit="payload => editKeyword(payload, 'spam')"
      />

      <KeywordList
        v-else-if="activeTab === 'toxic'"
        :items="filteredToxic"
        title="Toxic & Profanity Filter"
        description="These patterns match harmful, abusive, or highly toxic language and trigger immediate strike allocation."
        color-class="bg-danger"
        item-class="border-red-500/30 bg-red-500/10 text-red-500"
        btn-class="text-red-500/70 hover:text-red-500 hover:bg-red-500/20"
        :icon="IconShieldX"
        empty-message="No matching toxic keywords found."
        @delete="w => deleteKeyword(w, 'toxic')"
        @edit="payload => editKeyword(payload, 'toxic')"
      />

      <KeywordList
        v-else-if="activeTab === 'pattern'"
        :items="filteredPattern"
        title="Regex Pattern Filter"
        description="Match messages based on regular expressions (e.g. \b[0-9]{4}\b) to block specific patterns."
        color-class="bg-primary"
        item-class="border-blue-500/30 bg-blue-500/10 text-blue-500"
        btn-class="text-blue-500/70 hover:text-blue-500 hover:bg-blue-500/20"
        border-class="border-blue-500/20 text-blue-500/80"
        :icon="IconCode"
        empty-message="No matching regex patterns found."
        :is-pattern="true"
        @delete="w => deleteKeyword(w, 'pattern')"
        @edit="payload => editKeyword(payload, 'pattern')"
      />

      <KeywordList
        v-else-if="activeTab === 'sticker'"
        :items="filteredSticker"
        title="Sticker Pack Filter"
        description="These sticker packs will trigger automatic deletion to filter inappropriate stickers."
        color-class="bg-indigo-500"
        item-class="border-indigo-500/30 bg-indigo-500/10 text-indigo-500"
        btn-class="text-indigo-500/70 hover:text-indigo-500 hover:bg-indigo-500/20"
        :icon="IconAlertTriangle"
        empty-message="No matching sticker packs found."
        :format-sticker="true"
        @delete="w => deleteKeyword(w, 'sticker')"
        @edit="payload => editKeyword(payload, 'sticker')"
      />
    </div>
    
    <div v-else class="glass-card rounded-xl min-h-[400px] flex flex-col items-center justify-center gap-4 text-(--text-muted)">
      <div class="w-8 h-8 border-4 border-slate-500/20 border-t-primary rounded-full animate-spin"></div>
      <p class="text-sm font-medium">Synchronizing blocklists...</p>
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
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import KeywordSearch from '~/components/KeywordSearch.vue'
import KeywordForm from '~/components/KeywordForm.vue'
import KeywordTabs from '~/components/KeywordTabs.vue'
import KeywordList from '~/components/KeywordList.vue'
import { IconBan, IconShieldX, IconCode, IconAlertTriangle, IconAlertCircle, IconCheck } from '@tabler/icons-vue'

const { data: keywords, pending, refresh } = useFetch('/api/keywords')
const router = useRouter()
const route = useRoute()

const showAddForm = ref(false)
const searchQuery = ref('')

const activeTab = computed(() => route.query.tab || 'spam')

// Filtered lists
const filteredSpam = computed(() => {
  if (!keywords.value?.spam) return []
  if (!searchQuery.value) return keywords.value.spam
  return keywords.value.spam.filter(word => word.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const filteredToxic = computed(() => {
  if (!keywords.value?.toxic) return []
  if (!searchQuery.value) return keywords.value.toxic
  return keywords.value.toxic.filter(word => word.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const filteredPattern = computed(() => {
  if (!keywords.value?.pattern) return []
  if (!searchQuery.value) return keywords.value.pattern
  return keywords.value.pattern.filter(p => {
    const wordStr = typeof p === 'string' ? p : p.word
    return wordStr.toLowerCase().includes(searchQuery.value.toLowerCase())
  })
})

const filteredSticker = computed(() => {
  if (!keywords.value?.sticker) return []
  if (!searchQuery.value) return keywords.value.sticker
  return keywords.value.sticker.filter(word => {
    if (typeof word !== 'string') return false
    return word.toLowerCase().includes(searchQuery.value.toLowerCase())
  })
})

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

async function handleAddKeyword(payload) {
  try {
    await $fetch('/api/keywords', {
      method: 'POST',
      body: payload
    })
    showAddForm.value = false
    await refresh()
    router.push({ query: { ...route.query, tab: payload.category } })
  } catch (err) {
    showModal('Failed to add keyword', err.message, 'danger', false)
  }
}

async function deleteKeyword(word, category) {
  const confirmed = await showModal(
    'Remove Keyword?',
    `Are you sure you want to remove "${word}" from the ${category} list?`,
    'danger',
    true
  )
  if (!confirmed) return
  
  try {
    await $fetch(`/api/keywords?word=${encodeURIComponent(word)}&category=${encodeURIComponent(category)}`, {
      method: 'DELETE'
    })
    await refresh()
  } catch (err) {
    showModal('Failed to delete keyword', err.message, 'danger', false)
  }
}

async function editKeyword(payload, category) {
  try {
    await $fetch('/api/keywords', {
      method: 'PUT',
      body: { ...payload, category }
    })
    await refresh()
  } catch (err) {
    showModal('Failed to update keyword', err.data?.statusMessage || err.message, 'danger', false)
  }
}
</script>
