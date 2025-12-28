<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Oportunidades</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Nova Oportunidade
      </button>
    </div>

    <!-- Filtro rápido -->
    <div class="card mb-6 p-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar por nome ou conta..."
        class="input"
        @input="onSearchInput"
      />
    </div>

    <!-- Indicadores (KPIs) -->
    <div v-if="!error" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 border-l-4" :style="{ borderLeftColor: kpi.color }">
        <div class="flex items-center justify-between mb-3">
          <div class="p-2 rounded-lg" :style="{ backgroundColor: kpi.color + '15' }">
            <component :is="kpi.icon" class="w-5 h-5" :style="{ color: kpi.color }" />
          </div>
          <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">{{ kpi.label }}</span>
        </div>
        <div>
          <div class="text-xl font-black text-gray-900 leading-none">
            {{ kpi.prefix }} {{ kpi.value }}
          </div>
          <div class="text-[10px] text-gray-500 mt-2 font-bold uppercase tracking-tight">
            {{ kpi.sub }}
          </div>
        </div>
      </div>
    </div>

    <div class="card overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="error" class="p-6 text-center">
        <div class="text-red-500 font-bold mb-2 flex items-center justify-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          Erro ao carregar dados
        </div>
        <p class="text-gray-600 text-sm">{{ error }}</p>
        <button @click="loadOportunidades" class="mt-4 text-primary-600 font-bold hover:underline">Tentar novamente</button>
      </div>

      <div v-else>
        <!-- Desktop Table -->
        <div class="hidden md:block overflow-x-auto">
          <table class="table">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">Nome</th>
                <th class="table-header">Conta</th>
                <th class="table-header">Valor</th>
                <th class="table-header">Estágio</th>
                <th class="table-header">Previsão</th>
                <th class="table-header">Probabilidade</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="oportunidade in oportunidades" :key="oportunidade.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900">{{ oportunidade.nome }}</td>
                <td class="table-cell text-gray-500">{{ oportunidade.conta_nome }}</td>
                <td class="table-cell font-semibold text-green-600">
                  R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </td>
                <td class="table-cell">
                  <span class="px-2 py-1 text-xs rounded-full font-medium" :style="{ backgroundColor: oportunidade.estagio_cor + '20', color: oportunidade.estagio_cor }">
                    {{ oportunidade.estagio_nome }}
                  </span>
                </td>
                <td class="table-cell text-gray-500">{{ formatDate(oportunidade.data_fechamento_esperada) }}</td>
                <td class="table-cell text-gray-500">{{ oportunidade.probabilidade }}%</td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button @click="openFaturamentoModal(oportunidade)" class="text-emerald-600 hover:text-emerald-700 font-medium" title="Configurar Faturamento">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </button>
                    <button @click="openEditModal(oportunidade)" class="text-primary-600 hover:text-primary-700 font-medium" title="Editar">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click="deleteOportunidade(oportunidade.id)" class="text-red-600 hover:text-red-700 font-medium" title="Excluir">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="oportunidade in oportunidades" :key="oportunidade.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="flex justify-between items-start mb-2">
               <div @click="openEditModal(oportunidade)" class="cursor-pointer">
                  <h3 class="font-bold text-gray-900">{{ oportunidade.nome }}</h3>
                  <p class="text-sm text-gray-500">{{ oportunidade.conta_nome }}</p>
               </div>
               <span class="px-2 py-1 text-[10px] font-bold uppercase rounded-full" :style="{ backgroundColor: oportunidade.estagio_cor + '20', color: oportunidade.estagio_cor }">
                  {{ oportunidade.estagio_nome }}
               </span>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mt-3 pt-3 border-t border-gray-50 cursor-pointer" @click="openEditModal(oportunidade)">
               <div>
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Valor Mensal</p>
                  <p class="text-sm font-bold text-green-600">R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR') }}</p>
               </div>
               <div class="text-right">
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Probabilidade</p>
                  <p class="text-sm font-bold text-gray-700">{{ oportunidade.probabilidade }}%</p>
               </div>
            </div>

            <div class="flex justify-end space-x-4 border-t pt-3 mt-4">
              <button 
                @click="openFaturamentoModal(oportunidade)" 
                class="text-xs font-bold text-emerald-600 uppercase tracking-widest flex items-center"
              >
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                 Faturamento
              </button>
              <button @click="openEditModal(oportunidade)" class="text-xs font-bold text-primary-600 uppercase tracking-widest flex items-center">
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                 Editar
              </button>
              <button @click="deleteOportunidade(oportunidade.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest flex items-center">
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                 Excluir
              </button>
            </div>
          </div>
        </div>

        <div v-if="oportunidades.length === 0" class="text-center py-12 text-gray-500">
          Nenhuma oportunidade registrada.
        </div>
      </div>
    </div>

    <!-- Modais -->
    <OportunidadeModal
      :show="showModal"
      :oportunidade="selectedOportunidade"
      @close="closeModal"
      @saved="loadOportunidades"
    />

    <FaturamentoModal
      :show="showFaturamentoModal"
      :oportunidade="selectedOportunidade"
      @close="closeFaturamentoModal"
      @saved="loadOportunidades"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import OportunidadeModal from '@/components/OportunidadeModal.vue'
