<template>
  <div class="min-h-screen bg-[var(--bg-layout)] text-[var(--text-body)] flex font-sans" :data-bs-theme="isDark ? 'dark' : 'light'">
    <!-- Sidebar -->
    <aside class="w-[260px] bg-[var(--bg-card)] border-r border-[var(--border-color)] flex-shrink-0 flex flex-col transition-all duration-300 z-20 hidden md:flex shadow-[var(--shadow-sm)]">
      <div class="h-16 flex items-center px-6 border-b border-[var(--border-color)]">
        <IconShield class="w-8 h-8 text-[var(--color-primary)] mr-3" />
        <span class="font-heading font-bold text-[18px] text-[var(--text-heading)] leading-tight tracking-tight">BotControl ERP</span>
      </div>
      
      <div class="p-4 flex-1">
        <div class="mb-4">
          <div class="px-4 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-2">Main Menu</div>
          <nav class="flex flex-col gap-1">
            <NuxtLink to="/" class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-[14px] font-medium transition-all duration-200 text-[var(--text-body)] hover:bg-[var(--color-primary-subtle)] hover:text-[var(--color-primary)] group" exact-active-class="bg-[var(--color-primary-subtle)] text-[var(--color-primary)] font-semibold shadow-sm">
              <IconLayoutDashboard class="w-[18px] h-[18px] group-hover:scale-110 transition-transform" />
              Dashboard
            </NuxtLink>
            <NuxtLink to="/keywords" class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-[14px] font-medium transition-all duration-200 text-[var(--text-body)] hover:bg-[var(--color-primary-subtle)] hover:text-[var(--color-primary)] group" active-class="bg-[var(--color-primary-subtle)] text-[var(--color-primary)] font-semibold shadow-sm">
              <IconKey class="w-[18px] h-[18px] group-hover:scale-110 transition-transform" />
              Keyword Engine
            </NuxtLink>
            <NuxtLink to="/violations" class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-[14px] font-medium transition-all duration-200 text-[var(--text-body)] hover:bg-[var(--color-primary-subtle)] hover:text-[var(--color-primary)] group" active-class="bg-[var(--color-primary-subtle)] text-[var(--color-primary)] font-semibold shadow-sm">
              <IconAlertTriangle class="w-[18px] h-[18px] group-hover:scale-110 transition-transform" />
              User Violations
            </NuxtLink>
          </nav>
        </div>
      </div>

      <div class="p-4 border-t border-[var(--border-color)]">
        <button @click="logout" class="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-muted)] hover:bg-[var(--color-danger-subtle)] hover:text-[var(--color-danger)] transition-colors">
          <IconLogout class="w-[18px] h-[18px]" />
          Sign Out
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
      <!-- Topbar -->
      <header class="h-[64px] bg-[var(--bg-card)] border-b border-[var(--border-color)] flex items-center justify-between px-4 sm:px-6 shrink-0 shadow-[var(--shadow-sm)] z-10">
        <div class="flex items-center gap-4">
          <button class="md:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-[var(--text-muted)]">
            <IconMenu2 class="w-6 h-6" />
          </button>
          <div class="hidden sm:flex items-center text-sm font-medium text-[var(--text-muted)]">
            <span>BotControl</span>
            <IconChevronRight class="w-4 h-4 mx-2 opacity-50" />
            <span class="text-[var(--text-heading)] font-semibold">{{ currentRouteName }}</span>
          </div>
        </div>
        
        <div class="flex items-center gap-2 sm:gap-4">
          <!-- Theme Toggle -->
          <button @click="toggleTheme" class="w-10 h-10 rounded-full flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-[var(--text-muted)]">
            <IconSun v-if="isDark" class="w-5 h-5" />
            <IconMoon v-else class="w-5 h-5" />
          </button>
          
          <button class="w-10 h-10 rounded-full flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative text-[var(--text-muted)]">
            <IconBell class="w-5 h-5" />
            <span class="absolute top-2 right-2 w-2 h-2 bg-[var(--color-danger)] rounded-full animate-ping"></span>
            <span class="absolute top-2 right-2 w-2 h-2 bg-[var(--color-danger)] rounded-full border-2 border-[var(--bg-card)]"></span>
          </button>
           
          <!-- Profile -->
          <div class="flex items-center gap-3 pl-2 sm:pl-4 border-l border-[var(--border-color)]">
            <div class="w-9 h-9 rounded-full bg-[var(--color-primary-subtle)] text-[var(--color-primary)] flex items-center justify-center font-bold text-sm shadow-sm ring-2 ring-[var(--bg-card)]">
              AD
            </div>
            <div class="hidden md:flex flex-col">
              <span class="text-[13px] font-semibold text-[var(--text-heading)] leading-none">Admin User</span>
              <span class="text-[11px] text-[var(--text-muted)] mt-1">Administrator</span>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 relative">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { 
  IconShield, 
  IconLayoutDashboard, 
  IconKey, 
  IconAlertTriangle, 
  IconLogout,
  IconBell,
  IconMenu2,
  IconChevronRight,
  IconSun,
  IconMoon
} from '@tabler/icons-vue'

const route = useRoute()
const isDark = ref(true)

const toggleTheme = () => {
  isDark.value = !isDark.value
  if(isDark.value) {
    document.documentElement.setAttribute('data-bs-theme', 'dark')
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.setAttribute('data-bs-theme', 'light')
    document.documentElement.classList.remove('dark')
  }
}

onMounted(() => {
  // Set initial theme
  document.documentElement.setAttribute('data-bs-theme', 'dark')
  document.documentElement.classList.add('dark')
})

const currentRouteName = computed(() => {
  if (route.path === '/') return 'Dashboard Overview'
  if (route.path.includes('/keywords')) return 'Keyword Manager'
  if (route.path.includes('/violations')) return 'User Violations'
  return 'Application'
})

const logout = () => {
  // Add logout logic here
}
</script>
