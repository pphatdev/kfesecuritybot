<template>
  <div class="keywords-manager">
    <!-- Top Action Bar -->
    <div class="actions-bar glass-panel">
      <div class="search-box">
        <IconSearch class="icon search-icon" />
        <input type="text" v-model="searchQuery" placeholder="Search blocked keywords..." />
      </div>
      <button class="btn btn-primary" @click="showAddForm = !showAddForm">
        <template v-if="showAddForm">Close Editor</template>
        <template v-else>
          <IconPlus class="icon" />
          Add Blockword
        </template>
      </button>
    </div>

    <!-- Collapsible Add Keyword Form -->
    <div class="add-form glass-panel" v-if="showAddForm">
      <div class="form-title">
        <h3>Create Blocked Keyword</h3>
        <p>Define a new word or pattern to match and instantly delete.</p>
      </div>
      
      <div class="form-row">
        <div class="form-group flex-2">
          <label for="keyword-input">Keyword / Pattern</label>
          <input
            type="text"
            id="keyword-input"
            v-model="newWord"
            placeholder="e.g. crypto, free money..."
            @keyup.enter="addKeyword"
          />
        </div>
        <div class="form-group flex-1">
          <label for="category-select">Category</label>
          <select id="category-select" v-model="newCategory">
            <option value="spam">Spam / Promo</option>
            <option value="toxic">Toxic / Profanity</option>
          </select>
        </div>
        <div class="form-actions">
          <button class="btn btn-save" @click="addKeyword" :disabled="!newWord.trim()">
            <span>Save Pattern</span>
            <IconDeviceFloppy class="icon" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Tab Bar Selector -->
    <div class="tab-bar" v-if="!pending">
      <button :class="['tab-btn', { active: activeTab === 'spam' }]" @click="activeTab = 'spam'">
        <IconBan class="icon tab-icon" />
        <span class="tab-label">Spam Patterns</span>
        <span class="tab-count">{{ keywords?.spam?.length || 0 }}</span>
      </button>
      <button :class="['tab-btn', { active: activeTab === 'toxic' }]" @click="activeTab = 'toxic'">
        <IconShieldX class="icon tab-icon" />
        <span class="tab-label">Toxic Patterns</span>
        <span class="tab-count">{{ keywords?.toxic?.length || 0 }}</span>
      </button>
    </div>

    <!-- Active Tab Panel Container -->
    <div class="tab-panel" v-if="!pending">
      <!-- Spam Keywords Tab -->
      <div class="category-card" v-if="activeTab === 'spam'">
        <div class="category-header">
          <div class="header-title">
            <h3>Spam Detection Filter</h3>
            <p class="subtitle">These pattern matches trigger automatic deletion to filter promos and spam scripts.</p>
          </div>
        </div>
        
        <div class="category-body">
          <div v-if="!filteredSpam.length" class="empty-list">
            No matching spam keywords found.
          </div>
          <TransitionGroup name="tag" tag="div" class="tag-cloud" v-else>
            <span class="tag-pill spam-tag" v-for="word in filteredSpam" :key="word">
              <span class="tag-text">{{ word }}</span>
              <button class="tag-delete" @click="deleteKeyword(word, 'spam')" title="Delete pattern">×</button>
            </span>
          </TransitionGroup>
        </div>
      </div>

      <!-- Toxic Keywords Tab -->
      <div class="category-card" v-if="activeTab === 'toxic'">
        <div class="category-header">
          <div class="header-title">
            <h3>Toxic & Profanity Filter</h3>
            <p class="subtitle">These patterns match harmful, abusive, or highly toxic language and trigger immediate strike allocation.</p>
          </div>
        </div>
        
        <div class="category-body">
          <div v-if="!filteredToxic.length" class="empty-list">
            No matching toxic keywords found.
          </div>
          <TransitionGroup name="tag" tag="div" class="tag-cloud" v-else>
            <span class="tag-pill toxic-tag" v-for="word in filteredToxic" :key="word">
              <span class="tag-text">{{ word }}</span>
              <button class="tag-delete" @click="deleteKeyword(word, 'toxic')" title="Delete pattern">×</button>
            </span>
          </TransitionGroup>
        </div>
      </div>
    </div>
    
    <div class="loading-state glass-panel" v-else>
      <span class="spinner"></span>
      <p>Synchronizing blocklists...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IconSearch, IconPlus, IconDeviceFloppy, IconBan, IconShieldX } from '@tabler/icons-vue'

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
.keywords-manager {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.actions-bar {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 8px 16px;
  flex: 1;
  max-width: 400px;
  transition: var(--transition-smooth);
}

.search-box:focus-within {
  border-color: var(--color-active);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(229, 143, 36, 0.15);
}

.search-icon {
  font-size: 1.1rem;
  opacity: 0.6;
}

.search-box input {
  border: none;
  background: transparent;
  width: 100%;
  font-family: inherit;
  font-size: 0.95rem;
  color: var(--color-text-body);
  outline: none;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-smooth);
  font-family: inherit;
  font-size: 0.95rem;
}

