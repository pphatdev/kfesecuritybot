<template>
  <div class="keywords-manager">
    <div class="actions-bar">
      <div class="search-box">
        <input type="text" v-model="searchQuery" placeholder="Search keywords..." />
      </div>
      <button class="btn btn-primary" @click="showAddForm = !showAddForm">
        {{ showAddForm ? 'Cancel' : '+ Add Keyword' }}
      </button>
    </div>

    <!-- Add Keyword Form -->
    <div class="add-form card" v-if="showAddForm">
      <div class="form-group">
        <label>Keyword:</label>
        <input type="text" v-model="newWord" placeholder="Enter word to block..." />
      </div>
      <div class="form-group">
        <label>Category:</label>
        <select v-model="newCategory">
          <option value="spam">Spam</option>
          <option value="toxic">Toxic</option>
        </select>
      </div>
      <button class="btn btn-primary" @click="addKeyword" :disabled="!newWord.trim()">Save Keyword</button>
    </div>
    
    <div class="cards-layout" v-if="!pending">
      <!-- Spam Keywords -->
      <div class="card">
        <div class="card-header spam-header">
          <h2>Spam Keywords</h2>
          <span class="badge">{{ keywords?.spam?.length || 0 }} words</span>
        </div>
        <div class="card-body">
          <ul class="keyword-list">
            <li class="keyword-item" v-for="word in filteredSpam" :key="word">
              <span class="word">{{ word }}</span>
              <button class="btn-icon" @click="deleteKeyword(word, 'spam')">🗑️</button>
            </li>
          </ul>
        </div>
      </div>

      <!-- Toxic Keywords -->
      <div class="card">
        <div class="card-header toxic-header">
          <h2>Toxic Keywords</h2>
          <span class="badge">{{ keywords?.toxic?.length || 0 }} words</span>
        </div>
        <div class="card-body">
          <ul class="keyword-list">
            <li class="keyword-item" v-for="word in filteredToxic" :key="word">
              <span class="word">{{ word }}</span>
              <button class="btn-icon" @click="deleteKeyword(word, 'toxic')">🗑️</button>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div v-else>Loading keywords...</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const { data: keywords, pending, refresh } = useFetch('/api/keywords')

const showAddForm = ref(false)
const newWord = ref('')
const newCategory = ref('spam')
const searchQuery = ref('')

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
    newWord.value = ''
    showAddForm.value = false
    await refresh()
  } catch (err) {
    alert('Failed to add keyword: ' + err.message)
  }
}

async function deleteKeyword(word, category) {
  if (!confirm(`Are you sure you want to delete "${word}"?`)) return
  
  try {
    await $fetch('/api/keywords', {
      method: 'DELETE',
      body: { word, category }
    })
    await refresh()
  } catch (err) {
    alert('Failed to delete keyword: ' + err.message)
  }
}
</script>

<style scoped>
.actions-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.search-box input {
  padding: 10px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  width: 300px;
  font-family: inherit;
  font-size: 0.9rem;
}

.search-box input:focus {
  outline: none;
  border-color: var(--color-active);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-white);
}

.btn-primary:hover {
  background-color: var(--color-text-body);
}

.cards-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.card {
  background-color: var(--color-bg-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 1.1rem;
}

.spam-header {
  border-top: 4px solid #ef6c00;
}

.toxic-header {
  border-top: 4px solid #c62828;
}

.badge {
  background-color: var(--color-bg-app);
  padding: 4px 10px;
  border-radius: var(--radius-lg);
  font-size: 0.75rem;
  color: var(--color-text-light);
  font-weight: 600;
}

.card-body {
  padding: 0;
}

.keyword-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.keyword-item {
  padding: 12px 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.keyword-item:hover {
  background-color: var(--color-bg-app);
}

.keyword-item:last-child {
  border-bottom: none;
}

.word {
  font-family: monospace;
  font-size: 0.95rem;
  color: var(--color-text-body);
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.keyword-item:hover .btn-icon {
  opacity: 1;
}

.btn-icon:hover {
  transform: scale(1.1);
}

.add-form {
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: flex-end;
  gap: 16px;
  background-color: var(--color-bg-app);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-light);
}

.form-group input, .form-group select {
  padding: 10px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: 0.95rem;
}

.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: var(--color-active);
}
</style>
