<template>
  <div class="space-y-6 pb-12">
    <!-- Header com Filtro de Período -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Dashboard Executivo</h1>
        <p class="text-gray-500">Inteligência de Vendas e Ciência de Dados</p>
      </div>
      <div class="flex items-center gap-2 bg-white p-1 rounded-xl shadow-sm border border-gray-100">
        <button 
          v-for="p in periodos" 
          :key="p.valor"
          @click="periodo = p.valor"
          :class="['px-4 py-2 text-sm font-semibold rounded-lg transition-all', 
                   periodo === p.valor ? 'bg-primary-600 text-white shadow-md' : 'text-gray-600 hover:bg-gray-50']"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!loaded" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
        <p class="text-gray-500">Carregando dados do dashboard...</p>
      </div>
    </div>

    <!-- KPIs Cards -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="card p-5 border-t-4" :style="{ borderColor: kpi.color }">
        <div class="flex items-center justify-between mb-2">
          <div class="p-2 rounded-lg" :style="{ backgroundColor: kpi.color + '1a' }">
            <svg class="w-5 h-5" :style="{ color: kpi.color }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="kpi.iconPath" />
            </svg>
          </div>
          <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">{{ kpi.label }}</span>
        </div>
        <div class="mt-4">
          <div class="text-2xl font-black text-gray-900">{{ kpi.prefix }}{{ kpi.value }}{{ kpi.suffix }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ kpi.sub }}</div>
        </div>
      </div>
    </div>

    <!-- Cards de Atividades (Ativas e Atrasadas) -->
    <div v-if="loaded" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Card Atividades Ativas -->
      <router-link 
        to="/atividades" 
        class="flex items-center justify-between p-4 bg-blue-50 border border-blue-100 rounded-2xl shadow-sm hover:bg-blue-100 transition-all group"
      >
        <div class="flex items-center">
          <div class="bg-blue-500 p-2 rounded-xl text-white mr-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
          </div>
          <div>
            <h4 class="text-blue-800 font-black text-sm uppercase tracking-wider leading-none mb-1">Atividades Ativas</h4>
            <p class="text-blue-700 text-xs font-bold">Você tem {{ dashboardData.kpis?.atividades_ativas || 0 }} atividades pendentes</p>
          </div>
        </div>
        <div class="flex items-center">
          <span class="text-2xl font-black text-blue-600 mr-2">{{ dashboardData.kpis?.atividades_ativas || 0 }}</span>
          <svg class="w-5 h-5 text-blue-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </div>
      </router-link>

      <!-- Card Atividades Atrasadas -->
      <router-link 
        to="/atividades" 
        class="flex items-center justify-between p-4 rounded-2xl shadow-sm transition-all group"
        :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'bg-red-50 border border-red-100 hover:bg-red-100 animate-pulse' : 'bg-green-50 border border-green-100 hover:bg-green-100'"
      >
        <div class="flex items-center">
          <div :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'bg-red-500' : 'bg-green-500'" class="p-2 rounded-xl text-white mr-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <div>
            <h4 :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-800' : 'text-green-800'" class="font-black text-sm uppercase tracking-wider leading-none mb-1">
              {{ dashboardData.kpis?.atividades_atrasadas > 0 ? 'Atividades Atrasadas' : 'Tudo em Dia!' }}
            </h4>
            <p :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-700' : 'text-green-700'" class="text-xs font-bold">
              {{ dashboardData.kpis?.atividades_atrasadas > 0 ? `Você tem ${dashboardData.kpis.atividades_atrasadas} atividades atrasadas` : 'Nenhuma atividade atrasada' }}
            </p>
          </div>
        </div>
        <div class="flex items-center">
          <span :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-600' : 'text-green-600'" class="text-2xl font-black mr-2">{{ dashboardData.kpis?.atividades_atrasadas || 0 }}</span>
          <svg :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-400' : 'text-green-400'" class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </div>
      </router-link>
    </div>

    <!-- Main Charts Grid -->
    <div v-if="loaded" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      
      <!-- Funil de Vendas -->
      <div class="lg:col-span-2 card p-6">
        <div class="flex justify-between items-center mb-6">
          <h3 class="font-bold text-gray-800 uppercase text-sm tracking-widest flex items-center">
             <svg class="w-4 h-4 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 20V10M12 20V4M6 20v-6" /></svg>
             Pipeline por Estágio
          </h3>
          <span class="text-xs text-gray-400 font-medium">Volume Total: R$ {{ totalPipeline.toLocaleString() }}</span>
        </div>
        <div class="h-80 relative">
          <Bar v-if="dashboardData.funil && dashboardData.funil.length > 0" :data="funelChartData" :options="funelChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-400">
            <p>Nenhum dado disponível</p>
          </div>
        </div>
      </div>

      <!-- Maturidade Média -->
      <div class="card p-6">
        <h3 class="font-bold text-gray-800 uppercase text-sm tracking-widest flex items-center mb-6">
           <svg class="w-4 h-4 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
           Maturidade dos Leads
        </h3>
        <div class="h-80">
          <Radar v-if="Object.keys(dashboardData.maturidade_media || {}).length > 0" :data="radarChartData" :options="radarChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-400">
            <p class="text-sm">Nenhum dado disponível</p>
          </div>
        </div>
        <div class="mt-4 text-center">
          <p class="text-xs text-gray-500 px-4">Média baseada nos últimos diagnósticos de maturidade realizados.</p>
        </div>
      </div>

      <!-- Tendência Mensal -->
      <div class="lg:col-span-2 card p-6">
        <h3 class="font-bold text-gray-800 uppercase text-sm tracking-widest flex items-center mb-6">
           <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M23 6l-9.5 9.5-5-5L1 18m16-12h6v6" /></svg>
           Performance de Vendas (Mensal)
        </h3>
        <div class="h-80">
          <Line v-if="dashboardData.tendencia && dashboardData.tendencia.length > 0" :data="lineChartData" :options="lineChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-400">
            <p>Nenhum dado disponível</p>
          </div>
        </div>
      </div>

      <!-- Origens de Leads -->
      <div class="card p-6">
        <h3 class="font-bold text-gray-800 uppercase text-sm tracking-widest flex items-center mb-6">
           <svg class="w-4 h-4 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21.21 15.89A10 10 0 118 2.83M22 12A10 10 0 0012 2v10z" /></svg>
           Top Origens
        </h3>
        <div class="h-64 mb-6">
          <Pie v-if="dashboardData.origens && dashboardData.origens.length > 0" :data="pieChartData" :options="pieChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-400">
            <p class="text-sm">Nenhum dado disponível</p>
          </div>
        </div>
        <div class="space-y-2">
          <div v-if="dashboardData.origens && dashboardData.origens.length > 0">
            <div v-for="(origem, idx) in dashboardData.origens" :key="idx" class="flex justify-between text-sm">
              <span class="text-gray-600 font-medium">{{ origem?.fonte || 'Direto/Outros' }}</span>
              <span class="font-bold text-gray-900">{{ origem?.total || 0 }} leads</span>
            </div>
          </div>
          <div v-else class="text-sm text-gray-400 text-center py-4">
            Nenhum dado disponível
          </div>
        </div>
      </div>

    </div>

    <!-- Contatos por Tipo e por Canal - Filtros Combinados -->
    <div v-if="loaded" class="card p-6 mt-6">
      <div class="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-4">
        <h3 class="font-bold text-gray-800 uppercase text-sm tracking-widest flex items-center">
          <svg class="w-4 h-4 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
          Contatos por Tipo e Canal
        </h3>
        
        <!-- Botão de ação com filtros selecionados -->
        <div class="flex items-center gap-2">
          <div v-if="filtroTipoSelecionado || filtroCanalSelecionado" class="flex items-center gap-2 text-sm">
            <span v-if="filtroTipoSelecionado" class="inline-flex items-center gap-1 px-2 py-1 bg-teal-100 text-teal-700 rounded-full">
              <span>{{ filtroTipoSelecionado.emoji || '👤' }}</span>
              {{ filtroTipoSelecionado.nome }}
              <button @click="filtroTipoSelecionado = null" class="ml-1 hover:text-teal-900">&times;</button>
            </span>
            <span v-if="filtroCanalSelecionado" class="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-full">
              🏢 {{ filtroCanalSelecionado.nome }}
              <button @click="filtroCanalSelecionado = null" class="ml-1 hover:text-amber-900">&times;</button>
            </span>
          </div>
          <router-link 
            :to="urlContatosFiltrados"
            class="btn-primary text-sm px-4 py-2 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
            Ver Contatos
          </router-link>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Contatos por Tipo -->
        <div>
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-teal-500"></span>
            Por Tipo de Contato
          </p>
          <div v-if="dashboardData.contatos_por_tipo && dashboardData.contatos_por_tipo.length > 0" class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <button 
              v-for="tipo in dashboardData.contatos_por_tipo" 
              :key="tipo.id"
              @click="toggleFiltroTipo(tipo)"
              :class="[
                'flex flex-col items-center justify-center p-3 rounded-xl transition-all cursor-pointer',
                filtroTipoSelecionado?.id === tipo.id 
                  ? 'bg-teal-500 text-white shadow-lg ring-2 ring-teal-300' 
                  : 'bg-gradient-to-br from-gray-50 to-gray-100 hover:from-teal-50 hover:to-teal-100 hover:shadow-md'
              ]"
            >
              <span class="text-2xl mb-1">{{ tipo.emoji || '👤' }}</span>
              <span class="text-xl font-black">{{ tipo.total }}</span>
              <span class="text-[10px] font-medium text-center truncate w-full" :class="filtroTipoSelecionado?.id === tipo.id ? 'text-teal-100' : 'text-gray-500'">{{ tipo.nome }}</span>
            </button>
          </div>
          <div v-else class="flex items-center justify-center h-24 text-gray-400">
            <p class="text-sm">Nenhum contato</p>
          </div>
        </div>

        <!-- Contatos por Canal -->
        <div>
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
            Por Canal
          </p>
          <div v-if="dashboardData.contatos_por_canal && dashboardData.contatos_por_canal.length > 0" class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <button 
              v-for="canal in dashboardData.contatos_por_canal" 
              :key="canal.id"
              @click="toggleFiltroCanal(canal)"
              :class="[
                'flex flex-col items-center justify-center p-3 rounded-xl transition-all cursor-pointer',
                filtroCanalSelecionado?.id === canal.id 
                  ? 'bg-amber-500 text-white shadow-lg ring-2 ring-amber-300' 
                  : 'bg-gradient-to-br from-gray-50 to-gray-100 hover:from-amber-50 hover:to-amber-100 hover:shadow-md'
              ]"
            >
              <span class="text-2xl mb-1">🏢</span>
              <span class="text-xl font-black">{{ canal.total }}</span>
              <span class="text-[10px] font-medium text-center truncate w-full" :class="filtroCanalSelecionado?.id === canal.id ? 'text-amber-100' : 'text-gray-500'">{{ canal.nome }}</span>
            </button>
          </div>
          <div v-else class="flex items-center justify-center h-24 text-gray-400">
            <p class="text-sm">Nenhum canal</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import api from '@/services/api'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  ArcElement,
  Filler
} from 'chart.js'
import { Bar, Radar, Line, Pie } from 'vue-chartjs'

