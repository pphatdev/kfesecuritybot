<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="logo">
        <h2>🛡️ BotControl</h2>
      </div>
      <nav class="nav-menu">
        <NuxtLink to="/" class="nav-item">📊 Dashboard</NuxtLink>
        <NuxtLink to="/keywords" class="nav-item">🔑 Keywords</NuxtLink>
        <NuxtLink to="/violations" class="nav-item">⚠️ Violations</NuxtLink>
      </nav>
    </aside>
    
    <main class="main-content">
      <header class="top-header">
        <div class="header-title">
          <h1 v-if="route.path === '/'">Dashboard Overview</h1>
          <h1 v-else-if="route.path === '/keywords'">Keyword Manager</h1>
          <h1 v-else-if="route.path === '/violations'">User Violations</h1>
        </div>
      </header>
      
      <div class="page-content">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 250px;
  background-color: var(--color-bg-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 24px;
  border-bottom: 1px solid var(--color-border);
}

.logo h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-primary);
}

.nav-menu {
  padding: 16px 0;
  display: flex;
  flex-direction: column;
}

.nav-item {
  padding: 12px 24px;
  color: var(--color-text-body);
  font-weight: 500;
  transition: all 0.2s;
  border-left: 4px solid transparent;
}

.nav-item:hover {
  background-color: var(--color-bg-app);
}

.nav-item.router-link-active {
  color: var(--color-active);
  background-color: rgba(6, 115, 2, 0.05);
  border-left-color: var(--color-active);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-header {
  height: 72px;
  background-color: var(--color-bg-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  padding: 0 32px;
}

.header-title h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
}

.page-content {
  padding: 32px;
  flex: 1;
  overflow-y: auto;
}
</style>
