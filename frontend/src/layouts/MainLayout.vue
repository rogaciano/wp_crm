<template>
  <div class="min-h-screen bg-zinc-50 flex font-sans">
    <!-- Mobile Header -->
    <header class="lg:hidden fixed top-0 left-0 right-0 bg-white border-b border-zinc-200 px-4 py-3 flex items-center justify-between z-40">
      <h1 class="text-lg font-bold font-display tracking-tight text-zinc-900">CRM Vendas</h1>
      <button @click="toggleSidebar" class="p-2 -mr-2 text-zinc-600 hover:bg-zinc-100 rounded-md">
        <svg v-if="!isSidebarOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </header>

    <!-- Sidebar Overlay -->
    <div 
      v-if="isSidebarOpen" 
      @click="closeSidebar"
      class="fixed inset-0 bg-zinc-900/80 backdrop-blur-sm z-40 lg:hidden transition-opacity"
    ></div>

    <!-- Sidebar -->
    <aside 
      :class="[
        'fixed lg:sticky top-0 h-screen w-72 bg-zinc-900 border-r border-zinc-800 z-50 transition-transform duration-300 flex flex-col',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Brand & User Profile -->
      <div class="p-6 border-b border-zinc-800">
        <div class="flex items-center gap-4 mb-6">
          <div class="h-10 w-10 bg-primary-600 rounded-md flex items-center justify-center text-white font-display font-bold text-xl shadow-lg shadow-primary-900/20">
            C
          </div>
          <div>
            <h1 class="text-white font-display font-bold text-lg leading-none tracking-tight">CRM Vendas</h1>
            <span class="text-xs text-zinc-500 font-medium tracking-wide">Enterprise Edition</span>
          </div>
        </div>

        <!-- User Card -->
        <div class="flex items-center gap-3 bg-zinc-800/50 p-3 rounded-md border border-zinc-700/50">
          <img 
            v-if="user?.avatar_url" 
            :src="user.avatar_url" 
            class="w-10 h-10 rounded-md object-cover bg-zinc-800"
          />
          <div 
            v-else 
            class="w-10 h-10 rounded-md bg-zinc-700 flex items-center justify-center text-zinc-300 font-bold text-sm"
          >
            {{ userInitials }}
          </div>
          
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-zinc-100 truncate">{{ user?.full_name || 'Usuário' }}</p>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              <p class="text-xs text-zinc-400 truncate">{{ user?.perfil || 'Membro' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto px-4 py-6 space-y-1">
        <p class="px-2 text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2">Principal</p>
        
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
          <span>Dashboard</span>
        </router-link>

        <router-link to="/kanban" class="nav-item" active-class="active">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" /></svg>
          <span>Kanban</span>
        </router-link>

        <router-link to="/contas" class="nav-item" active-class="active">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
          <span>Empresas</span>
        </router-link>

        <router-link to="/contatos" class="nav-item" active-class="active">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
          <span>Contatos</span>
        </router-link>

        <router-link to="/oportunidades" class="nav-item" active-class="active">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <div class="flex-1 flex justify-between items-center">
            <span>Oportunidades</span>
            <span v-if="whatsappUnread.oportunidades > 0" class="px-1.5 py-0.5 rounded-sm bg-primary-600 text-white text-[10px] font-bold">{{ whatsappUnread.oportunidades }}</span>
          </div>
        </router-link>

        <router-link to="/atividades" class="nav-item" active-class="active">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
          <div class="flex-1 flex justify-between items-center">
            <span>Atividades</span>
            <span v-if="atrasadasCount > 0" class="px-1.5 py-0.5 rounded-sm bg-rose-500 text-white text-[10px] font-bold animate-pulse">{{ atrasadasCount }}</span>
          </div>
        </router-link>

        <!-- Gestor Only -->
        <div v-if="isGestor" class="pt-6">
          <p class="px-2 text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2">Gestão</p>
          <router-link to="/meu-canal/whatsapp" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
            <span>WhatsApp Canal</span>
          </router-link>
        </div>

        <!-- Admin Only -->
        <div v-if="isAdmin" class="pt-6">
          <p class="px-2 text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2">Administração</p>
          
          <router-link to="/config/usuarios" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
            <span>Usuários</span>
          </router-link>

          <router-link to="/config/funis" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
            <span>Funis</span>
          </router-link>

          <router-link to="/config/canais" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
            <span>Canais</span>
          </router-link>

          <router-link to="/config/estagios" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>
            <span>Estágios</span>
          </router-link>

          <router-link to="/config/tipos-contato" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>
            <span>Tipos de Contatos</span>
          </router-link>

          <router-link to="/config/planos" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
            <span>Planos de Venda</span>
          </router-link>

          <router-link to="/config/whatsapp" class="nav-item" active-class="active">
             <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
              <div class="flex-1 flex justify-between items-center">
                <span>WhatsApp Config</span>
                <span v-if="whatsappUnread.total > 0" class="px-1.5 py-0.5 rounded-sm bg-emerald-600 text-white text-[10px] font-bold">{{ whatsappUnread.total }}</span>
              </div>
          </router-link>

          <router-link to="/config/logs" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            <span>Logs de Auditoria</span>
          </router-link>

          <router-link to="/config/organograma" class="nav-item" active-class="active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            <span>Organograma</span>
          </router-link>
        </div>
      </nav>

      <!-- Logout -->
      <div class="p-4 border-t border-zinc-800 bg-zinc-900">
        <button @click="handleLogout" class="w-full flex items-center gap-3 px-4 py-2 text-sm font-medium text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md transition-colors group">
          <svg class="w-5 h-5 text-zinc-500 group-hover:text-red-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
          <span>Sair da conta</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 min-h-screen transition-all duration-300 pt-16 lg:pt-0 overflow-visible">
      <div class="p-4 lg:p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWhatsappStore } from '@/stores/whatsapp'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const whatsappStore = useWhatsappStore()

const isSidebarOpen = ref(false)

const user = computed(() => authStore.user)
const isAdmin = computed(() => authStore.isAdmin)
const isGestor = computed(() => user.value?.perfil === 'RESPONSAVEL')

const userInitials = computed(() => {
  if (!user.value) return '?'
  const fullName = user.value.full_name || user.value.first_name || user.value.username || ''
  const parts = fullName.trim().split(' ').filter(p => p.length > 0)
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  return (fullName[0] || '?').toUpperCase()
})

const atrasadasCount = ref(0)
const whatsappUnread = computed(() => whatsappStore.unreadCounts)

onMounted(() => {
  fetchAtividadesStats()
  if (authStore.isAuthenticated) whatsappStore.fetchUnreadCounts()
  
  setInterval(() => {
    if (authStore.isAuthenticated) fetchAtividadesStats()
  }, 5 * 60 * 1000)

  setInterval(() => {
    if (authStore.isAuthenticated) whatsappStore.fetchUnreadCounts()
  }, 30 * 1000)
})

async function fetchAtividadesStats() {
  if (!authStore.isAuthenticated) return
  try {
    const response = await api.get('/atividades/stats/')
    atrasadasCount.value = response.data.atrasadas
  } catch (error) {
    console.error('Erro ao buscar stats:', error)
  }
}

function toggleSidebar() { isSidebarOpen.value = !isSidebarOpen.value }
function closeSidebar() { isSidebarOpen.value = false }
function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-item {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium text-zinc-400 hover:text-white hover:bg-zinc-800 transition-all duration-200 border border-transparent;
}

.nav-item.active {
  @apply bg-zinc-800 text-white border-zinc-700/50 shadow-sm;
}

.nav-item.active svg {
  @apply text-primary-500;
}
</style>
