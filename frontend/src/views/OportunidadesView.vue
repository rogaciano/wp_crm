<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Oportunidades</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Nova Oportunidade
      </button>
    </div>

    <!-- Filtros -->
    <div class="card mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar nome ou conta..."
          class="input"
          @input="onSearchInput"
        />
        <select v-model="funilFilter" class="input" @change="loadOportunidades">
          <option value="">Todos os Funis</option>
          <option v-for="f in funisOptions" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
        <select v-model="statusFilter" class="input" @change="loadOportunidades">
          <option value="ABERTO">Abertas (Ativas)</option>
          <option value="GANHO">Ganhos (Clientes)</option>
          <option value="PERDIDO">Perdidos</option>
          <option value="">Todos os Status</option>
        </select>
        <select v-if="authStore.isAdmin" v-model="canalFilter" class="input" @change="loadOportunidades">
          <option value="">Todos os Canais</option>
          <option v-for="c in canaisOptions" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
        <div v-else></div> <!-- Spacer -->
      </div>
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
          <table class="table min-w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">Nome</th>
                <th class="table-header">Conta</th>
                <th class="table-header text-right">Valor</th>
                <th class="table-header text-center">Estágio</th>
                <th class="table-header text-center">Previsão</th>
                <th class="table-header text-center">Prob.</th>
                <th class="table-header text-center sticky right-0 bg-gray-50">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="oportunidade in oportunidades" :key="oportunidade.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900 max-w-[200px] truncate" :title="oportunidade.nome">
                  {{ oportunidade.nome }}
                </td>
                <td class="table-cell text-gray-500 max-w-[180px] truncate" :title="oportunidade.conta_nome">
                  {{ oportunidade.conta_nome }}
                </td>
                <td class="table-cell text-right font-semibold text-green-600 whitespace-nowrap">
                  R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </td>
                <td class="table-cell text-center">
                  <span class="px-2 py-1 text-xs rounded-full font-medium whitespace-nowrap" :style="{ backgroundColor: oportunidade.estagio_cor + '20', color: oportunidade.estagio_cor }">
                    {{ oportunidade.estagio_nome }}
                  </span>
                </td>
                <td class="table-cell text-center text-gray-500 whitespace-nowrap">{{ formatDate(oportunidade.data_fechamento_esperada) }}</td>
                <td class="table-cell text-center text-gray-500">{{ oportunidade.probabilidade }}%</td>
                <td class="table-cell sticky right-0 bg-white">
                  <div class="flex justify-center items-center gap-1">
                    <button @click="openWhatsapp(oportunidade)" class="p-1.5 text-emerald-500 hover:bg-emerald-50 rounded-lg" title="WhatsApp">
                       <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
                    </button>
                    <button @click="openFaturamentoModal(oportunidade)" class="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg" title="Faturamento">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </button>
                    <button v-if="oportunidade.plano" @click="openPropostaPreview(oportunidade.id)" class="p-1.5 text-purple-600 hover:bg-purple-50 rounded-lg" title="Proposta">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1.01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </button>
                    <button v-if="oportunidade.plano" @click="copyBillingInfo(oportunidade.id)" class="p-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg" title="Copiar">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m-1 4h.01M9 16h5m0 0l-1-1m1 1l-1 1" /></svg>
                    </button>
                    <button @click="openEditModal(oportunidade)" class="p-1.5 text-primary-600 hover:bg-primary-50 rounded-lg" title="Editar">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click="deleteOportunidade(oportunidade.id)" class="p-1.5 text-red-600 hover:bg-red-50 rounded-lg" title="Excluir">
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
            <div class="flex justify-between items-end mt-2">
               <div class="text-xs text-gray-400">
                  <span class="font-bold uppercase tracking-widest text-[9px]">Indicador:</span>
                  <span class="ml-1 text-gray-600 outline-none">{{ oportunidade.indicador_nome || 'Direto' }}</span>
               </div>
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

            <div class="flex flex-wrap justify-end gap-x-4 gap-y-2 border-t pt-3 mt-4">
              <button @click="openWhatsapp(oportunidade)" class="flex items-center text-xs font-bold text-emerald-600 uppercase tracking-wider">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
                WhatsApp
              </button>
              <button 
                @click="openFaturamentoModal(oportunidade)" 
                class="text-xs font-bold text-emerald-600 uppercase tracking-widest flex items-center"
              >
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                 Faturamento
              </button>
              <button 
                v-if="oportunidade.plano"
                @click="openPropostaPreview(oportunidade.id)" 
                class="text-xs font-bold text-purple-600 uppercase tracking-widest flex items-center"
              >
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1.01.293.707V19a2 2 0 01-2 2z" /></svg>
                 Proposta
              </button>
              <button 
                v-if="oportunidade.plano"
                @click="copyBillingInfo(oportunidade.id)" 
                class="text-xs font-bold text-indigo-600 uppercase tracking-widest flex items-center"
              >
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m-1 4h.01M9 16h5m0 0l-1-1m1 1l-1 1" /></svg>
                 Copiar
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
      @saved="handleSaved"
    />

    <!-- WhatsApp -->
    <WhatsappChat
      :show="showWhatsapp"
      :number="whatsappData.number"
      :title="whatsappData.title"
      :oportunidade="whatsappData.oportunidade"
      @close="showWhatsapp = false"
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
import { useRouter } from 'vue-router'
import api from '@/services/api'
import OportunidadeModal from '@/components/OportunidadeModal.vue'
import FaturamentoModal from '@/components/FaturamentoModal.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

