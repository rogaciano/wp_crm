<template>
  <div class="space-y-8 pb-12">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-zinc-200 pb-6">
      <div>
        <h1 class="text-3xl font-bold text-zinc-900 font-display tracking-tight">Dashboard Executivo</h1>
        <p class="text-zinc-500 font-medium mt-1">Visão geral de performance e inteligência de vendas</p>
      </div>
      
      <div class="flex flex-wrap items-center gap-3">
        <!-- Filtro de Canal -->
        <div v-if="authStore.isAdmin" class="relative">
          <select 
            v-model="canalFiltro" 
            @change="loadDashboard"
            class="appearance-none bg-white border border-zinc-300 rounded-md px-4 py-2 pr-8 text-sm font-medium text-zinc-700 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 shadow-sm transition-all hover:border-zinc-400"
          >
            <option :value="null">Todos os Canais</option>
            <option v-for="canal in canais" :key="canal.id" :value="canal.id">
              {{ canal.nome }}
            </option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-zinc-500">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </div>
        </div>
        
        <!-- Filtro de Período -->
        <div class="flex items-center bg-white p-1 rounded-md border border-zinc-200 shadow-sm">
          <button 
            v-for="p in periodos" 
            :key="p.valor"
            @click="periodo = p.valor"
            :class="['px-4 py-1.5 text-xs font-semibold rounded-sm transition-all', 
                     periodo === p.valor ? 'bg-zinc-900 text-white shadow-sm' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900']"
          >
            {{ p.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!loaded" class="text-center py-24">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-2 border-zinc-200 border-t-primary-600"></div>
      <p class="mt-4 text-zinc-400 font-medium text-sm animate-pulse">Carregando analytics...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="space-y-8">
      <!-- KPIs Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div v-for="kpi in kpiCards" :key="kpi.label" class="bg-white border border-zinc-200 p-5 rounded-md shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1 h-full" :style="{ backgroundColor: kpi.color }"></div>
          <div class="flex justify-between items-start mb-2">
             <span class="text-xs font-bold text-zinc-500 uppercase tracking-wider">{{ kpi.label }}</span>
             <svg class="w-4 h-4 text-zinc-300 group-hover:text-zinc-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="kpi.iconPath" />
             </svg>
          </div>
          <div class="flex items-baseline gap-1">
             <span class="text-xs font-medium text-zinc-400" v-if="kpi.prefix">{{ kpi.prefix }}</span>
             <span class="text-2xl font-bold text-zinc-900 font-display">{{ kpi.value }}</span>
             <span class="text-sm font-medium text-zinc-500" v-if="kpi.suffix">{{ kpi.suffix }}</span>
          </div>
          <p class="text-xs text-zinc-400 mt-1">{{ kpi.sub }}</p>
        </div>
      </div>

      <!-- Quick Actions / Alerts -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <router-link to="/atividades" class="group bg-white border border-zinc-200 p-5 rounded-md shadow-sm hover:border-primary-500 transition-all flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-zinc-100 text-zinc-600 rounded-md group-hover:bg-primary-50 group-hover:text-primary-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
            </div>
            <div>
              <h3 class="font-bold text-zinc-900 group-hover:text-primary-700 transition-colors">Tarefas Pendentes</h3>
              <p class="text-sm text-zinc-500">Fluxo de trabalho e follow-ups</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
             <span class="text-2xl font-display font-bold text-zinc-900">{{ dashboardData.kpis?.atividades_ativas || 0 }}</span>
             <svg class="w-5 h-5 text-zinc-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </div>
        </router-link>

        <router-link to="/atividades" class="group bg-white border border-zinc-200 p-5 rounded-md shadow-sm hover:border-red-500 transition-all flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div :class="['p-3 rounded-md transition-colors', dashboardData.kpis?.atividades_atrasadas > 0 ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600']">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <div>
              <h3 :class="['font-bold transition-colors', dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-700' : 'text-emerald-700']">
                 {{ dashboardData.kpis?.atividades_atrasadas > 0 ? 'Atenção Necessária' : 'Tudo em dia' }}
              </h3>
              <p :class="['text-sm', dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-500' : 'text-emerald-500']">
                {{ dashboardData.kpis?.atividades_atrasadas > 0 ? 'Tarefas atrasadas detectadas' : 'Nenhuma pendência crítica' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
             <span :class="['text-2xl font-display font-bold', dashboardData.kpis?.atividades_atrasadas > 0 ? 'text-red-600' : 'text-emerald-600']">
               {{ dashboardData.kpis?.atividades_atrasadas || 0 }}
             </span>
             <svg class="w-5 h-5 text-zinc-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </div>
        </router-link>
      </div>

      <!-- Charts Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Funil -->
        <div class="lg:col-span-2 bg-white border border-zinc-200 rounded-md p-6 shadow-sm">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-sm font-bold text-zinc-900 font-display">Pipeline por Estágio</h3>
            <div class="text-right">
              <p class="text-xs text-zinc-500 uppercase tracking-widest font-bold">Volume Total</p>
              <p class="text-lg font-bold text-primary-600 font-display">R$ {{ totalPipeline.toLocaleString() }}</p>
            </div>
          </div>
          <div class="h-80 relative">
            <Bar v-if="dashboardData.funil && dashboardData.funil.length > 0" :data="funelChartData" :options="funelChartOptions" />
            <div v-else class="flex items-center justify-center h-full text-zinc-400 text-sm">Sem dados de pipeline</div>
          </div>
        </div>

        <!-- Maturidade -->
        <div class="bg-white border border-zinc-200 rounded-md p-6 shadow-sm flex flex-col">
          <h3 class="text-sm font-bold text-zinc-900 font-display mb-6">Índice de Maturidade</h3>
          <div class="flex-1 min-h-[300px] relative">
            <Radar v-if="Object.keys(dashboardData.maturidade_media || {}).length > 0" :data="radarChartData" :options="radarChartOptions" />
            <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-zinc-300">
               <svg class="w-12 h-12 mb-2 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
               <span class="text-xs font-bold uppercase tracking-widest">Sem Diagnósticos</span>
            </div>
          </div>
        </div>

        <!-- Tendência -->
        <div class="lg:col-span-2 bg-white border border-zinc-200 rounded-md p-6 shadow-sm">
          <h3 class="text-sm font-bold text-zinc-900 font-display mb-6">Tendência de Conversão (6 Meses)</h3>
          <div class="h-80">
            <Line v-if="dashboardData.tendencia && dashboardData.tendencia.length > 0" :data="lineChartData" :options="lineChartOptions" />
            <div v-else class="flex items-center justify-center h-full text-zinc-400 text-sm">Aguardando dados históricos...</div>
          </div>
        </div>

        <!-- Origens -->
        <div class="bg-white border border-zinc-200 rounded-md p-6 shadow-sm">
           <h3 class="text-sm font-bold text-zinc-900 font-display mb-6">Canais de Aquisição</h3>
           <div class="h-[200px] mb-6 relative">
             <Doughnut v-if="dashboardData.origens && dashboardData.origens.length > 0" :data="pieChartData" :options="pieChartOptions" />
             <div v-else class="absolute inset-0 flex items-center justify-center text-zinc-300 text-sm">Sem dados</div>
           </div>
           <div class="space-y-3">
             <div v-for="(origem, idx) in dashboardData.origens.slice(0, 4)" :key="idx" class="flex justify-between items-center text-sm border-b border-zinc-50 pb-2 last:border-0 last:pb-0">
                <div class="flex items-center gap-2">
                   <span class="w-2.5 h-2.5 rounded-sm" :style="{ backgroundColor: ['#F97316', '#10B981', '#64748B', '#F43F5E', '#8B5CF6'][idx] }"></span>
                   <span class="text-zinc-600 truncate max-w-[100px] sm:max-w-[140px]">{{ origem?.fonte || 'Direto/Outros' }}</span>
                </div>
                <span class="font-bold text-zinc-900">{{ origem?.total || 0 }}</span>
             </div>
           </div>
        </div>

      </div>

      <!-- Advanced Reports Section -->
      <div class="bg-white border border-zinc-200 rounded-md p-6 shadow-sm">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
           <h3 class="text-sm font-bold text-zinc-900 font-display flex items-center gap-2">
             <span class="w-2 h-2 bg-zinc-900 rounded-full"></span>
             Relatório de Atendimento & Distribuição
           </h3>
           <button v-if="filtroTipoSelecionado" @click="filtroTipoSelecionado = null" class="text-xs font-bold text-red-600 hover:underline">
             Limpar filtros
           </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div>
            <p class="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-4">Por Tipo de Contato</p>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
               <button 
                  v-for="tipo in dashboardData.contatos_por_tipo" 
                  :key="tipo.id"
                  @click="toggleFiltroTipo(tipo)"
                  :class="[
                    'p-4 rounded-md border text-left transition-all',
                    filtroTipoSelecionado?.id === tipo.id 
                      ? 'border-primary-500 bg-primary-50/50 ring-1 ring-primary-500' 
                      : 'border-zinc-200 bg-zinc-50/50 hover:bg-white hover:border-zinc-300'
                  ]"
                >
                  <span class="text-2xl block mb-2">{{ tipo.emoji || '👤' }}</span>
                  <span class="text-xl font-bold text-zinc-900 block font-display">{{ tipo.total }}</span>
                  <span class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">{{ tipo.nome }}</span>
                </button>
            </div>
          </div>

          <div>
             <p class="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-4">Por Unidade de Negócio</p>
             <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
               <div v-for="canal in dashboardData.contatos_por_canal.slice(0, 6)" :key="canal.id" 
                    class="flex items-center justify-between p-3 bg-white rounded-md border border-zinc-100 hover:border-zinc-200 transition-colors">
                  <div class="flex items-center gap-3">
                     <div class="w-8 h-8 rounded bg-zinc-100 flex items-center justify-center text-zinc-600 font-bold text-xs uppercase">
                       {{ canal.nome.charAt(0) }}
                     </div>
                     <span class="text-xs font-bold text-zinc-700 truncate max-w-[120px]">{{ canal.nome }}</span>
                  </div>
                  <span class="text-sm font-bold text-zinc-900 font-display">{{ canal.total }}</span>
               </div>
             </div>
          </div>
        </div>

        <div class="mt-8 flex justify-end">
           <router-link :to="urlContatosFiltrados" class="inline-flex items-center gap-2 text-sm font-bold text-primary-600 hover:text-primary-700">
             Ver relatório completo de contatos
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
           </router-link>
        </div>
      </div>

      <!-- Mapa Geográfico (admin only) -->
      <div v-if="authStore.isAdmin" class="bg-white border border-zinc-200 rounded-md shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-zinc-100">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-zinc-900 rounded-full"></span>
            <h3 class="text-sm font-bold text-zinc-900 font-display">Distribuição Geográfica de Clientes</h3>
          </div>
          <router-link to="/config/mapa" class="text-xs font-bold text-primary-600 hover:text-primary-700 flex items-center gap-1">
            Ver mapa completo
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
          </router-link>
        </div>
        <MapaBrasil :contas="mapaContas" height="380px" />
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
import { Bar, Radar, Line, Doughnut } from 'vue-chartjs'
import { useAuthStore } from '@/stores/auth'
import MapaBrasil from '@/components/MapaBrasil.vue'

ChartJS.register(
  Title, Tooltip, Legend, BarElement, CategoryScale, 
  LinearScale, PointElement, LineElement, RadialLinearScale, 
  ArcElement, Filler
)

// Global Chart Config (Neo-Precision Style)
ChartJS.defaults.font.family = "'Inter', sans-serif"
ChartJS.defaults.color = '#71717a'
ChartJS.defaults.scale.grid.color = '#f4f4f5'

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
  kpis: {}, funil: [], tendencia: [], origens: [],
  maturidade_media: {}, contatos_por_tipo: [], contatos_por_canal: [],
  vendas_por_plano: [], vendas_por_canal: []
})

const mapaContas = ref([])

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
    dashboardData.value = response.data
    loaded.value = true
  } catch (error) {
    console.error('Erro dashboard:', error)
    loaded.value = true
  }
}

