<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="login-header">
        <IconShieldLock class="icon lock-icon" />
        <h2>BotControl Panel</h2>
        <p>Dashboard Authentication</p>
      </div>

      <div class="instructions">
        <h3>How to get your OTP:</h3>
        <ol>
          <li>Open your Telegram bot chat.</li>
          <li>Send the command <code>/login</code>.</li>
          <li>The bot will send you a 6-digit OTP privately.</li>
        </ol>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Telegram Username or ID</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="e.g. pphat or 12345678"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="otp">One-Time Password (OTP)</label>
          <input
            type="text"
            id="otp"
            v-model="otp"
            placeholder="Enter 6-digit OTP"
            pattern="[0-9]{6}"
            maxlength="6"
            required
            :disabled="loading"
          />
        </div>

        <div v-if="error" class="error-message">
          <IconAlertCircle class="icon error-icon" />
          <span>{{ error }}</span>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <template v-if="loading">
            <span class="spinner"></span>
          </template>
          <template v-else>
            <span>Authenticate</span>
            <IconLockOpen class="icon" />
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

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: radial-gradient(circle at center, var(--color-bg-surface-solid) 0%, var(--color-bg-app) 100%);
  padding: 16px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  background-color: var(--color-bg-surface) !important;
  backdrop-filter: var(--glass-backdrop);
  -webkit-backdrop-filter: var(--glass-backdrop);
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.lock-icon {
  font-size: 3rem;
  display: block !important;
  margin: 0 auto 12px auto !important;
  color: var(--color-primary);
}

.login-header h2 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #FFFFFF 0%, rgba(255, 255, 255, 0.6) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.login-header p {
  margin: 4px 0 0 0;
  color: var(--color-text-light);
  font-size: 0.9rem;
}

.instructions {
  background-color: rgba(229, 143, 36, 0.1);
  border-left: 4px solid var(--color-primary);
  padding: 16px;
  border-radius: var(--radius-sm);
  margin-bottom: 24px;
  font-size: 0.85rem;
  color: var(--color-text-body);
}

.instructions h3 {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  color: var(--color-primary);
  font-weight: 600;
}

.instructions ol {
  margin: 0;
  padding-left: 20px;
  color: var(--color-text-body);
}

.instructions li {
  margin-bottom: 6px;
}

.instructions code {
  background-color: rgba(0, 0, 0, 0.4);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
  color: #FFFFFF;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-body);
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
  background-color: rgba(0, 0, 0, 0.3) !important;
  color: var(--color-text-white) !important;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.form-group input:focus {
  border-color: var(--color-active);
  box-shadow: 0 0 0 3px rgba(229, 143, 36, 0.15) !important;
  background-color: rgba(0, 0, 0, 0.5) !important;
}

.error-message {
  background-color: rgba(239, 68, 68, 0.15);
  color: #FCA5A5;
  padding: 12px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  border: 1px solid rgba(239, 68, 68, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  color: #FCA5A5 !important;
  flex-shrink: 0;
}

.submit-btn {
  background-color: var(--color-primary);
  color: #000000;
  border: none;
  border-radius: var(--radius-md);
  padding: 14px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(229, 143, 36, 0.2);
}

.submit-btn:hover {
  background-color: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(229, 143, 36, 0.4);
}

.submit-btn:active {
  transform: scale(0.98);
}

.submit-btn:disabled {
  background-color: var(--color-disabled-bg) !important;
  color: var(--color-disabled-text) !important;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
