<template>
  <div class="flex flex-col gap-6">
    <!-- Top Action Bar -->
    <div class="glass-card rounded-xl p-4 flex flex-col sm:flex-row justify-between items-center gap-4">
      <div class="relative w-full sm:w-96">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <IconSearch class="h-5 w-5 text-[var(--text-muted)]" />
        </div>
        <input 
          type="text" 
          v-model="searchQuery" 
          class="block w-full pl-10 pr-3 py-2 border border-[var(--border-color)] rounded-lg leading-5 bg-[var(--bg-card)] text-[var(--text-body)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] sm:text-sm transition-colors" 
          placeholder="Search blocked keywords..." 
        />
      </div>
      
      <button 
        @click="showAddForm = !showAddForm"
        class="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--color-primary)] transition-colors"
      >
        <template v-if="showAddForm">
          <IconX class="h-4 w-4" />
          Close Editor
        </template>
        <template v-else>
          <IconPlus class="h-4 w-4" />
          Add Blockword
        </template>
      </button>
    </div>

    <!-- Collapsible Add Keyword Form -->
    <div v-if="showAddForm" class="glass-card rounded-xl p-6 transition-all duration-300 transform origin-top animate-in slide-in-from-top-4 fade-in">
      <div class="mb-5 border-b border-[var(--border-color)] pb-4">
        <h3 class="text-lg font-semibold text-[var(--text-heading)]">Create Blocked Keyword</h3>
        <p class="text-sm text-[var(--text-muted)] mt-1">Define a new word or pattern to match and instantly delete.</p>
      </div>
      
      <div class="flex flex-col md:flex-row gap-4 items-end">
        <div class="flex-1 w-full">
          <label for="keyword-input" class="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">Keyword / Pattern</label>
          <input
            type="text"
            id="keyword-input"
            v-model="newWord"
            class="block w-full px-3 py-2.5 border border-[var(--border-color)] rounded-lg text-sm bg-[var(--bg-card)] text-[var(--text-body)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] transition-colors"
            placeholder="e.g. crypto, free money..."
            @keyup.enter="addKeyword"
          />
        </div>
        
        <div class="w-full md:w-64">
          <label for="category-select" class="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">Category</label>
          <select 
            id="category-select" 
            v-model="newCategory"
            class="block w-full px-3 py-2.5 border border-[var(--border-color)] rounded-lg text-sm bg-[var(--bg-card)] text-[var(--text-body)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] transition-colors appearance-none"
          >
            <option value="spam">Spam / Promo</option>
            <option value="toxic">Toxic / Profanity</option>
          </select>
        </div>
        
        <div class="w-full md:w-auto">
          <button 
            @click="addKeyword" 
            :disabled="!newWord.trim()"
            class="w-full flex items-center justify-center gap-2 px-6 py-2.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-[var(--color-success)] hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span>Save Pattern</span>
            <IconDeviceFloppy class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Tab Bar Selector -->
    <div v-if="!pending" class="flex flex-wrap gap-2 p-1.5 bg-slate-500/5 rounded-xl border border-[var(--border-color)] w-fit">
      <button 
        @click="activeTab = 'spam'"
        :class="[
          'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
          activeTab === 'spam' 
            ? 'bg-[var(--color-primary)] text-white shadow-sm' 
            : 'text-[var(--text-muted)] hover:text-[var(--text-heading)] hover:bg-slate-500/10'
        ]"
      >
        <IconBan class="w-4 h-4" />
        <span>Spam Patterns</span>
        <span :class="[
          'px-2 py-0.5 rounded-full text-xs font-semibold',
          activeTab === 'spam' ? 'bg-black/20 text-white' : 'bg-slate-500/10 text-[var(--text-muted)]'
        ]">
          {{ keywords?.spam?.length || 0 }}
        </span>
      </button>
      
      <button 
        @click="activeTab = 'toxic'"
        :class="[
          'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
          activeTab === 'toxic' 
            ? 'bg-[var(--color-primary)] text-white shadow-sm' 
            : 'text-[var(--text-muted)] hover:text-[var(--text-heading)] hover:bg-slate-500/10'
        ]"
      >
        <IconShieldX class="w-4 h-4" />
        <span>Toxic Patterns</span>
        <span :class="[
          'px-2 py-0.5 rounded-full text-xs font-semibold',
          activeTab === 'toxic' ? 'bg-black/20 text-white' : 'bg-slate-500/10 text-[var(--text-muted)]'
        ]">
          {{ keywords?.toxic?.length || 0 }}
        </span>
      </button>
    </div>

    <!-- Active Tab Panel Container -->
    <div v-if="!pending" class="glass-card rounded-xl overflow-hidden min-h-[400px] flex flex-col">
      
      <!-- Spam Keywords Tab -->
      <div v-if="activeTab === 'spam'" class="flex flex-col h-full animate-in fade-in duration-300">
        <div class="px-6 py-5 border-b border-[var(--border-color)] bg-[var(--bg-card)]">
          <h3 class="text-[15px] font-semibold text-[var(--text-heading)] flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-[var(--color-warning)]"></span>
            Spam Detection Filter
          </h3>
          <p class="text-[13px] text-[var(--text-muted)] mt-1">These pattern matches trigger automatic deletion to filter promos and spam scripts.</p>
        </div>
        
        <div class="p-6 flex-1 bg-slate-500/5">
          <div v-if="!filteredSpam.length" class="flex flex-col items-center justify-center h-48 text-[var(--text-muted)]">
            <IconBan class="w-12 h-12 mb-3 opacity-20" />
            <p class="text-sm">No matching spam keywords found.</p>
          </div>
          
          <TransitionGroup name="tag" tag="div" class="flex flex-wrap gap-3" v-else>
            <span 
              v-for="word in filteredSpam" 
              :key="word"
              class="inline-flex items-center gap-1.5 pl-3 pr-1.5 py-1.5 rounded-lg text-sm font-medium font-mono border border-amber-500/30 bg-amber-500/10 text-amber-500 shadow-sm hover:shadow-md transition-shadow group"
            >
              <span class="select-all">{{ word }}</span>
              <button 
                @click="deleteKeyword(word, 'spam')" 
                class="p-0.5 rounded-md text-amber-500/70 hover:text-amber-500 hover:bg-amber-500/20 transition-colors"
                title="Delete pattern"
              >
                <IconX class="w-4 h-4" />
              </button>
            </span>
          </TransitionGroup>
        </div>
      </div>

      <!-- Toxic Keywords Tab -->
      <div v-if="activeTab === 'toxic'" class="flex flex-col h-full animate-in fade-in duration-300">
        <div class="px-6 py-5 border-b border-[var(--border-color)] bg-[var(--bg-card)]">
          <h3 class="text-[15px] font-semibold text-[var(--text-heading)] flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-[var(--color-danger)]"></span>
            Toxic & Profanity Filter
          </h3>
          <p class="text-[13px] text-[var(--text-muted)] mt-1">These patterns match harmful, abusive, or highly toxic language and trigger immediate strike allocation.</p>
        </div>
        
        <div class="p-6 flex-1 bg-slate-500/5">
          <div v-if="!filteredToxic.length" class="flex flex-col items-center justify-center h-48 text-[var(--text-muted)]">
            <IconShieldX class="w-12 h-12 mb-3 opacity-20" />
            <p class="text-sm">No matching toxic keywords found.</p>
          </div>
          
          <TransitionGroup name="tag" tag="div" class="flex flex-wrap gap-3" v-else>
            <span 
              v-for="word in filteredToxic" 
              :key="word"
              class="inline-flex items-center gap-1.5 pl-3 pr-1.5 py-1.5 rounded-lg text-sm font-medium font-mono border border-red-500/30 bg-red-500/10 text-red-500 shadow-sm hover:shadow-md transition-shadow group"
            >
              <span class="select-all">{{ word }}</span>
              <button 
                @click="deleteKeyword(word, 'toxic')" 
                class="p-0.5 rounded-md text-red-500/70 hover:text-red-500 hover:bg-red-500/20 transition-colors"
                title="Delete pattern"
              >
                <IconX class="w-4 h-4" />
              </button>
            </span>
          </TransitionGroup>
        </div>
      </div>
    </div>
    
    <div v-else class="glass-card rounded-xl min-h-[400px] flex flex-col items-center justify-center gap-4 text-[var(--text-muted)]">
      <div class="w-8 h-8 border-4 border-slate-500/20 border-t-[var(--color-primary)] rounded-full animate-spin"></div>
      <p class="text-sm font-medium">Synchronizing blocklists...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IconSearch, IconPlus, IconX, IconDeviceFloppy, IconBan, IconShieldX } from '@tabler/icons-vue'

const { data: keywords, pending, refresh } = useFetch('/api/keywords')

const showAddForm = ref(false)
const newWord = ref('')
const newCategory = ref('spam')
const searchQuery = ref('')
const activeTab = ref('spam')

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

async function addKeyword() {
  if (!newWord.value.trim()) return
  
  try {
    await $fetch('/api/keywords', {
      method: 'POST',
      body: { word: newWord.value, category: newCategory.value }
    })
    activeTab.value = newCategory.value
    newWord.value = ''
    showAddForm.value = false
    await refresh()
  } catch (err) {
    alert('Failed to add keyword: ' + err.message)
  }
}

async function deleteKeyword(word, category) {
  if (!confirm(`Are you sure you want to remove "${word}" from the ${category} list?`)) return
  
  try {
    await $fetch(`/api/keywords?word=${encodeURIComponent(word)}&category=${encodeURIComponent(category)}`, {
      method: 'DELETE'
    })
    await refresh()
  } catch (err) {
    alert('Failed to delete keyword: ' + err.message)
  }
}
</script>

<style scoped>
.tag-enter-active,
.tag-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.tag-enter-from,
.tag-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(10px);
}
</style>
