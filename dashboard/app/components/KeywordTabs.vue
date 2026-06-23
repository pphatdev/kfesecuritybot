<template>
  <div class="flex flex-wrap gap-2 p-1.5 bg-slate-500/5 rounded-xl border border-(--border-color) w-fit">
    <NuxtLink 
      v-for="tab in tabs" 
      :key="tab.id"
      :to="{ query: { ...$route.query, tab: tab.id } }"
      class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      :class="[
        activeTab === tab.id
          ? 'bg-primary text-white shadow-sm' 
          : 'text-(--text-muted) hover:text-(--text-heading) hover:bg-slate-500/10'
      ]"
    >
      <component :is="tab.icon" class="w-4 h-4" />
      <span>{{ tab.label }}</span>
      <span :class="[
        'px-2 py-0.5 rounded-full text-xs font-semibold',
        activeTab === tab.id ? 'bg-black/20 text-white' : 'bg-slate-500/10 text-(--text-muted)'
      ]">
        {{ getCount(tab.id) }}
      </span>
    </NuxtLink>
  </div>
</template>

<script setup>
import { IconBan, IconShieldX, IconCode, IconAlertTriangle } from '@tabler/icons-vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  keywords: {
    type: Object,
    default: () => ({})
  },
  activeTab: {
    type: String,
    default: 'spam'
  }
})

const $route = useRoute()

const tabs = [
  { id: 'spam', label: 'Spam Patterns', icon: IconBan },
  { id: 'toxic', label: 'Toxic Patterns', icon: IconShieldX },
  { id: 'pattern', label: 'Regex Patterns', icon: IconCode },
  { id: 'sticker', label: 'Sticker Packs', icon: IconAlertTriangle }
]

function getCount(tabId) {
  return props.keywords?.[tabId]?.length || 0
}
</script>