function loadDashboard() { fetchDashboard() }

onMounted(async () => {
  if (authStore.isAdmin) {
    await fetchCanais()
    fetchContasMapa()
  }
  await fetchDashboard()
})

async function fetchContasMapa() {
  try {
    const res = await api.get('/contas/mapa/')
    mapaContas.value = res.data
  } catch (e) {
    console.error('Erro ao carregar mapa:', e)
  }
}

watch(periodo, fetchDashboard)

const totalPipeline = computed(() => {
  return (dashboardData.value.funil || []).reduce((acc, curr) => acc + (Number(curr?.valor) || 0), 0)
})

const kpiCards = computed(() => {
  const kpis = dashboardData.value.kpis || {}
  return [
    { 
      label: 'Receita Ganha', 
      value: Number(kpis.receita_ganha || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), 
      sub: 'Conversões confirmadas', 
      iconPath: 'M12 1v22m5-18H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6', 
      color: '#10B981' // Emerald
    },
    { 
      label: 'Pipeline Ativo', 
      value: Number(kpis.pipeline_ativo || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), 
      sub: 'Em negociação', 
      iconPath: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6', 
      color: '#F97316' // Orange (Primary)
    },
    { 
      label: 'Win Rate', 
      value: Number(kpis.win_rate || 0).toFixed(1), 
      suffix: '%', 
      sub: 'Efetividade global', 
      iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', 
      color: '#8B5CF6' // Violet
    },
    { 
      label: 'Ticket Médio', 
      value: Number(kpis.ticket_medio || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), 
      sub: 'Média de contrato', 
      iconPath: 'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z', 
      color: '#eab308' // Yellow
    },
    { 
      label: 'Novas Opps', 
      value: String(kpis.opps_novas || 0), 
      sub: 'Volume do período', 
      iconPath: 'M12 4v16m8-8H4', 
      color: '#3f3f46' // Zinc
    }
  ]
})

