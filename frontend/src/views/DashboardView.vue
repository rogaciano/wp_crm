<template>
  <div class="space-y-6 pb-12">
    <!-- Header com Filtros -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-gray-900 font-outfit uppercase tracking-tighter">Dashboard Executivo</h1>
        <p class="text-gray-500 font-bold uppercase text-[10px] tracking-widest mt-1">Inteligência de Vendas e Ciência de Dados</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <!-- Filtro de Canal (apenas Admin) -->
        <select 
          v-if="authStore.isAdmin"
          v-model="canalFiltro" 
          @change="loadDashboard"
          class="bg-white border border-gray-100 rounded-xl px-4 py-2 text-sm font-bold shadow-sm focus:outline-none focus:ring-4 focus:ring-primary-50 transition-all cursor-pointer"
        >
          <option :value="null">Todos os Canais</option>
          <option v-for="canal in canais" :key="canal.id" :value="canal.id">
            {{ canal.nome }}
          </option>
        </select>
        
        <!-- Filtro de Período -->
        <div class="flex items-center gap-2 bg-white p-1 rounded-2xl shadow-sm border border-gray-100">
          <button 
            v-for="p in periodos" 
            :key="p.valor"
            @click="periodo = p.valor"
            :class="['px-5 py-2 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all', 
                     periodo === p.valor ? 'bg-primary-600 text-white shadow-lg shadow-primary-200' : 'text-gray-400 hover:bg-gray-50']"
          >
            {{ p.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!loaded" class="text-center py-24">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-100 border-b-primary-600"></div>
      <p class="mt-4 text-gray-400 font-bold uppercase text-[10px] tracking-widest">Sincronizando analytics...</p>
    </div>

    <!-- KPIs Cards -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="card p-6 border-none shadow-xl shadow-gray-100/50">
        <div class="flex items-center justify-between mb-4">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center p-2 shadow-lg" :style="{ backgroundColor: kpi.color + '1a', color: kpi.color }">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="kpi.iconPath" />
            </svg>
          </div>
          <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest">{{ kpi.label }}</span>
        </div>
        <div>
          <div class="text-2xl font-black text-gray-900 leading-none">{{ kpi.prefix }}{{ kpi.value }}{{ kpi.suffix }}</div>
          <div class="text-[10px] text-gray-400 font-bold uppercase tracking-tighter mt-2">{{ kpi.sub }}</div>
        </div>
      </div>
    </div>

    <!-- Cards de Atividades -->
    <div v-if="loaded" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Card Atividades Ativas -->
      <router-link 
        to="/atividades" 
        class="card-action bg-blue-50/50 border-blue-100"
      >
        <div class="flex items-center">
          <div class="bg-blue-600 p-2.5 rounded-xl text-white shadow-lg shadow-blue-200 mr-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
          </div>
          <div>
            <h4 class="text-blue-900 font-black text-[11px] uppercase tracking-widest leading-none mb-1">Tarefas Ativas</h4>
            <p class="text-blue-600 text-[10px] font-bold uppercase tracking-tighter">Foco em execução necessária</p>
          </div>
        </div>
        <div class="flex items-center">
          <span class="text-2xl font-black text-blue-700 mr-2">{{ dashboardData.kpis?.atividades_ativas || 0 }}</span>
          <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </div>
      </router-link>

      <!-- Card Atividades Atrasadas -->
      <router-link 
        to="/atividades" 
        class="card-action"
        :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'bg-red-50 border-red-100 animate-pulse-subtle' : 'bg-green-50 border-green-100'"
      >
        <div class="flex items-center">
          <div :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'bg-red-600 shadow-red-200' : 'bg-green-600 shadow-green-200'" class="p-2.5 rounded-xl text-white shadow-lg mr-4">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <div>
            <h4 :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-900' : 'text-green-900'" class="font-black text-[11px] uppercase tracking-widest leading-none mb-1">
              {{ dashboardData.kpis?.atividades_atrasadas > 0 ? 'Tarefas Atrasadas' : 'Tudo em Dia!' }}
            </h4>
            <p :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-600' : 'text-green-600'" class="text-[10px] font-bold uppercase tracking-tighter">
              {{ dashboardData.kpis?.atividades_atrasadas > 0 ? 'Alerta crítico de produtividade' : 'Excelente controle de pipeline' }}
            </p>
          </div>
        </div>
        <div class="flex items-center">
          <span :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-700' : 'text-green-700'" class="text-2xl font-black mr-2">{{ dashboardData.kpis?.atividades_atrasadas || 0 }}</span>
          <svg :class="dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-400' : 'text-green-400'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </div>
      </router-link>
    </div>

    <!-- Main Charts Grid -->
    <div v-if="loaded" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      
      <!-- Funil de Vendas -->
      <div class="lg:col-span-2 card p-8 shadow-2xl shadow-gray-100/30">
        <div class="flex justify-between items-center mb-8">
          <h3 class="font-black text-gray-800 uppercase text-[10px] tracking-widest flex items-center">
             <div class="p-1.5 bg-primary-50 rounded-lg mr-3">
               <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 20V10M12 20V4M6 20v-6" /></svg>
             </div>
             Pipeline por Estágio
          </h3>
          <div class="text-right">
            <span class="block text-[8px] font-black text-gray-300 uppercase tracking-widest leading-none mb-1">Volume Total Estimado</span>
            <span class="text-sm font-black text-primary-600">R$ {{ totalPipeline.toLocaleString() }}</span>
          </div>
        </div>
        <div class="h-80 relative">
          <Bar v-if="dashboardData.funil && dashboardData.funil.length > 0" :data="funelChartData" :options="funelChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-300 italic text-xs">Nenhum dado de pipeline no período</div>
        </div>
      </div>

      <!-- Maturidade Média -->
      <div class="card p-8 shadow-2xl shadow-gray-100/30">
        <h3 class="font-black text-gray-800 uppercase text-[10px] tracking-widest flex items-center mb-8">
           <div class="p-1.5 bg-rose-50 rounded-lg mr-3">
             <svg class="w-4 h-4 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
           </div>
           Índice de Maturidade
        </h3>
        <div class="h-80">
          <Radar v-if="Object.keys(dashboardData.maturidade_media || {}).length > 0" :data="radarChartData" :options="radarChartOptions" />
          <div v-else class="flex flex-col items-center justify-center h-full text-gray-300 gap-3">
            <svg class="w-8 h-8 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            <p class="text-[10px] font-black uppercase tracking-widest">Sem diagnósticos realizados</p>
          </div>
        </div>
        <div class="mt-6 pt-4 border-t border-gray-50 text-center">
          <p class="text-[9px] font-bold text-gray-400 uppercase tracking-tighter">Baseado em inteligência artificial e coleta de dados sdr/sales.</p>
        </div>
      </div>

      <!-- Tendência Mensal -->
      <div class="lg:col-span-2 card p-8 shadow-2xl shadow-gray-100/30">
        <h3 class="font-black text-gray-800 uppercase text-[10px] tracking-widest flex items-center mb-8">
           <div class="p-1.5 bg-emerald-50 rounded-lg mr-3">
             <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M23 6l-9.5 9.5-5-5L1 18m16-12h6v6" /></svg>
           </div>
           Performance (Conversão Semestral)
        </h3>
        <div class="h-80">
          <Line v-if="dashboardData.tendencia && dashboardData.tendencia.length > 0" :data="lineChartData" :options="lineChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-300 italic text-xs">Aguardando dados históricos...</div>
        </div>
      </div>

      <!-- Origens -->
      <div class="card p-8 shadow-2xl shadow-gray-100/30">
        <h3 class="font-black text-gray-800 uppercase text-[10px] tracking-widest flex items-center mb-8">
           <div class="p-1.5 bg-indigo-50 rounded-lg mr-3">
             <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21.21 15.89A10 10 0 118 2.83M22 12A10 10 0 0012 2v10z" /></svg>
           </div>
           Canais de Aquisição
        </h3>
        <div class="h-64 mb-6">
          <Pie v-if="dashboardData.origens && dashboardData.origens.length > 0" :data="pieChartData" :options="pieChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-gray-300">Nenhum dado</div>
        </div>
        <div class="space-y-3">
          <div v-for="(origem, idx) in dashboardData.origens.slice(0, 3)" :key="idx" class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: ['#3B82F6', '#10B981', '#F59E0B'][idx] }"></span>
              <span class="text-[10px] font-black text-gray-500 uppercase truncate max-w-[120px]">{{ origem?.fonte || 'Direto/Outros' }}</span>
            </div>
            <span class="text-xs font-black text-gray-900">{{ origem?.total || 0 }} <span class="text-[10px] text-gray-400 font-bold ml-1 uppercase">Negócios</span></span>
          </div>
        </div>
      </div>

    </div>

    <!-- Contatos por Tipo e Canal -->
    <div v-if="loaded" class="card p-8 shadow-2xl shadow-gray-100/30">
      <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <h3 class="font-black text-gray-800 uppercase text-[10px] tracking-widest flex items-center">
          <div class="p-1.5 bg-teal-50 rounded-lg mr-3">
            <svg class="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
          </div>
          Distribuição de Atendimento
        </h3>
        
        <div class="flex items-center gap-3">
          <div v-if="filtroTipoSelecionado || filtroCanalSelecionado" class="flex items-center gap-1.5">
            <span v-if="filtroTipoSelecionado" class="flex items-center gap-1 px-3 py-1.5 bg-teal-50 text-teal-700 rounded-xl text-[10px] font-black border border-teal-100 uppercase">
              {{ filtroTipoSelecionado.nome }}
              <button @click="filtroTipoSelecionado = null" class="hover:text-teal-900 ml-1">×</button>
            </span>
          </div>
          <router-link :to="urlContatosFiltrados" class="btn btn-primary text-[10px] px-6 py-2.5">
            Abrir Relatório Detalhado
          </router-link>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
        <div>
          <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-teal-500"></span>
            Categorização de Contatos
          </p>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <button 
              v-for="tipo in dashboardData.contatos_por_tipo" 
              :key="tipo.id"
              @click="toggleFiltroTipo(tipo)"
              :class="[
                'flex flex-col items-center justify-center p-5 rounded-3xl transition-all',
                filtroTipoSelecionado?.id === tipo.id 
                  ? 'bg-teal-600 text-white shadow-xl shadow-teal-200 ring-4 ring-teal-50' 
                  : 'bg-gray-50 border border-gray-100 hover:bg-white hover:shadow-lg'
              ]"
            >
              <span class="text-3xl mb-2">{{ tipo.emoji || '👤' }}</span>
              <span class="text-2xl font-black">{{ tipo.total }}</span>
              <span class="text-[9px] font-bold uppercase tracking-widest mt-1 opacity-60">{{ tipo.nome }}</span>
            </button>
          </div>
        </div>

        <div>
           <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
            Performance por Unidade
          </p>
          <div class="space-y-4">
             <div v-for="canal in dashboardData.contatos_por_canal.slice(0, 6)" :key="canal.id" 
                  class="flex items-center justify-between p-4 bg-gray-50/50 rounded-2xl border border-gray-50">
               <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-white flex items-center justify-center shadow-sm font-black text-gray-400 text-[10px]">
                    {{ canal.nome.charAt(0) }}
                  </div>
                  <span class="text-xs font-black text-gray-700 uppercase tracking-tighter">{{ canal.nome }}</span>
               </div>
               <span class="text-sm font-black text-gray-900">{{ canal.total }} <span class="text-[10px] text-gray-400 font-bold uppercase ml-1">Un.</span></span>
             </div>
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
import { Bar, Radar, Line, Pie, Doughnut } from 'vue-chartjs'
import { useAuthStore } from '@/stores/auth'

