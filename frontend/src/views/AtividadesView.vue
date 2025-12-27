<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Atividades</h1>
      <button class="btn btn-primary w-full sm:w-auto shadow-sm">+ Nova Atividade</button>
    </div>

    <div class="card p-0 overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      
      <div v-else class="divide-y divide-gray-100">
        <div
          v-for="atividade in atividades"
          :key="atividade.id"
          class="flex flex-col sm:flex-row sm:items-start justify-between p-4 md:p-6 hover:bg-gray-50 transition-colors gap-4"
        >
          <div class="flex items-start space-x-4">
            <div :class="[getIconClass(atividade.tipo), 'flex-shrink-0']">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-gray-900 truncate">{{ atividade.titulo }}</h3>
              <p class="text-xs font-semibold text-primary-600 uppercase tracking-wider mb-1">{{ atividade.tipo }}</p>
              <p v-if="atividade.descricao" class="text-sm text-gray-600 line-clamp-2 md:line-clamp-none">{{ atividade.descricao }}</p>
              <div class="flex items-center mt-2 space-x-2 text-[10px] text-gray-400 font-medium">
                <span class="flex items-center">
                   <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                   {{ atividade.proprietario_nome }}
                </span>
                <span v-if="atividade.data_vencimento" class="sm:hidden flex items-center">
                   <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                   {{ formatDateTime(atividade.data_vencimento) }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex sm:flex-col items-center sm:items-end justify-between sm:justify-start gap-2 border-t sm:border-t-0 pt-3 sm:pt-0 mt-2 sm:mt-0">
            <span :class="getStatusClass(atividade.status)">
              {{ atividade.status }}
            </span>
            <p v-if="atividade.data_vencimento" class="hidden sm:block text-xs text-gray-400 font-medium mt-auto">
               Vence em: {{ formatDateTime(atividade.data_vencimento) }}
            </p>
          </div>
        </div>
      </div>
      
      <div v-if="atividades.length === 0 && !loading" class="text-center py-12 text-gray-500 italic">
        Nenhuma atividade planejada.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const atividades = ref([])
const loading = ref(false)

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

function getIconClass(tipo) {
  const classes = {
    'TAREFA': 'p-2 rounded-full bg-blue-100 text-blue-600',
    'LIGACAO': 'p-2 rounded-full bg-green-100 text-green-600',
    'REUNIAO': 'p-2 rounded-full bg-purple-100 text-purple-600',
    'EMAIL': 'p-2 rounded-full bg-yellow-100 text-yellow-600',
    'NOTA': 'p-2 rounded-full bg-gray-100 text-gray-600'
  }
  return classes[tipo] || 'p-2 rounded-full bg-gray-100 text-gray-600'
}

function getStatusClass(status) {
  const classes = {
    'Pendente': 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    'Concluída': 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
    'Cancelada': 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800'
  }
  return classes[status] || 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800'
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('pt-BR')
}
</script>