ChartJS.register(
  Title, Tooltip, Legend, BarElement, CategoryScale, 
  LinearScale, PointElement, LineElement, RadialLinearScale, 
  ArcElement, Filler
)

const periodo = ref(30)
const periodos = [
  { label: '7D', valor: 7 },
  { label: '30D', valor: 30 },
  { label: '90D', valor: 90 },
  { label: '1 Ano', valor: 365 }
]

const loaded = ref(false)
const dashboardData = ref({
  kpis: {},
  funil: [],
  tendencia: [],
  origens: [],
  maturidade_media: {},
  contatos_por_tipo: [],
  contatos_por_canal: []
})

// Filtros combinados para contatos
const filtroTipoSelecionado = ref(null)
const filtroCanalSelecionado = ref(null)

function toggleFiltroTipo(tipo) {
  if (filtroTipoSelecionado.value?.id === tipo.id) {
    filtroTipoSelecionado.value = null
  } else {
    filtroTipoSelecionado.value = tipo
  }
}

function toggleFiltroCanal(canal) {
  if (filtroCanalSelecionado.value?.id === canal.id) {
    filtroCanalSelecionado.value = null
  } else {
    filtroCanalSelecionado.value = canal
  }
}

const urlContatosFiltrados = computed(() => {
  const params = new URLSearchParams()
  if (filtroTipoSelecionado.value) {
    params.append('tipo_contato', filtroTipoSelecionado.value.id)
  }
  if (filtroCanalSelecionado.value) {
    params.append('canal', filtroCanalSelecionado.value.id)
  }
  const queryString = params.toString()
  return queryString ? `/contatos?${queryString}` : '/contatos'
})