ChartJS.register(
  Title, Tooltip, Legend, BarElement, CategoryScale, 
  LinearScale, PointElement, LineElement, RadialLinearScale, 
  ArcElement, Filler
)

const authStore = useAuthStore()
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
  contatos_por_canal: [],
  vendas_por_plano: [],
  vendas_por_canal: []
})

const canais = ref([])
const canalFiltro = ref(null)
const filtroTipoSelecionado = ref(null)
const filtroCanalSelecionado = ref(null)

function toggleFiltroTipo(tipo) {
  filtroTipoSelecionado.value = filtroTipoSelecionado.value?.id === tipo.id ? null : tipo
}

const urlContatosFiltrados = computed(() => {
  const params = new URLSearchParams()
  if (filtroTipoSelecionado.value) params.append('tipo_contato', filtroTipoSelecionado.value.id)
  if (filtroCanalSelecionado.value) params.append('canal', filtroCanalSelecionado.value.id)
  const queryString = params.toString()
  return queryString ? `/contatos?${queryString}` : '/contatos'
})

async function fetchCanais() {
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data
  } catch (err) { console.error(err) }
}

async function fetchDashboard() {
  loaded.value = false
  try {
    const params = { periodo: periodo.value }
    if (canalFiltro.value) params.canal_id = canalFiltro.value
    const response = await api.get('/dashboard/', { params })
    dashboardData.value = {
      kpis: response.data.kpis || {},
      funil: response.data.funil || [],
      tendencia: response.data.tendencia || [],
      origens: response.data.origens || [],
      maturidade_media: response.data.maturidade_media || {},
      contatos_por_tipo: response.data.contatos_por_tipo || [],
      contatos_por_canal: response.data.contatos_por_canal || [],
      vendas_por_plano: response.data.vendas_por_plano || [],
      vendas_por_canal: response.data.vendas_por_canal || []
    }
    loaded.value = true
  } catch (error) {
    console.error('Erro dashboard:', error)
    loaded.value = true
  }
}