import FaturamentoModal from '@/components/FaturamentoModal.vue'

// Ícones simples
const IconPipeline = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>' }
const IconWin = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }
const IconTicket = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }
const IconTotal = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>' }

const oportunidades = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const showModal = ref(false)
const showFaturamentoModal = ref(false)
const selectedOportunidade = ref(null)

const stats = ref({
  total_valor: 0,
  total_contagem: 0,
  valor_medio: 0,
  valor_ganho: 0,
  valor_aberto: 0,
  contagem_aberta: 0,
  contagem_ganha: 0
})

const kpiCards = computed(() => [
  { 
    label: 'Pipeline Aberto', 
    value: formatCurrency(stats.value.valor_aberto), 
    prefix: 'R$', 
    sub: `${stats.value.contagem_aberta} oportunidades ativas`, 
    icon: IconPipeline, 
    color: '#3B82F6' 
  },
  { 
    label: 'Vendas Ganhas', 
    value: formatCurrency(stats.value.valor_ganho), 
    prefix: 'R$', 
    sub: `${stats.value.contagem_ganha} negócios fechados`, 
    icon: IconWin, 
    color: '#10B981' 
  },
  { 
    label: 'Ticket Médio', 
    value: formatCurrency(stats.value.valor_medio), 
    prefix: 'R$', 
    sub: 'Valor médio por card', 
    icon: IconTicket, 
    color: '#F59E0B' 
  },
  { 
    label: 'Potencial Total', 
    value: formatCurrency(stats.value.total_valor), 
    prefix: 'R$', 
    sub: `${stats.value.total_contagem} cards no total`, 
    icon: IconTotal, 
    color: '#6366F1' 
  }
])

function formatCurrency(val) {
  return Number(val || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(() => {
  loadOportunidades()
})

async function loadOportunidades() {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    // Busca lista e stats em paralelo
    const [listRes, statsRes] = await Promise.all([
      api.get('/oportunidades/', { params }),
      api.get('/oportunidades/stats/', { params })
    ])
    
    oportunidades.value = listRes.data.results || listRes.data
    stats.value = statsRes.data
  } catch (err) {
    console.error('Erro ao carregar oportunidades:', err)
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
function onSearchInput() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadOportunidades()
  }, 500)
}

function openCreateModal() {
  selectedOportunidade.value = null
  showModal.value = true
}

function openEditModal(oportunidade) {
  selectedOportunidade.value = oportunidade
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedOportunidade.value = null
}

function openFaturamentoModal(oportunidade) {
  selectedOportunidade.value = oportunidade
  showFaturamentoModal.value = true
}

function closeFaturamentoModal() {
  showFaturamentoModal.value = false
  selectedOportunidade.value = null
}

async function copyBillingInfo(id) {
  try {
    const response = await api.get(`/oportunidades/${id}/gerar_texto_faturamento/`)
    const texto = response.data.texto
    
    await navigator.clipboard.writeText(texto)
    alert('Texto de faturamento copiado para a área de transferência! 📋')
  } catch (error) {
    console.error('Erro ao gerar texto:', error)
    alert('Erro ao gerar texto de faturamento. Verifique se o plano está selecionado.')
  }
}

async function deleteOportunidade(id) {
  if (!confirm('Tem certeza que deseja excluir esta oportunidade?')) return
  
  try {
    await api.delete(`/oportunidades/${id}/`)
    await loadOportunidades()
  } catch (error) {
    console.error('Erro ao excluir oportunidade:', error)
    alert('Erro ao excluir oportunidade')
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}
</script>