async function fetchDashboard() {
  loaded.value = false
  try {
    const response = await api.get('/dashboard/', { params: { periodo: periodo.value } })
    console.log('📊 Dados do dashboard recebidos:', response.data)
    
    // Garantir que os dados tenham a estrutura correta
    dashboardData.value = {
      kpis: response.data.kpis || {},
      funil: response.data.funil || [],
      tendencia: response.data.tendencia || [],
      origens: response.data.origens || [],
      maturidade_media: response.data.maturidade_media || {},
      contatos_por_tipo: response.data.contatos_por_tipo || [],
      contatos_por_canal: response.data.contatos_por_canal || []
    }
    
    console.log('📊 Dashboard data processado:', dashboardData.value)
    loaded.value = true
  } catch (error) {
    console.error('❌ Erro ao carregar dashboard:', error)
    console.error('Detalhes do erro:', error.response?.data || error.message)
    // Manter dados vazios mas marcar como carregado para não ficar em loading infinito
    loaded.value = true
  }
}

onMounted(fetchDashboard)
watch(periodo, fetchDashboard)

const totalPipeline = computed(() => {
  if (!dashboardData.value.funil || !Array.isArray(dashboardData.value.funil)) {
    return 0
  }
  return dashboardData.value.funil.reduce((acc, curr) => acc + (Number(curr?.valor) || 0), 0)
})