function loadDashboard() { fetchDashboard() }

onMounted(async () => {
  if (authStore.isAdmin) await fetchCanais()
  await fetchDashboard()
})

watch(periodo, fetchDashboard)

const totalPipeline = computed(() => {
  return (dashboardData.value.funil || []).reduce((acc, curr) => acc + (Number(curr?.valor) || 0), 0)
})

const kpiCards = computed(() => {
  const kpis = dashboardData.value.kpis || {}
  return [
    { 
      label: 'Receita Ganha', 
      value: Number(kpis.receita_ganha || 0).toLocaleString('pt-BR'), 
      prefix: 'R$ ', 
      sub: 'Conversões confirmadas', 
      iconPath: 'M12 1v22m5-18H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6', 
      color: '#10B981' 
    },
    { 
      label: 'Pipeline Ativo', 
      value: Number(kpis.pipeline_ativo || 0).toLocaleString('pt-BR'), 
      prefix: 'R$ ', 
      sub: 'Volume sob negociação', 
      iconPath: 'M12 22a10 10 0 100-20 10 10 0 000 20zm0-7a3 3 0 100-6 3 3 0 000 6zm0 4a7 7 0 100-14 7 7 0 000 14z', 
      color: '#3B82F6' 
    },
    { 
      label: 'Efetividade', 
      value: Number(kpis.win_rate || 0).toFixed(1), 
      suffix: '%', 
      sub: 'Taxa global de sucesso', 
      iconPath: 'M19 5L5 19M6.5 9a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM17.5 20a2.5 2.5 0 100-5 2.5 2.5 0 000 5z', 
      color: '#8B5CF6' 
    },
    { 
      label: 'Ticket Médio', 
      value: Number(kpis.ticket_medio || 0).toLocaleString('pt-BR'), 
      prefix: 'R$ ', 
      sub: 'Média por fechamento', 
      iconPath: 'M23 6l-9.5 9.5-5-5L1 18m16-12h6v6', 
      color: '#F59E0B' 
    },
    { 
      label: 'Novas Opps', 
      value: String(kpis.opps_novas || 0), 
      sub: 'Negócios gerados', 
      iconPath: 'M13 10V3L4 14h7v7l9-11h-7z', 
      color: '#64748B' 
    }
  ]
})

