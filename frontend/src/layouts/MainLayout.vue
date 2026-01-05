<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Mobile Header -->
    <header class="lg:hidden bg-white border-b px-4 py-3 flex items-center justify-between sticky top-0 z-40 shadow-sm">
      <h1 class="text-xl font-bold text-primary-600">CRM Vendas</h1>
      <button @click="toggleSidebar" class="p-2 rounded-md hover:bg-gray-100 text-gray-600">
        <svg v-if="!isSidebarOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </header>

    <!-- Sidebar Overlay (Mobile only) -->
    <div 
      v-if="isSidebarOpen" 
      @click="closeSidebar"
      class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-40 lg:hidden transition-opacity"
    ></div>

    <!-- Sidebar -->
    <aside 
      :class="[
        'fixed inset-y-0 left-0 w-64 bg-white shadow-lg z-50 transition-transform duration-300 lg:translate-x-0',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="p-6 border-b flex items-center justify-between lg:block">
          <div>
            <h1 class="text-2xl font-bold text-primary-600">CRM Vendas</h1>
            <p class="text-sm text-gray-500 mt-1 leading-tight">{{ user?.get_full_name || user?.username }}</p>
            <span class="inline-block mt-1 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-full bg-primary-100 text-primary-800">
              {{ user?.perfil }}
            </span>
          </div>
          <button @click="closeSidebar" class="lg:hidden p-2 text-gray-400 hover:text-gray-600">
             <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          <router-link
            @click="closeSidebar"
            to="/dashboard"
            class="nav-link"
            active-class="nav-link-active"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span>Dashboard</span>
          </router-link>

          <router-link
            @click="closeSidebar"
            to="/kanban"
            class="nav-link"
            active-class="nav-link-active"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
            </svg>
            <span>Kanban</span>
          </router-link>

          <router-link @click="closeSidebar" to="/leads" class="nav-link" active-class="nav-link-active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span class="flex-1">Leads</span>
            <span 
              v-if="whatsappUnread.leads > 0" 
              class="flex items-center justify-center min-w-[20px] h-5 px-1 bg-emerald-500 text-white text-[10px] font-black rounded-full shadow-sm"
              title="Mensagens não lidas de Leads"
            >
              {{ whatsappUnread.leads }}
            </span>
          </router-link>

          <router-link @click="closeSidebar" to="/contas" class="nav-link" active-class="nav-link-active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span>Contas/Empresas</span>
          </router-link>

          <router-link @click="closeSidebar" to="/contatos" class="nav-link" active-class="nav-link-active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Contatos</span>
          </router-link>

          <router-link @click="closeSidebar" to="/oportunidades" class="nav-link" active-class="nav-link-active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="flex-1">Oportunidades</span>
            <span 
              v-if="whatsappUnread.oportunidades > 0" 
              class="flex items-center justify-center min-w-[20px] h-5 px-1 bg-emerald-500 text-white text-[10px] font-black rounded-full shadow-sm"
              title="Mensagens não lidas de Oportunidades"
            >
              {{ whatsappUnread.oportunidades }}
            </span>
          </router-link>

          <router-link @click="closeSidebar" to="/atividades" class="nav-link" active-class="nav-link-active">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span class="flex-1">Atividades</span>
            <span 
              v-if="atrasadasCount > 0" 
              class="flex items-center justify-center w-5 h-5 bg-red-500 text-white text-[10px] font-black rounded-full animate-bounce shadow-sm"
              title="Atividades Atrasadas"
            >
              {{ atrasadasCount }}
            </span>
          </router-link>

          <!-- Admin Section -->
          <div v-if="isAdmin" class="pt-4 mt-4 border-t border-gray-100">
            <p class="px-3 text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">
              Administração
            </p>
            <router-link @click="closeSidebar" to="/config/usuarios" class="nav-link" active-class="nav-link-active">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <span>Usuários</span>
            </router-link>

            <router-link @click="closeSidebar" to="/config/funis" class="nav-link" active-class="nav-link-active">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span>Funis</span>
            </router-link>

            <router-link @click="closeSidebar" to="/config/canais" class="nav-link" active-class="nav-link-active">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span>Canais</span>
            </router-link>

            <router-link @click="closeSidebar" to="/config/estagios" class="nav-link" active-class="nav-link-active">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              <span>Estágios</span>
            </router-link>

            <router-link @click="closeSidebar" to="/config/tipos-contato" class="nav-link" active-class="nav-link-active">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span>Tipos de Contatos</span>
            </router-link>

            <router-link @click="closeSidebar" to="/config/planos" class="nav-link" active-class="nav-link-active">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-10-10l-10 10m16 0l-10 10l-10-10" />
              </svg>
              <span>Planos de Venda</span>
            </router-link>

            <router-link @click="closeSidebar" to="/config/whatsapp" class="nav-link" active-class="nav-link-active">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/>
              </svg>
              <span class="flex-1">WhatsApp</span>
              <span 
                v-if="whatsappUnread.total > 0" 
                class="flex items-center justify-center min-w-[20px] h-5 px-1 bg-emerald-500 text-white text-[10px] font-black rounded-full shadow-sm"
                title="Total de mensagens não lidas"
              >
                {{ whatsappUnread.total }}
              </span>
            </router-link>
          </div>
        </nav>

        <!-- Logout -->
        <div class="p-4 border-t border-gray-100 bg-gray-50/50">
          <button @click="handleLogout" class="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl text-sm font-semibold text-gray-700 hover:bg-red-50 hover:text-red-700 transition-all duration-200 border border-transparent hover:border-red-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span>Sair do Sistema</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="lg:ml-64 min-h-screen transition-all duration-300">
      <div class="p-4 md:p-8 max-w-7xl mx-auto">
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

const atrasadasCount = ref(0)
const whatsappUnread = computed(() => whatsappStore.unreadCounts)

onMounted(() => {
  fetchAtividadesStats()
  if (authStore.isAuthenticated) {
    whatsappStore.fetchUnreadCounts()
  }
  
  // Atualizações automáticas
  setInterval(() => {
    if (authStore.isAuthenticated) {
      fetchAtividadesStats()
    }
  }, 5 * 60 * 1000)

  setInterval(() => {
    if (authStore.isAuthenticated) {
      whatsappStore.fetchUnreadCounts()
    }
  }, 30 * 1000) // Aumentado para cada 30 segundos
})

async function fetchAtividadesStats() {
  if (!authStore.isAuthenticated) return
  try {
    const response = await api.get('/atividades/stats/')
    atrasadasCount.value = response.data.atrasadas
  } catch (error) {
    console.error('Erro ao buscar stats de atividades:', error)
  }
}

// Removida função fetchWhatsappUnread pois agora está na store

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value
}

function closeSidebar() {
  isSidebarOpen.value = false
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-link {
  @apply flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-600 hover:bg-gray-100 hover:text-primary-600 transition-all duration-200 font-medium whitespace-nowrap;
}

.nav-link-active {
  @apply bg-primary-600 text-white shadow-md shadow-primary-200 hover:bg-primary-700 hover:text-white;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-gray-200 rounded-full;
}
</style>
