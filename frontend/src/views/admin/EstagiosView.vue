<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Estágios do Funil</h1>
      <button class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Estágio</button>
    </div>

    <div class="card p-0 overflow-hidden">
      <div class="p-4 md:p-6 border-b border-gray-100 bg-gray-50/30">
        <p class="text-sm text-gray-500 font-medium">
          Configure os estágios do funil de vendas. Os estágios serão exibidos no Kanban na ordem definida.
        </p>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else class="divide-y divide-gray-100">
        <div
          v-for="estagio in estagios"
          :key="estagio.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between p-4 md:p-6 hover:bg-gray-50 transition-colors gap-4"
        >
          <div class="flex items-center space-x-4">
            <div 
              class="w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center text-white font-black shadow-sm"
              :style="{ backgroundColor: estagio.cor }"
            >
              {{ estagio.ordem }}
            </div>
            <div>
              <h3 class="font-bold text-gray-900">{{ estagio.nome }}</h3>
              <div class="flex flex-wrap gap-x-3 gap-y-1 mt-1">
                 <span class="text-[10px] font-bold uppercase text-primary-600 tracking-wider">
                   {{ getTipoLabel(estagio.tipo) }}
                 </span>
                 <span class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">
                   {{ estagio.total_oportunidades }} oportunidades
                 </span>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-end space-x-4 border-t sm:border-t-0 pt-3 sm:pt-0">
            <button class="flex items-center text-xs font-bold text-primary-600 uppercase tracking-widest hover:text-primary-700">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              Editar
            </button>
            <button class="flex items-center text-xs font-bold text-red-600 uppercase tracking-widest hover:text-red-700">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Excluir
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const estagios = ref([])
const loading = ref(false)

onMounted(() => {
  loadEstagios()
})

async function loadEstagios() {
  loading.value = true
  try {
    const response = await api.get('/estagios-funil/')
    estagios.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar estágios:', error)
  } finally {
    loading.value = false
  }
}

function getTipoLabel(tipo) {
  const labels = {
    'ABERTO': 'Aberto',
    'GANHO': 'Fechado - Ganho',
    'PERDIDO': 'Fechado - Perdido'
  }
  return labels[tipo] || tipo
}
</script>
