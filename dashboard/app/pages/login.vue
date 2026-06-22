<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-(--bg-layout) relative overflow-hidden">
    <!-- Premium background effect -->
    <div class="absolute top-0 w-full h-full overflow-hidden pointer-events-none flex justify-center">
      <div class="absolute top-[-20%] w-[800px] h-[800px] bg-primary-subtle rounded-full blur-[100px] opacity-30"></div>
      <div class="absolute top-[40%] right-[-10%] w-[600px] h-[600px] bg-secondary-subtle rounded-full blur-[100px] opacity-20"></div>
    </div>

    <div class="glass-card w-full max-w-md p-8 sm:p-10 rounded-2xl shadow-(--shadow-lg) relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-subtle text-primary mb-4 ring-8 ring-(--bg-card) shadow-sm">
          <IconShieldLock class="w-8 h-8" />
        </div>
        <h2 class="text-2xl font-bold font-heading text-(--text-heading)">BotControl Panel</h2>
        <p class="text-(--text-muted) mt-1.5 text-sm">Dashboard Authentication</p>
      </div>

      <div class="bg-warning-subtle border-l-4 border-warning p-4 rounded-r-lg mb-6 text-sm">
        <h3 class="font-semibold text-warning mb-1.5">How to get your OTP:</h3>
        <ol class="list-decimal pl-5 text-(--text-body) space-y-1">
          <li>Open your Telegram bot chat.</li>
          <li>Send the command <code class="bg-black/10 dark:bg-black/30 px-1.5 py-0.5 rounded text-xs font-mono">/login</code>.</li>
          <li>The bot will send you a 6-digit OTP privately.</li>
        </ol>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label for="username" class="block text-sm font-medium text-(--text-heading) mb-1.5">Telegram Username or ID</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="e.g. pphat or 12345678"
            required
            :disabled="loading"
            class="block w-full px-4 py-3 border border-(--border-color) rounded-lg bg-(--bg-card) text-(--text-body) placeholder-(--text-muted) focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        <div>
          <label for="otp" class="block text-sm font-medium text-(--text-heading) mb-1.5">One-Time Password (OTP)</label>
          <input
            type="text"
            id="otp"
            v-model="otp"
            placeholder="Enter 6-digit OTP"
            pattern="[0-9]{6}"
            maxlength="6"
            required
            :disabled="loading"
            class="block w-full px-4 py-3 border border-(--border-color) rounded-lg bg-(--bg-card) text-(--text-body) placeholder-(--text-muted) focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed text-center tracking-widest font-mono text-lg"
          />
        </div>

        <div v-if="error" class="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-500 animate-in fade-in slide-in-from-top-1">
          <IconAlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
          <span>{{ error }}</span>
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-primary hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-0.5 active:translate-y-0"
        >
          <template v-if="loading">
            <span class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          </template>
          <template v-else>
            <span>Authenticate</span>
            <IconLockOpen class="w-5 h-5" />
          </template>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { IconShieldLock, IconAlertCircle, IconLockOpen } from '@tabler/icons-vue'

definePageMeta({
  layout: false
})

const username = ref('')
const otp = ref('')
const error = ref('')
const loading = ref(false)
const authState = useState('auth')

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: {
        username_or_id: username.value.trim(),
        otp: otp.value.trim()
      }
    })

    if (response.success) {
      authState.value = {
        authenticated: true,
        user: response.user
      }
      navigateTo('/')
    } else {
      error.value = 'Authentication failed.'
    }
  } catch (err) {
    error.value = err.data?.statusMessage || 'Failed to authenticate. Please check your OTP and try again.'
  } finally {
    loading.value = false
  }
}
</script>