const kpiCards = computed(() => {
  const kpis = dashboardData.value.kpis || {}
  
  return [
    { 
      label: 'Receita Ganha', 
      value: (kpis.receita_ganha != null && kpis.receita_ganha !== undefined) 
        ? Number(kpis.receita_ganha).toLocaleString('pt-BR') 
        : '0', 
      prefix: 'R$ ', 
      sub: 'Total no período', 
      iconPath: 'M12 1v22m5-18H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6', 
      color: '#10B981' 
    },
    { 
      label: 'Pipeline Ativo', 
      value: (kpis.pipeline_ativo != null && kpis.pipeline_ativo !== undefined) 
        ? Number(kpis.pipeline_ativo).toLocaleString('pt-BR') 
        : '0', 
      prefix: 'R$ ', 
      sub: 'Oportunidades abertas', 
      iconPath: 'M12 22a10 10 0 100-20 10 10 0 000 20zm0-7a3 3 0 100-6 3 3 0 000 6zm0 4a7 7 0 100-14 7 7 0 000 14z', 
      color: '#3B82F6' 
    },
    { 
      label: 'Win Rate', 
      value: (kpis.win_rate != null && kpis.win_rate !== undefined) 
        ? Number(kpis.win_rate).toFixed(1) 
        : '0', 
      suffix: '%', 
      sub: 'Taxa de conversão', 
      iconPath: 'M19 5L5 19M6.5 9a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM17.5 20a2.5 2.5 0 100-5 2.5 2.5 0 000 5z', 
      color: '#8B5CF6' 
    },
    { 
      label: 'Ticket Médio', 
      value: (kpis.ticket_medio != null && kpis.ticket_medio !== undefined) 
        ? Number(kpis.ticket_medio).toLocaleString('pt-BR') 
        : '0', 
      prefix: 'R$ ', 
      sub: 'Por venda ganha', 
      iconPath: 'M23 6l-9.5 9.5-5-5L1 18m16-12h6v6', 
      color: '#F59E0B' 
    },
    { 
      label: 'Novos Leads', 
      value: (kpis.leads_novos != null && kpis.leads_novos !== undefined) 
        ? String(kpis.leads_novos) 
        : '0', 
      sub: 'Gerados no período', 
      iconPath: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2m4-14a4 4 0 100-8 4 4 0 000 8zm14 14v-2a4 4 0 00-3-3.87m-4-12a4 4 0 010 7.75', 
      color: '#64748B' 
    },
    { 
      label: 'Atrasos', 
      value: (kpis.atividades_atrasadas != null && kpis.atividades_atrasadas !== undefined) 
        ? String(kpis.atividades_atrasadas) 
        : '0', 
      sub: 'Atividades vencidas', 
      iconPath: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z', 
      color: '#EF4444' 
    }
  ]
})

