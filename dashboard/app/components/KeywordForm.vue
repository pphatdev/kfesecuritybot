<template>
  <div class="glass-card rounded-xl p-6 transition-all duration-300 transform origin-top animate-in slide-in-from-top-4 fade-in">
    <div class="mb-5 border-b border-(--border-color) pb-4">
      <h3 class="text-lg font-semibold text-(--text-heading)">Create Blocked Keyword</h3>
      <p class="text-sm text-(--text-muted) mt-1">Define a new word or pattern to match and instantly delete.</p>
    </div>
    
    <div class="flex flex-col md:flex-row gap-4 items-end">
      <div class="flex-1 w-full">
        <label for="keyword-input" class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider mb-2">
          {{ category === 'sticker' ? 'Identifier' : 'Keyword / Pattern' }}
        </label>
        <InputText
          id="keyword-input"
          v-model="word"
          unstyled
          class="block w-full px-3 py-2.5 border border-(--border-color) rounded-lg text-sm bg-(--bg-card) text-(--text-body) focus:outline-none focus:ring-2 focus:ring-primary transition-colors"
          :placeholder="category === 'sticker' ? 'e.g. MyPackName, 😀, or AgAD...' : (category === 'file_ext' ? 'e.g. .exe, .apk...' : 'e.g. crypto, free money...')"
          @keyup.enter="handleAdd"
        />
      </div>
      
      <div class="w-full md:w-64">
        <label for="category-select" class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider mb-2">Category</label>
        <select 
          v-model="category"
          class="block w-full px-3 py-2.5 border border-(--border-color) rounded-lg text-sm bg-(--bg-card) text-(--text-body) focus:outline-none focus:ring-2 focus:ring-primary transition-colors appearance-none"
        >
          <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      
      <div class="w-full md:w-64" v-if="category === 'sticker'">
        <label for="sticker-type-select" class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider mb-2">Ban Type</label>
        <select 
          v-model="stickerBanType"
          class="block w-full px-3 py-2.5 border border-(--border-color) rounded-lg text-sm bg-(--bg-card) text-(--text-body) focus:outline-none focus:ring-2 focus:ring-primary transition-colors appearance-none"
        >
          <option v-for="opt in stickerTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>

      <div class="w-full md:w-auto" v-if="category === 'pattern'">
        <label for="response-input" class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider mb-2">Custom Response (Optional)</label>
        <InputText
          id="response-input"
          v-model="response"
          unstyled
          class="block w-full px-3 py-2.5 border border-(--border-color) rounded-lg text-sm bg-(--bg-card) text-(--text-body) focus:outline-none focus:ring-2 focus:ring-primary transition-colors"
          placeholder="e.g. No links allowed!"
          @keyup.enter="handleAdd"
        />
      </div>
      
      <div class="w-full md:w-auto">
        <Button 
          @click="handleAdd" 
          :disabled="!word.trim()"
          unstyled
          class="w-full flex items-center justify-center gap-2 px-6 py-2.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-success hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span>Save Pattern</span>
          <IconDeviceFloppy class="h-4 w-4" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { IconDeviceFloppy } from '@tabler/icons-vue'

const emit = defineEmits(['add-keyword'])

const word = ref('')
const category = ref('spam')
const stickerBanType = ref('pack')
const response = ref('')

const categoryOptions = [
  { label: 'Spam / Promo', value: 'spam' },
  { label: 'Toxic / Profanity', value: 'toxic' },
  { label: 'Regex Pattern', value: 'pattern' },
  { label: 'Sticker Pack', value: 'sticker' },
  { label: 'File Extension', value: 'file_ext' }
]

const stickerTypeOptions = [
  { label: 'Pack Name', value: 'pack' },
  { label: 'Specific Emoji', value: 'emoji' },
  { label: 'Unique ID (Index)', value: 'id' }
]

function handleAdd() {
  if (!word.value.trim()) return
  
  let finalWord = word.value.trim()
  if (category.value === 'sticker') {
    finalWord = `${stickerBanType.value}:${finalWord}`
  }

  emit('add-keyword', {
    word: finalWord,
    category: category.value,
    response: category.value === 'pattern' ? response.value.trim() : undefined
  })
  
  word.value = ''
  response.value = ''
}
</script>
