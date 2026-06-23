<template>
  <div class="flex flex-col h-full animate-in fade-in duration-300">
    <div class="px-6 py-5 border-b border-(--border-color) bg-(--bg-card)">
      <h3 class="text-[15px] font-semibold text-(--text-heading) flex items-center gap-2">
        <span class="w-2 h-2 rounded-full" :class="colorClass"></span>
        {{ title }}
      </h3>
      <p class="text-[13px] text-(--text-muted) mt-1">{{ description }}</p>
    </div>
    
    <div class="p-6 flex-1 bg-slate-500/5">
      <div v-if="!items.length" class="flex flex-col items-center justify-center h-48 text-(--text-muted)">
        <component :is="icon" class="w-12 h-12 mb-3 opacity-20" />
        <p class="text-sm">{{ emptyMessage }}</p>
      </div>
      
      <TransitionGroup name="tag" tag="div" :class="isPattern ? 'flex flex-col gap-3' : 'flex flex-wrap gap-3'" v-else>
        <!-- Pattern Items -->
        <template v-if="isPattern">
          <div 
            v-for="p in items" 
            :key="p.word"
            class="flex flex-col gap-2 p-3 rounded-lg border shadow-sm transition-shadow group"
            :class="itemClass"
          >
            <div v-if="editingItem !== p.word">
              <div class="flex items-center justify-between gap-3">
                <span class="font-mono text-sm select-all">{{ p.word }}</span>
                <div class="flex items-center gap-1 shrink-0">
                  <button 
                    @click="startEdit(p.word, p.response)" 
                    class="p-1 rounded-md transition-colors"
                    :class="btnClass"
                    title="Edit pattern"
                  >
                    <IconPencil class="w-4 h-4" />
                  </button>
                  <button 
                    @click="$emit('delete', p.word)" 
                    class="p-1 rounded-md transition-colors"
                    :class="btnClass"
                    title="Delete pattern"
                  >
                    <IconX class="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div v-if="p.response" class="text-xs italic border-t pt-2 mt-2" :class="borderClass">
                Response: {{ p.response }}
              </div>
            </div>
            
            <div v-else class="flex flex-col gap-2">
              <input 
                v-model="editWord" 
                class="w-full px-2 py-1 text-sm rounded bg-(--bg-card) border focus:outline-none focus:ring-1 text-(--text-body)" 
                :class="borderClass"
                placeholder="Regex pattern"
                @keyup.enter="saveEdit(p.word)"
                @keyup.esc="cancelEdit"
                ref="editInputRef"
              />
              <input 
                v-model="editResponse" 
                class="w-full px-2 py-1 text-xs rounded bg-(--bg-card) border focus:outline-none focus:ring-1 text-(--text-body)" 
                :class="borderClass"
                placeholder="Response (optional)"
                @keyup.enter="saveEdit(p.word)"
                @keyup.esc="cancelEdit"
              />
              <div class="flex justify-end gap-1 mt-1">
                <button 
                  @click="saveEdit(p.word)" 
                  class="px-2 py-1 text-xs font-medium rounded-md transition-colors bg-success/20 text-success hover:bg-success/30"
                  title="Save"
                >
                  Save
                </button>
                <button 
                  @click="cancelEdit" 
                  class="px-2 py-1 text-xs font-medium rounded-md transition-colors bg-slate-500/20 text-slate-500 hover:bg-slate-500/30"
                  title="Cancel"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </template>
        
        <!-- Normal Items -->
        <template v-else>
          <span 
            v-for="word in items" 
            :key="word"
            class="inline-flex items-center gap-1.5 pl-3 pr-1.5 py-1.5 rounded-lg text-sm font-medium font-mono border shadow-sm hover:shadow-md transition-shadow group"
            :class="itemClass"
          >
            <template v-if="editingItem !== word">
              <span class="select-all">{{ formatWord(word) }}</span>
              <div class="flex items-center gap-0.5">
                <button 
                  @click="startEdit(word)" 
                  class="p-0.5 rounded-md transition-colors"
                  :class="btnClass"
                  title="Edit item"
                >
                  <IconPencil class="w-4 h-4" />
                </button>
                <button 
                  @click="$emit('delete', word)" 
                  class="p-0.5 rounded-md transition-colors"
                  :class="btnClass"
                  title="Delete item"
                >
                  <IconX class="w-4 h-4" />
                </button>
              </div>
            </template>
            <template v-else>
              <input 
                v-model="editWord" 
                class="w-32 px-1.5 py-0.5 text-sm rounded bg-(--bg-card) border focus:outline-none focus:ring-1 text-(--text-body)" 
                :class="borderClass"
                @keyup.enter="saveEdit(word)"
                @keyup.esc="cancelEdit"
                ref="editInputRef"
              />
              <div class="flex items-center gap-0.5">
                <button 
                  @click="saveEdit(word)" 
                  class="p-0.5 rounded-md transition-colors text-success hover:bg-success/20"
                  title="Save"
                >
                  <IconCheck class="w-4 h-4" />
                </button>
                <button 
                  @click="cancelEdit" 
                  class="p-0.5 rounded-md transition-colors text-slate-500 hover:bg-slate-500/20"
                  title="Cancel"
                >
                  <IconX class="w-4 h-4" />
                </button>
              </div>
            </template>
          </span>
        </template>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { IconX, IconPencil, IconCheck } from '@tabler/icons-vue'

const props = defineProps({
  items: { type: Array, required: true },
  title: String,
  description: String,
  colorClass: String,
  itemClass: String,
  btnClass: String,
  borderClass: String,
  icon: [Object, Function],
  emptyMessage: String,
  isPattern: Boolean,
  formatSticker: Boolean
})

const emit = defineEmits(['delete', 'edit'])

const editingItem = ref(null)
const editWord = ref('')
const editResponse = ref('')
const editInputRef = ref(null)

function startEdit(word, response = '') {
  editingItem.value = word
  editWord.value = word
  editResponse.value = response
  
  nextTick(() => {
    if (editInputRef.value) {
      const input = Array.isArray(editInputRef.value) ? editInputRef.value[0] : editInputRef.value
      if (input) input.focus()
    }
  })
}

function cancelEdit() {
  editingItem.value = null
  editWord.value = ''
  editResponse.value = ''
}

function saveEdit(oldWord) {
  if (!editWord.value.trim()) return
  
  // If nothing changed, just cancel
  if (editWord.value.trim() === oldWord && editResponse.value.trim() === (props.isPattern ? (editResponse.value || '') : '')) {
    cancelEdit()
    return
  }

  emitEdit(oldWord)
}

function emitEdit(oldWord) {
  emit('edit', {
    oldWord,
    newWord: editWord.value.trim(),
    newResponse: editResponse.value.trim()
  })
  cancelEdit()
}

function formatWord(word) {
  if (!props.formatSticker) return word;
  if (!word || typeof word !== 'string') return '[Unknown]'
  if (word.startsWith('pack:')) return `[Pack] ${word.substring(5)}`
  if (word.startsWith('emoji:')) return `[Emoji] ${word.substring(6)}`
  if (word.startsWith('id:')) return `[ID] ${word.substring(3)}`
  return `[Pack] ${word}`
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