const funelChartData = computed(() => ({
  labels: (dashboardData.value.funil || []).map(f => f?.nome || ''),
  datasets: [{
    label: 'Valor (R$)',
    data: (dashboardData.value.funil || []).map(f => Number(f?.valor) || 0),
    backgroundColor: (dashboardData.value.funil || []).map(f => f?.cor || '#3B82F6'),
    borderRadius: 12
  }]
}))

const funelChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, grid: { borderDash: [2, 2], color: '#f1f1f1' }, ticks: { font: { weight: 'bold', size: 10 }, color: '#999' } },
    x: { grid: { display: false }, ticks: { font: { weight: 'black', size: 9 }, color: '#666' } }
  }
}

const radarChartData = computed(() => {
  const maturidade = dashboardData.value.maturidade_media || {}
  const keys = Object.keys(maturidade)
  return {
    labels: keys.length > 0 ? keys.map(k => k.toUpperCase()) : ['Aguardando'],
    datasets: [{
      label: 'Score',
      data: keys.length > 0 ? Object.values(maturidade) : [0],
      backgroundColor: 'rgba(244, 63, 94, 0.15)',
      borderColor: '#F43F5E',
      borderWidth: 3,
      pointBackgroundColor: '#F43F5E',
      pointRadius: 4
    }]
  }
})

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: { 
      min: 0, max: 10, ticks: { display: false }, 
      grid: { color: '#f1f1f1' }, 
      pointLabels: { font: { size: 9, weight: 'black' }, color: '#999' } 
    }
  },
  plugins: { legend: { display: false } }
}

