<template>
  <div class="app-container">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <div class="logo">
        <IconShield class="icon logo-icon" />
        <h2>BotControl</h2>
      </div>
      <nav class="nav-menu">
        <NuxtLink to="/" class="nav-item">
          <IconLayoutDashboard class="icon nav-icon" />
          <span class="nav-label">Dashboard</span>
        </NuxtLink>
        <NuxtLink to="/keywords" class="nav-item">
          <IconKey class="icon nav-icon" />
          <span class="nav-label">Keywords</span>
        </NuxtLink>
        <NuxtLink to="/violations" class="nav-item">
          <IconAlertTriangle class="icon nav-icon" />
          <span class="nav-label">Violations</span>
        </NuxtLink>
      </nav>
      
      <div class="sidebar-spacer"></div>
      
      <!-- User Profile Card -->
      <div class="user-profile" v-if="authState?.authenticated">
        <div class="user-info">
          <div class="user-avatar">
            <span>{{ (authState.user?.username || authState.user?.user_id || 'U').substring(0, 2).toUpperCase() }}</span>
          </div>
          <div class="user-details">
            <span class="username" :title="authState.user?.username || authState.user?.user_id">
              @{{ authState.user?.username || authState.user?.user_id }}
            </span>
            <span class="user-role">Administrator</span>
          </div>
        </div>
        <button @click="logout" class="logout-btn">
          <span>Logout</span>
          <IconLogout class="icon btn-icon" />
        </button>
      </div>
    </aside>
    
    <!-- Main Content Area -->
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
import { IconShield, IconLayoutDashboard, IconKey, IconAlertTriangle, IconLogout } from '@tabler/icons-vue'

const route = useRoute()
const authState = useState('auth')

const logout = async () => {
  try {
    await $fetch('/api/auth/logout', { method: 'POST' })
  } catch (error) {
    console.error('Logout error:', error)
  }
  authState.value = { authenticated: false }
  navigateTo('/login')
}
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  padding: 16px;
  gap: 16px;
}

.sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  border-radius: var(--radius-lg);
  flex-shrink: 0;
  position: sticky;
  top: 24px;
  height: calc(100vh - 48px);
  background: rgba(20, 18, 16, 0.75) !important;
  backdrop-filter: blur(24px) saturate(150%);
  -webkit-backdrop-filter: blur(24px) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  box-shadow: 0 24px 40px rgba(0, 0, 0, 0.25) !important;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 2.2rem;
  color: #FFFFFF;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
}

.logo h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #FFFFFF !important;
  font-weight: 800;
  background: linear-gradient(135deg, #FFFFFF 0%, rgba(255, 255, 255, 0.6) 100%) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  letter-spacing: -0.02em;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.6) !important;
  font-weight: 600;
  border-radius: var(--radius-md);
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  position: relative;
  overflow: hidden;
  border: 1px solid transparent;
}

.nav-item:hover {
  color: #FFFFFF !important;
  background-color: rgba(255, 255, 255, 0.05) !important;
  transform: translateX(4px);
  border-color: rgba(255, 255, 255, 0.08);
}

.nav-item.router-link-active {
  color: #FFFFFF !important;
  background: rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.04) !important;
  transform: translateX(6px);
  border-color: rgba(255, 255, 255, 0.15);
}

.nav-item.router-link-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 15%;
  height: 70%;
  width: 4px;
  background: #FFFFFF;
  border-radius: 0 4px 4px 0;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.8);
}

.nav-icon {
  font-size: 1.2rem;
}

.nav-label {
  font-size: 1rem;
}

.sidebar-spacer {
  flex: 1;
}

.user-profile {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1) !important;
  color: #FFFFFF !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.user-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.username {
  font-weight: 600;
  color: #FFFFFF !important;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.75rem;
  color: rgba(253, 251, 247, 0.6) !important;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: var(--radius-sm);
  padding: 10px;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7) !important;
  cursor: pointer;
  transition: var(--transition-smooth);
  width: 100%;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: #FFFFFF !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.top-header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  flex-shrink: 0;
}

.header-title h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary) !important;
  background: none !important;
  -webkit-background-clip: unset !important;
  background-clip: unset !important;
  -webkit-text-fill-color: unset !important;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

@media (max-width: 1024px) {
  .app-container {
    flex-direction: column;
    padding: 16px;
    gap: 16px;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
    top: 0;
    padding: 20px;
  }
  
  .logo {
    margin-bottom: 20px;
  }
  
  .nav-menu {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .nav-item {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
  
  .sidebar-spacer {
    display: none;
  }
  
  .user-profile {
    margin-top: 20px;
  }
}
</style>