// Charts Visuals
const chartPalette = ['#F97316', '#10B981', '#64748B', '#F43F5E', '#8B5CF6', '#EAB308']

const funelChartData = computed(() => ({
  labels: (dashboardData.value.funil || []).map(f => f?.nome || ''),
  datasets: [{
    label: 'Valor (R$)',
    data: (dashboardData.value.funil || []).map(f => Number(f?.valor) || 0),
    backgroundColor: '#F97316',
    borderRadius: 4,
    barPercentage: 0.6
  }]
}))

const funelChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, border: { display: false }, grid: { borderDash: [4, 4] } },
    x: { grid: { display: false }, border: { display: false } }
  }
}

const radarChartData = computed(() => {
  const maturidade = dashboardData.value.maturidade_media || {}
  const keys = Object.keys(maturidade)
  return {
    labels: keys.length > 0 ? keys.map(k => k.toUpperCase()) : [],
    datasets: [{
      label: 'Score',
      data: keys.length > 0 ? Object.values(maturidade) : [],
      backgroundColor: 'rgba(249, 115, 22, 0.2)',
      borderColor: '#F97316',
      borderWidth: 2,
      pointBackgroundColor: '#fff',
      pointBorderColor: '#F97316',
      pointRadius: 3
    }]
  }
})

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: { 
      min: 0, max: 10, ticks: { display: false }, 
      angleLines: { color: '#e4e4e7' }, 
      grid: { color: '#e4e4e7' },
      pointLabels: { font: { size: 10, weight: 'bold' } } 
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
      { 
        type: 'bar',
        label: 'Vendas (R$)', 
        data: t.map(i => i.valor), 
        backgroundColor: '#10B981',
        borderRadius: 2,
        order: 2
      },
      { 
        type: 'line',
        label: 'Oportunidades', 
        data: t.map(i => i.novas), 
        borderColor: '#0f172a',
        backgroundColor: '#0f172a',
        borderWidth: 2, 
        pointRadius: 3,
        tension: 0.1,
        yAxisID: 'y1',
        order: 1
      }
    ]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 6 } } },
  scales: {
    y: { display: false, grid: { display: false } },
    y1: { display: false, position: 'right', grid: { display: false } },
    x: { grid: { display: false }, border: { display: false } }
  }
}

const pieChartData = computed(() => ({
  labels: (dashboardData.value.origens || []).map(o => o?.fonte),
  datasets: [{
    data: (dashboardData.value.origens || []).map(o => o?.total),
    backgroundColor: chartPalette,
    borderWidth: 0,
    hoverOffset: 4
  }]
}))

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  cutout: '75%'
}
</script>
