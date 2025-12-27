<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Atividades</h1>
      <button 
        @click="openCreateModal"
        class="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 transition-all shadow-sm hover:shadow-md"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nova Atividade
      </button>
    </div>

    <!-- Filtros Rápidos -->
    <div class="flex flex-wrap gap-2">
      <button 
        v-for="status in ['Todas', 'Pendente', 'Concluída', 'Cancelada']" 
        :key="status"
        @click="filterStatus = status"
        :class="[
          'px-4 py-1.5 rounded-full text-xs font-bold transition-all border',
          filterStatus === status 
            ? 'bg-primary-600 text-white border-primary-600 shadow-sm' 
            : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300'
        ]"
      >
        {{ status }}
      </button>
    </div>

    <div class="card p-0 overflow-hidden shadow-sm border border-gray-100">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-500">Carregando atividades...</p>
      </div>
      
      <div v-else class="divide-y divide-gray-100">
        <div
          v-for="atividade in filteredAtividades"
          :key="atividade.id"
          class="group flex flex-col sm:flex-row sm:items-center justify-between p-4 md:p-6 hover:bg-gray-50 transition-colors gap-4"
        >
          <div class="flex items-start space-x-4 flex-1">
            <div :class="[getIconClass(atividade.tipo), 'flex-shrink-0 mt-1']">
              <!-- Ícone dinâmico baseado no tipo -->
              <svg v-if="atividade.tipo === 'TAREFA'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
              <svg v-else-if="atividade.tipo === 'LIGACAO'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
              <svg v-else-if="atividade.tipo === 'REUNIAO'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
              <svg v-else-if="atividade.tipo === 'EMAIL'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 012-2V7a2 2 0 01-2-2H5a2 2 0 01-2 2v10a2 2 0 012 2z" /></svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h3 class="font-bold text-gray-900 truncate">{{ atividade.titulo }}</h3>
                <span :class="getStatusClass(atividade.status)">
                  {{ atividade.status }}
                </span>
              </div>
              <p class="text-[10px] font-bold text-primary-600 uppercase tracking-widest mt-0.5">{{ atividade.tipo }}</p>
              
              <p v-if="atividade.descricao" class="text-sm text-gray-600 mt-2 line-clamp-2 md:line-clamp-none">
                {{ atividade.descricao }}
              </p>
              
              <div class="flex flex-wrap items-center mt-3 gap-y-2 gap-x-4 text-[11px] text-gray-400 font-medium">
                <span class="flex items-center">
                   <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                   {{ atividade.proprietario_nome }}
                </span>
                <span v-if="atividade.data_vencimento" class="flex items-center" :class="{'text-red-500 font-bold': isOverdue(atividade)}">
                   <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                   Vence: {{ formatDateTime(atividade.data_vencimento) }}
                </span>
                <span v-if="atividade.data_conclusao" class="flex items-center text-green-600">
                   <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                   Concluída em: {{ formatDateTime(atividade.data_conclusao) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Ações -->
          <div class="flex items-center gap-2 sm:opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              v-if="atividade.status === 'Pendente'"
              @click="handleConcluir(atividade)"
              class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="Marcar como concluída"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            </button>
            <button 
              @click="openEditModal(atividade)"
              class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Editar"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
            </button>
            <button 
              @click="handleDelete(atividade)"
              class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Excluir"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="filteredAtividades.length === 0 && !loading" class="text-center py-12">
        <div class="bg-gray-50 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
        </div>
        <p class="text-gray-500 font-mediumitalic">Nenhuma atividade encontrada.</p>
      </div>
    </div>

    <!-- Modal de Atividade -->
    <AtividadeModal
      :show="showModal"
      :atividade="selectedAtividade"
      @close="showModal = false"
      @saved="loadAtividades"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import AtividadeModal from '@/components/AtividadeModal.vue'

const atividades = ref([])
const loading = ref(false)
const filterStatus = ref('Todas')

// Modal state
const showModal = ref(false)
const selectedAtividade = ref(null)

const filteredAtividades = computed(() => {
  if (filterStatus.value === 'Todas') return atividades.value
  return atividades.value.filter(a => a.status === filterStatus.value)
})

onMounted(() => {
  loadAtividades()
})

async function loadAtividades() {
  loading.value = true
  try {
    const response = await api.get('/atividades/')
    atividades.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar atividades:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedAtividade.value = null
  showModal.value = true
}

function openEditModal(atividade) {
  selectedAtividade.value = { ...atividade }
  showModal.value = true
}

async function handleConcluir(atividade) {
  try {
    await api.post(`/atividades/${atividade.id}/concluir/`)
    await loadAtividades()
  } catch (error) {
    console.error('Erro ao concluir atividade:', error)
    alert('Erro ao concluir atividade.')
  }
}

async function handleDelete(atividade) {
  if (!confirm(`Tem certeza que deseja excluir a atividade "${atividade.titulo}"?`)) return
  
  try {
    await api.delete(`/atividades/${atividade.id}/`)
    await loadAtividades()
  } catch (error) {
    console.error('Erro ao excluir atividade:', error)
    alert('Erro ao excluir atividade.')
  }
}

function isOverdue(atividade) {
  if (atividade.status !== 'Pendente' || !atividade.data_vencimento) return false
  return new Date(atividade.data_vencimento) < new Date()
}

function getIconClass(tipo) {
  const classes = {
    'TAREFA': 'p-2 rounded-xl bg-blue-50 text-blue-600',
    'LIGACAO': 'p-2 rounded-xl bg-emerald-50 text-emerald-600',
    'REUNIAO': 'p-2 rounded-xl bg-violet-50 text-violet-600',
    'EMAIL': 'p-2 rounded-xl bg-amber-50 text-amber-600',
    'NOTA': 'p-2 rounded-xl bg-gray-50 text-gray-600'
  }
  return classes[tipo] || 'p-2 rounded-xl bg-gray-50 text-gray-600'
}

function getStatusClass(status) {
  const classes = {
    'Pendente': 'px-2 py-0.5 text-[10px] font-black rounded-full bg-amber-100 text-amber-700 uppercase',
    'Concluída': 'px-2 py-0.5 text-[10px] font-black rounded-full bg-emerald-100 text-emerald-700 uppercase',
    'Cancelada': 'px-2 py-0.5 text-[10px] font-black rounded-full bg-rose-100 text-rose-700 uppercase'
  }
  return classes[status] || 'px-2 py-0.5 text-[10px] font-black rounded-full bg-gray-100 text-gray-700 uppercase'
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}
</script>
