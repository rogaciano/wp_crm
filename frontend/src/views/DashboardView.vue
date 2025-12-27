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

    <!-- KPIs Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
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

    <!-- Main Charts Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      
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
          <Bar v-if="loaded" :data="funelChartData" :options="funelChartOptions" />
        </div>
      </div>

      <!-- Maturidade Média -->
      <div class="card p-6">
        <h3 class="font-bold text-gray-800 uppercase text-sm tracking-widest flex items-center mb-6">
           <svg class="w-4 h-4 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
           Maturidade dos Leads
        </h3>
        <div class="h-80">
          <Radar v-if="loaded" :data="radarChartData" :options="radarChartOptions" />
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
          <Line v-if="loaded" :data="lineChartData" :options="lineChartOptions" />
        </div>
      </div>

      <!-- Origens de Leads -->
      <div class="card p-6">
        <h3 class="font-bold text-gray-800 uppercase text-sm tracking-widest flex items-center mb-6">
           <svg class="w-4 h-4 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21.21 15.89A10 10 0 118 2.83M22 12A10 10 0 0012 2v10z" /></svg>
           Top Origens
        </h3>
        <div class="h-64 mb-6">
          <Pie v-if="loaded" :data="pieChartData" :options="pieChartOptions" />
        </div>
        <div class="space-y-2">
          <div v-for="(origem, idx) in dashboardData.origens" :key="idx" class="flex justify-between text-sm">
            <span class="text-gray-600 font-medium">{{ origem.fonte || 'Direto/Outros' }}</span>
            <span class="font-bold text-gray-900">{{ origem.total }} leads</span>
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
  maturidade_media: {}
})

async function fetchDashboard() {
  loaded.value = false
  try {
    const response = await api.get('/dashboard/', { params: { periodo: periodo.value } })
    dashboardData.value = response.data
    loaded.value = true
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error)
  }
}

onMounted(fetchDashboard)
watch(periodo, fetchDashboard)

const totalPipeline = computed(() => {
  return dashboardData.value.funil.reduce((acc, curr) => acc + (Number(curr.valor) || 0), 0)
})

const kpiCards = computed(() => [
  { 
    label: 'Receita Ganha', 
    value: dashboardData.value.kpis.receita_ganha?.toLocaleString('pt-BR') || '0', 
    prefix: 'R$ ', 
    sub: 'Total no período', 
    iconPath: 'M12 1v22m5-18H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6', 
    color: '#10B981' 
  },
  { 
    label: 'Pipeline Ativo', 
    value: dashboardData.value.kpis.pipeline_ativo?.toLocaleString('pt-BR') || '0', 
    prefix: 'R$ ', 
    sub: 'Oportunidades abertas', 
    iconPath: 'M12 22a10 10 0 100-20 10 10 0 000 20zm0-7a3 3 0 100-6 3 3 0 000 6zm0 4a7 7 0 100-14 7 7 0 000 14z', 
    color: '#3B82F6' 
  },
  { 
    label: 'Win Rate', 
    value: dashboardData.value.kpis.win_rate || '0', 
    suffix: '%', 
    sub: 'Taxa de conversão', 
    iconPath: 'M19 5L5 19M6.5 9a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM17.5 20a2.5 2.5 0 100-5 2.5 2.5 0 000 5z', 
    color: '#8B5CF6' 
  },
  { 
    label: 'Ticket Médio', 
    value: dashboardData.value.kpis.ticket_medio?.toLocaleString('pt-BR') || '0', 
    prefix: 'R$ ', 
    sub: 'Por venda ganha', 
    iconPath: 'M23 6l-9.5 9.5-5-5L1 18m16-12h6v6', 
    color: '#F59E0B' 
  },
  { 
    label: 'Novos Leads', 
    value: dashboardData.value.kpis.leads_novos || '0', 
    sub: 'Gerados no período', 
    iconPath: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2m4-14a4 4 0 100-8 4 4 0 000 8zm14 14v-2a4 4 0 00-3-3.87m-4-12a4 4 0 010 7.75', 
    color: '#64748B' 
  }
])

// Chart Configurations
const funelChartData = computed(() => ({
  labels: dashboardData.value.funil.map(f => f.nome),
  datasets: [{
    label: 'Valor (R$)',
    data: dashboardData.value.funil.map(f => f.valor),
    backgroundColor: dashboardData.value.funil.map(f => f.cor),
    borderRadius: 8
  }]
}))

const funelChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, grid: { display: false }, ticks: { callback: v => 'R$ ' + v.toLocaleString() } }
  }
}

const radarChartData = computed(() => ({
  labels: Object.keys(dashboardData.value.maturidade_media),
  datasets: [{
    label: 'Score Médio',
    data: Object.values(dashboardData.value.maturidade_media),
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderColor: '#EF4444',
    pointBackgroundColor: '#EF4444',
    pointBorderColor: '#fff'
  }]
}))

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: { min: 0, max: 10, ticks: { display: false } }
  }
}

const lineChartData = computed(() => ({
  labels: dashboardData.value.tendencia.map(t => new Date(t.mes).toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' })),
  datasets: [
    {
      label: 'Vendas Ganhas (R$)',
      data: dashboardData.value.tendencia.map(t => t.valor),
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      fill: true,
      tension: 0.4
    },
    {
      label: 'Novas Oportunidades',
      data: dashboardData.value.tendencia.map(t => t.novas),
      borderColor: '#3B82F6',
      borderDash: [5, 5],
      tension: 0.4
    }
  ]
}))

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } }
}

const pieChartData = computed(() => ({
  labels: dashboardData.value.origens.map(o => o.fonte || 'Outros'),
  datasets: [{
    data: dashboardData.value.origens.map(o => o.total),
    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6']
  }]
}))

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
