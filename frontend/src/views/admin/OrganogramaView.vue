<template>
  <div class="p-6">
    <!-- Cabeçalho -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Organograma</h1>
      <p class="text-sm text-gray-600 mt-1">Estrutura hierárquica da equipe de vendas</p>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow-sm p-4 border-l-4 border-blue-500">
        <p class="text-sm font-medium text-gray-500">Canais</p>
        <p class="text-2xl font-bold text-gray-900">{{ estatisticas.total_canais }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 border-l-4 border-purple-500">
        <p class="text-sm font-medium text-gray-500">Responsáveis</p>
        <p class="text-2xl font-bold text-gray-900">{{ estatisticas.total_responsaveis }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 border-l-4 border-green-500">
        <p class="text-sm font-medium text-gray-500">Vendedores</p>
        <p class="text-2xl font-bold text-gray-900">{{ estatisticas.total_vendedores }}</p>
      </div>
    </div>

    <!-- Organograma -->
    <div class="bg-white rounded-lg shadow-sm p-6 overflow-auto relative">
      <!-- Loading Overlay -->
      <div v-if="loading" class="absolute inset-0 bg-white/80 flex justify-center items-center z-10">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
      
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-800">Diagrama Hierárquico</h2>
        <div class="flex gap-2">
          <button 
            @click="zoomIn" 
            class="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            title="Aumentar zoom"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/>
            </svg>
          </button>
          <button 
            @click="zoomOut" 
            class="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            title="Diminuir zoom"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"/>
            </svg>
          </button>
          <button 
            @click="resetZoom" 
            class="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            title="Resetar zoom"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
          <button 
            @click="recarregar" 
            class="p-2 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-lg transition-colors"
            title="Recarregar"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Container do diagrama SVG -->
      <div 
        class="svg-container border border-gray-200 rounded-lg bg-gradient-to-br from-gray-50 to-white p-8 min-h-[400px] flex justify-center items-center overflow-auto"
        :style="{ transform: `scale(${zoom})`, transformOrigin: 'top center' }"
      >
        <!-- SVG gerado pelo backend -->
        <div v-html="svgCode" v-if="svgCode && !loading" class="w-full"></div>
        <p v-if="!svgCode && !loading" class="text-gray-400">Nenhum dado para exibir</p>
      </div>
    </div>

    <!-- Legenda -->
    <div class="mt-6 bg-white rounded-lg shadow-sm p-4">
      <h3 class="text-sm font-semibold text-gray-700 mb-3">Legenda</h3>
      <div class="flex flex-wrap gap-4">
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded" style="background: #1e40af"></div>
          <span class="text-sm text-gray-600">Administrador</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded" style="background: #059669"></div>
          <span class="text-sm text-gray-600">Canal (Responsável)</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded border border-gray-400" style="background: #f3f4f6"></div>
          <span class="text-sm text-gray-600">Vendedor</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { sanitizeSvg } from '@/utils/sanitize'

const loading = ref(false)
const svgCode = ref('')
const zoom = ref(1)
const estatisticas = ref({
  total_canais: 0,
  total_responsaveis: 0,
  total_vendedores: 0
})

onMounted(() => {
  carregarOrganograma()
})

async function carregarOrganograma() {
  loading.value = true
  try {
    const response = await api.get('/organograma/')
    console.log('Dados recebidos:', response.data)
    svgCode.value = sanitizeSvg(response.data.svg)
    estatisticas.value = response.data.estatisticas
  } catch (error) {
    console.error('Erro ao carregar organograma:', error)
  } finally {
    loading.value = false
  }
}

function zoomIn() {
  zoom.value = Math.min(zoom.value + 0.1, 2)
}

function zoomOut() {
  zoom.value = Math.max(zoom.value - 0.1, 0.5)
}

function resetZoom() {
  zoom.value = 1
}

function recarregar() {
  carregarOrganograma()
}
</script>

<style scoped>
.svg-container {
  transition: transform 0.2s ease;
}

.svg-container :deep(svg) {
  max-width: 100%;
  height: auto;
}
</style>