// Chart Configurations
const funelChartData = computed(() => {
  const funil = dashboardData.value.funil || []
  return {
    labels: funil.map(f => f?.nome || ''),
    datasets: [{
      label: 'Valor (R$)',
      data: funil.map(f => Number(f?.valor) || 0),
      backgroundColor: funil.map(f => f?.cor || '#3B82F6'),
      borderRadius: 8
    }]
  }
})

const funelChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, grid: { display: false }, ticks: { callback: v => 'R$ ' + v.toLocaleString() } }
  }
}

const radarChartData = computed(() => {
  const maturidade = dashboardData.value.maturidade_media || {}
  const keys = Object.keys(maturidade)
  return {
    labels: keys.length > 0 ? keys : ['Sem dados'],
    datasets: [{
      label: 'Score Médio',
      data: keys.length > 0 ? Object.values(maturidade).map(v => Number(v) || 0) : [0],
      backgroundColor: 'rgba(239, 68, 68, 0.2)',
      borderColor: '#EF4444',
      pointBackgroundColor: '#EF4444',
      pointBorderColor: '#fff'
    }]
  }
})

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: { min: 0, max: 10, ticks: { display: false } }
  }
}

const lineChartData = computed(() => {
  const tendencia = dashboardData.value.tendencia || []
  console.log('📈 Dados de tendência para gráfico:', tendencia)
  
  if (tendencia.length === 0) {
    console.log('⚠️ Nenhum dado de tendência disponível')
    return {
      labels: ['Sem dados'],
      datasets: [
        {
          label: 'Vendas Ganhas (R$)',
          data: [0],
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Novas Oportunidades',
          data: [0],
          borderColor: '#3B82F6',
          borderDash: [5, 5],
          tension: 0.4
        }
      ]
    }
  }
  
  const labels = tendencia.map(t => {
    if (!t?.mes) return ''
    try {
      // Formato ISO: "2024-01-01" ou "2024-01-01T00:00:00"
      const dateStr = t.mes.includes('T') ? t.mes.split('T')[0] : t.mes
      const date = new Date(dateStr + 'T00:00:00')
      return date.toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' })
    } catch (e) {
      console.error('Erro ao formatar data:', t.mes, e)
      return t.mes
    }
  })
  
  const valores = tendencia.map(t => Number(t?.valor) || 0)
  const novas = tendencia.map(t => Number(t?.novas) || 0)
  
  console.log('📈 Labels:', labels)
  console.log('📈 Valores:', valores)
  console.log('📈 Novas:', novas)
  
  return {
    labels: labels,
    datasets: [
      {
        label: 'Vendas Ganhas (R$)',
        data: valores,
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Novas Oportunidades',
        data: novas,
        borderColor: '#3B82F6',
        borderDash: [5, 5],
        tension: 0.4
      }
    ]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } }
}

const pieChartData = computed(() => {
  const origens = dashboardData.value.origens || []
  return {
    labels: origens.length > 0 
      ? origens.map(o => o?.fonte || 'Outros')
      : ['Sem dados'],
    datasets: [{
      data: origens.length > 0 
        ? origens.map(o => Number(o?.total) || 0)
        : [0],
      backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6']
    }]
  }
})

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } }
}
</script>

<style scoped>
.card {
  @apply bg-white rounded-2xl shadow-sm border border-gray-100;
}
</style>