.btn-primary {
  background: var(--color-primary) !important;
  color: var(--color-bg-app) !important;
  box-shadow: 0 4px 15px rgba(229, 143, 36, 0.2);
}

.btn-primary:hover {
  background: var(--color-primary-light) !important;
  transform: translateY(-1px);
}

.btn-save {
  background: var(--color-secondary) !important;
  color: var(--color-bg-app) !important;
  box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
  padding: 12px 24px;
}

.btn-save:hover {
  background: var(--color-secondary-light) !important;
}

.btn-save:disabled {
  background-color: var(--color-disabled-bg) !important;
  color: var(--color-disabled-text) !important;
  box-shadow: none;
  cursor: not-allowed;
}

.add-form {
  padding: 24px;
  animation: slideDown 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-title {
  margin-bottom: 24px;
}

.form-title h3 {
  margin: 0 0 4px 0;
  font-size: 1.15rem;
  color: var(--color-primary);
}

.form-title p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-light);
}

.form-row {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.flex-2 { flex: 2; min-width: 240px; }
.flex-1 { flex: 1; min-width: 160px; }

.form-group label {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-light);
  letter-spacing: 0.05em;
}

.form-group input, .form-group select {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: 0.95rem;
  background-color: rgba(0, 0, 0, 0.3);
  color: var(--color-text-body);
  outline: none;
  transition: var(--transition-smooth);
}

.form-group input:focus, .form-group select:focus {
  border-color: var(--color-active);
  background-color: rgba(0, 0, 0, 0.5);
}

.form-actions {
  display: flex;
  align-items: flex-end;
}

.tab-bar {
  display: inline-flex;
  gap: 4px;
  background-color: rgba(0, 0, 0, 0.3);
  padding: 6px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 24px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text-light);
  cursor: pointer;
  transition: var(--transition-smooth);
}

.tab-btn:hover {
  color: var(--color-text-white);
  background-color: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
  color: #FFFFFF !important;
  background-color: var(--color-primary);
  box-shadow: 0 4px 15px rgba(229, 143, 36, 0.3);
  border-color: rgba(255, 255, 255, 0.15);
}

.tab-count {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: var(--radius-lg);
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--color-text-light);
  font-weight: 600;
}

.tab-btn.active .tab-count {
  background-color: rgba(0, 0, 0, 0.25);
  color: #FFFFFF;
}

.tab-panel {
  background-color: var(--color-bg-surface) !important;
  backdrop-filter: var(--glass-backdrop);
  -webkit-backdrop-filter: var(--glass-backdrop);
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  transition: var(--transition-smooth);
}

.category-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-header {
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 18px;
}

.category-header h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-primary);
}

.category-body {
  flex: 1;
}

.empty-list {
  padding: 24px 0;
  color: var(--color-text-light);
  font-size: 0.9rem;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 600;
  font-family: monospace;
  box-shadow: var(--shadow-sm);
  transition: var(--transition-smooth);
}

.tag-pill:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.spam-tag {
  background-color: rgba(249, 115, 22, 0.15);
  color: #FDBA74;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.toxic-tag {
  background-color: rgba(239, 68, 68, 0.15);
  color: #FCA5A5;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.tag-text {
  user-select: all;
}

.tag-delete {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.1rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  opacity: 0.5;
  transition: var(--transition-smooth);
}

.tag-delete:hover {
  opacity: 1;
  transform: scale(1.2);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  gap: 16px;
  color: var(--color-text-light);
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--color-border);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Animations */
.tag-enter-active,
.tag-leave-active {
  transition: all 0.3s ease;
}
.tag-enter-from,
.tag-leave-to {
  opacity: 0;
  transform: scale(0.85);
}
</style>
