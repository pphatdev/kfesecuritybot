<template>
  <div class="glass-card rounded-xl p-4 flex flex-col sm:flex-row justify-between items-center gap-4">
    <div class="relative w-full sm:w-96">
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">
        <IconSearch class="h-5 w-5 text-(--text-muted)" />
      </div>
      <InputText 
        v-model="model" 
        unstyled
        class="block w-full pl-10 pr-3 py-2 border border-(--border-color) rounded-lg leading-5 bg-(--bg-card) text-(--text-body) placeholder-(--text-muted) focus:outline-none focus:ring-2 focus:ring-primary sm:text-sm transition-colors" 
        placeholder="Search blocked keywords..." 
      />
    </div>
    
    <Button 
      @click="$emit('toggle-form')"
      unstyled
      :class="[
        'w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors',
        showAddForm ? 'bg-slate-600 hover:bg-slate-700' : 'bg-primary hover:bg-orange-500'
      ]"
    >
      <IconX v-if="showAddForm" class="h-4 w-4" />
      <IconPlus v-else class="h-4 w-4" />
      <span>{{ showAddForm ? 'Close Editor' : 'Add Blockword' }}</span>
    </Button>
  </div>
</template>

<script setup>
import { IconSearch, IconPlus, IconX } from '@tabler/icons-vue'

defineProps({
  showAddForm: Boolean
})

const model = defineModel()
defineEmits(['toggle-form'])
</script>
