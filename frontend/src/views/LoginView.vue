<template>
  <div 
    class="min-h-screen flex items-center justify-center bg-cover bg-center transition-all duration-1000 relative overflow-hidden"
    :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <!-- Overlay gradiente para garantir legibilidade -->
    <div class="absolute inset-0 bg-gradient-to-br from-zinc-900/60 via-zinc-900/40 to-primary-900/60 backdrop-blur-[2px]"></div>

    <!-- Conteúdo do Login -->
    <div class="glass-card p-10 rounded-3xl shadow-2xl w-full max-w-md relative z-10 border border-white/20 animate-in fade-in zoom-in duration-500">
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl mb-4 border border-white/20 shadow-xl">
          <span class="text-3xl font-display font-bold text-white">C</span>
        </div>
        <h1 class="text-4xl font-display font-bold text-white tracking-tight">CRM de Vendas</h1>
        <p class="text-white/70 mt-3 font-medium">Faça login para gerenciar seus negócios</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="username" class="block text-xs font-bold text-white uppercase tracking-widest mb-2 ml-1">
            Usuário
          </label>
          <div class="relative group">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 group-focus-within:text-white transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            </span>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              class="w-full bg-white/10 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:bg-white/20 focus:border-white/30 focus:ring-0 transition-all outline-none"
              placeholder="Seu usuário"
            />
          </div>
        </div>

        <div>
          <label for="password" class="block text-xs font-bold text-white uppercase tracking-widest mb-2 ml-1">
            Senha
          </label>
          <div class="relative group">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 group-focus-within:text-white transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
            </span>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="w-full bg-white/10 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:bg-white/20 focus:border-white/30 focus:ring-0 transition-all outline-none"
              placeholder="Sua senha"
            />
          </div>
        </div>

        <div v-if="error" class="bg-red-500/20 border border-red-500/30 text-red-200 p-4 rounded-2xl text-sm font-medium animate-in slide-in-from-top-2">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-white text-zinc-900 hover:bg-zinc-100 disabled:opacity-50 py-4 rounded-2xl text-lg font-bold transition-all shadow-xl shadow-white/10 flex items-center justify-center gap-3 active:scale-[0.98]"
        >
          <template v-if="!loading">
            Entrar no Sistema
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
          </template>
          <template v-else>
            <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Validando acesso...
          </template>
        </button>
      </form>
    </div>

    <!-- Rodapé -->
    <div class="absolute bottom-6 text-center z-10">
      <p class="text-white/40 text-xs font-bold tracking-widest uppercase">CRM Vendas & Pós Vendas &copy; 2026 • Developed by Rogaciano</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const backgroundImage = ref('')

onMounted(() => {
  // Escolhe uma foto aleatória entre foto1.jpeg e foto11.jpeg
  const randomNum = Math.floor(Math.random() * 11) + 1
  const baseUrl = (import.meta.env.VITE_API_URL || '').replace('/api', '')
  backgroundImage.value = `${baseUrl}/media/fundos/foto${randomNum}.jpeg`
})

async function handleLogin() {
  loading.value = true
  error.value = ''

  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Usuário ou senha inválidos'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

.font-display {
  font-family: 'Outfit', 'Inter', sans-serif;
}
</style>