const lineChartData = computed(() => {
  const t = dashboardData.value.tendencia || []
  return {
    labels: t.map(i => {
      const d = new Date(i.mes + 'T00:00:00')
      return d.toLocaleDateString('pt-BR', { month: 'short' }).toUpperCase()
    }),
    datasets: [
      { label: 'Vendas (R$)', data: t.map(i => i.valor), borderColor: '#10B981', backgroundColor: 'rgba(16, 185, 129, 0.05)', fill: true, tension: 0.4, borderWidth: 4, pointRadius: 0 },
      { label: 'Oportunidades', data: t.map(i => i.novas), borderColor: '#3B82F6', borderDash: [4, 4], tension: 0.4, borderWidth: 2, pointRadius: 0 }
    ]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { font: { weight: 'black', size: 9 }, boxWidth: 10 } } },
  scales: {
    y: { grid: { display: false }, ticks: { display: false } },
    x: { grid: { display: false }, ticks: { font: { weight: 'bold', size: 9 }, color: '#ccc' } }
  }
}

const pieChartData = computed(() => ({
  labels: (dashboardData.value.origens || []).map(o => o?.fonte),
  datasets: [{
    data: (dashboardData.value.origens || []).map(o => o?.total),
    backgroundColor: ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6'],
    borderWidth: 0
  }]
}))

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } }
}
</script>

<style scoped>
.font-outfit { font-family: 'Outfit', sans-serif; }
.card { @apply bg-white rounded-[2rem] border border-gray-100; }
.card-action { @apply flex items-center justify-between p-6 rounded-[2rem] shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] border; }
.btn { @apply px-6 py-3 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all shadow-md; }
.btn-primary { @apply bg-primary-600 text-white hover:bg-primary-700 shadow-primary-200; }
.animate-pulse-subtle { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .8; } }
</style>