// Ícones simples
const IconPipeline = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>' }
const IconWin = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }
const IconTicket = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }
const IconTotal = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>' }

const oportunidades = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const funilFilter = ref('')
const canalFilter = ref('')
const statusFilter = ref('ABERTO')
const funisOptions = ref([])
const canaisOptions = ref([])

// WhatsApp
const showWhatsapp = ref(false)
const whatsappData = ref({
  number: '',
  title: '',
  oportunidade: null
})
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
  loadFilterOptions()
})

async function loadFilterOptions() {
  try {
    const [funisRes, canaisRes] = await Promise.all([
      api.get('/funis/', { params: { tipo: 'VENDAS' } }),
      authStore.isAdmin ? api.get('/canais/') : Promise.resolve({ data: [] })
    ])
    funisOptions.value = funisRes.data.results || funisRes.data
    canaisOptions.value = canaisRes.data.results || canaisRes.data
  } catch (err) {
    console.error('Erro ao carregar opções de filtro:', err)
  }
}

async function loadOportunidades() {
  loading.value = true
  error.value = null
  try {
    const params = {
      search: searchQuery.value || undefined,
      funil: funilFilter.value || undefined,
      canal: canalFilter.value || undefined,
      estagio__tipo: statusFilter.value || undefined
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
  router.push({ name: 'oportunidade-detail', params: { id: oportunidade.id } })
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

function handleSaved() {
  loadOportunidades()
}

function openWhatsapp(opp) {
  if (!opp.contato_telefone) {
    alert('Oportunidade sem telefone de contato cadastrado.')
    return
  }
  // Remove formatação do telefone (mantém apenas números)
  let cleanNumber = opp.contato_telefone.replace(/\D/g, '')

  // Adiciona código do país (55) se não estiver presente
  if (!cleanNumber.startsWith('55') && cleanNumber.length <= 11) {
    cleanNumber = '55' + cleanNumber
  }

  whatsappData.value = {
    number: cleanNumber,
    title: opp.nome,
    oportunidade: opp.id
  }
  showWhatsapp.value = true
}

async function openPropostaPreview(id) {
  try {
    const response = await api.get(`/oportunidades/${id}/gerar_proposta/?formato=html`, {
      responseType: 'text'
    })
    const win = window.open('', '_blank')
    win.document.write(response.data)
    win.document.close()
  } catch (error) {
    console.error('Erro ao gerar proposta:', error)
    alert('Erro ao gerar proposta.')
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
