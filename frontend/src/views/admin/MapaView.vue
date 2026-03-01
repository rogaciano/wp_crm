<template>
  <div class="mapa-admin space-y-6 pb-12">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-zinc-200 pb-6">
      <div>
        <h1 class="text-3xl font-bold text-zinc-900 font-display tracking-tight">Mapa de Clientes</h1>
        <p class="text-zinc-500 font-medium mt-1">Distribuição geográfica dos clientes por estado e canal</p>
      </div>

      <!-- KPIs rápidos -->
      <div class="flex items-center gap-4 flex-wrap">
        <div class="bg-white border border-zinc-200 rounded-md px-4 py-2 text-center shadow-sm">
          <p class="text-2xl font-bold text-zinc-900 font-display">{{ contas.length }}</p>
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Contas</p>
        </div>
        <div class="bg-white border border-zinc-200 rounded-md px-4 py-2 text-center shadow-sm">
          <p class="text-2xl font-bold text-blue-600 font-display">{{ oportunidades.length }}</p>
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Oportunidades</p>
        </div>
        <div class="bg-white border border-zinc-200 rounded-md px-4 py-2 text-center shadow-sm">
          <p class="text-2xl font-bold text-emerald-600 font-display">{{ estadosCobertos }}</p>
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Estados</p>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3 items-center">
      <div class="relative">
        <select v-model="filtroCanalId" @change="carregarContas"
          class="appearance-none bg-white border border-zinc-300 rounded-md px-4 py-2 pr-8 text-sm font-medium text-zinc-700 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 shadow-sm">
          <option :value="null">Todos os Canais</option>
          <option v-for="canal in canais" :key="canal.id" :value="canal.id">{{ canal.nome }}</option>
        </select>
        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-zinc-500">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </div>
      </div>

      <div class="relative">
        <select v-model="filtroStatus" @change="carregarContas"
          class="appearance-none bg-white border border-zinc-300 rounded-md px-4 py-2 pr-8 text-sm font-medium text-zinc-700 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 shadow-sm">
          <option value="">Todos os Status</option>
          <option value="PROSPECT">Prospect</option>
          <option value="CLIENTE_ATIVO">Cliente Ativo</option>
          <option value="INATIVO">Inativo</option>
        </select>
        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-zinc-500">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </div>
      </div>

      <!-- Filtro Tipo -->
      <div class="flex items-center bg-white p-1 rounded-md border border-zinc-200 shadow-sm gap-0.5">
        <button v-for="opt in tipoOpcoes" :key="opt.valor" @click="filtroTipo = opt.valor"
          :class="['px-3 py-1.5 text-xs font-semibold rounded-sm transition-all',
            filtroTipo === opt.valor ? 'bg-zinc-900 text-white' : 'text-zinc-600 hover:bg-zinc-50']">
          {{ opt.label }}
        </button>
      </div>

      <div v-if="loading" class="text-sm text-zinc-400 flex items-center gap-2">
        <div class="inline-block animate-spin rounded-full h-4 w-4 border-2 border-zinc-200 border-t-primary-600"></div>
        Carregando...
      </div>
    </div>

    <!-- Mapa + Painel lateral -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Mapa principal -->
      <div class="lg:col-span-2 bg-white border border-zinc-200 rounded-md shadow-sm overflow-hidden">
        <MapaBrasil
          :contas="filtroTipo !== 'oportunidades' ? contasFiltradas : []"
          :oportunidades="filtroTipo !== 'contas' ? oportunidades : []"
          :canais="canaisComEstado"
          :mostrar-oportunidades="filtroTipo !== 'contas'"
          height="560px"
          @selectEstado="onSelecionarEstado"
          @selectConta="onSelecionarConta"
        />
      </div>

      <!-- Painel lateral -->
      <div class="bg-white border border-zinc-200 rounded-md shadow-sm flex flex-col">
        <div class="p-5 border-b border-zinc-100">
          <h3 class="font-bold text-zinc-900 text-sm font-display">
            {{ estadoSelecionado ? `📍 ${estadoSelecionado.nome}` : 'Selecione um estado' }}
          </h3>
          <p v-if="estadoSelecionado" class="text-xs text-zinc-400 mt-0.5">
            {{ estadoSelecionado.contas.length }} empresa(s) encontrada(s)
          </p>
          <p v-else class="text-xs text-zinc-400 mt-0.5">Clique em um pin no mapa</p>
        </div>

        <div class="flex-1 overflow-y-auto divide-y divide-zinc-50">
          <div v-if="!estadoSelecionado" class="p-8 text-center">
            <svg class="w-10 h-10 mx-auto text-zinc-200 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p class="text-sm text-zinc-400">Clique em um marcador no mapa para ver as empresas do estado</p>
          </div>

          <router-link
            v-for="conta in estadoSelecionado?.contas"
            :key="conta.id"
            :to="`/contas/${conta.id}`"
            class="block px-5 py-3 hover:bg-zinc-50 transition-colors group"
          >
            <div class="flex items-start gap-2">
              <span class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" :style="{ backgroundColor: conta.canal_cor || '#64748b' }"></span>
              <div>
                <p class="font-semibold text-sm text-zinc-900 group-hover:text-primary-600 transition-colors">{{ conta.nome_empresa }}</p>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="text-xs text-zinc-400">{{ conta.cidade || conta.estado }}</span>
                  <span class="text-zinc-300">·</span>
                  <span :class="['text-xs font-medium', statusClass(conta.status_cliente)]">{{ statusLabel(conta.status_cliente) }}</span>
                </div>
                <p class="text-xs text-zinc-400 mt-0.5">{{ conta.canal_nome }}</p>
              </div>
            </div>
          </router-link>
        </div>

        <!-- Totais por estado -->
        <div v-if="resumoEstados.length > 0" class="border-t border-zinc-100 p-4">
          <p class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-3">Ranking de Estados</p>
          <div class="space-y-2 max-h-48 overflow-y-auto">
            <div v-for="(item, idx) in resumoEstados" :key="item.uf" class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="text-zinc-400 w-4 text-right">{{ idx + 1 }}</span>
                <span class="font-bold text-zinc-700">{{ item.uf }}</span>
                <span class="text-zinc-500">{{ item.nome }}</span>
              </div>
              <span class="font-bold text-zinc-900">{{ item.total }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import MapaBrasil from '@/components/MapaBrasil.vue'

const ESTADOS_NOMES = {
  AC: 'Acre', AL: 'Alagoas', AP: 'Amapá', AM: 'Amazonas', BA: 'Bahia',
  CE: 'Ceará', DF: 'Distrito Federal', ES: 'Espírito Santo', GO: 'Goiás',
  MA: 'Maranhão', MT: 'Mato Grosso', MS: 'Mato Grosso do Sul', MG: 'Minas Gerais',
  PA: 'Pará', PB: 'Paraíba', PR: 'Paraná', PE: 'Pernambuco', PI: 'Piauí',
  RJ: 'Rio de Janeiro', RN: 'Rio Grande do Norte', RS: 'Rio Grande do Sul',
  RO: 'Rondônia', RR: 'Roraima', SC: 'Santa Catarina', SP: 'São Paulo',
  SE: 'Sergipe', TO: 'Tocantins',
}

const loading = ref(false)
const contas = ref([])
const oportunidades = ref([])
const canais = ref([])
const filtroCanalId = ref(null)
const filtroStatus = ref('')
const filtroTipo = ref('ambos')
const estadoSelecionado = ref(null)

const tipoOpcoes = [
  { label: 'Ambos', valor: 'ambos' },
  { label: '⚫ Contas', valor: 'contas' },
  { label: '◆ Oportunidades', valor: 'oportunidades' },
]

const contasFiltradas = computed(() => contas.value)
const canaisComEstado = computed(() => canais.value.filter(c => c.estado))

const estadosCobertos = computed(() => {
  const ufs = new Set(contas.value.map(c => c.estado?.toUpperCase()).filter(Boolean))
  return ufs.size
})

const resumoEstados = computed(() => {
  const mapa = {}
  contas.value.forEach(c => {
    const uf = c.estado?.toUpperCase()
    if (!uf) return
    if (!mapa[uf]) mapa[uf] = { uf, nome: ESTADOS_NOMES[uf] || uf, total: 0 }
    mapa[uf].total++
  })
  return Object.values(mapa).sort((a, b) => b.total - a.total)
})

async function carregarContas() {
  loading.value = true
  try {
    const params = {}
    if (filtroCanalId.value) params.canal_id = filtroCanalId.value
    if (filtroStatus.value) params.status = filtroStatus.value
    const res = await api.get('/contas/mapa/', { params })
    contas.value = res.data
    estadoSelecionado.value = null
    await carregarOportunidades()
  } catch (e) {
    console.error('Erro ao carregar mapa:', e)
  } finally {
    loading.value = false
  }
}

async function carregarCanais() {
  try {
    const res = await api.get('/canais/')
    canais.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

async function carregarOportunidades() {
  try {
    const params = { page_size: 500 }
    if (filtroCanalId.value) params.canal = filtroCanalId.value
    const res = await api.get('/oportunidades/', { params })
    const oppsRaw = res.data.results || res.data

    const mappedOpps = []
    for (const opp of oppsRaw) {
      const canalObj = canais.value.find(c => c.id === opp.canal)
      const cor = canalObj?.cor || '#64748b'
      const canalNome = canalObj?.nome || ''

      if (opp.conta) {
        const contaMatch = contas.value.find(c => c.id === opp.conta)
        if (contaMatch?.estado) {
          mappedOpps.push({
            id: opp.id,
            nome: opp.nome,
            estado: contaMatch.estado.toUpperCase(),
            cidade: contaMatch.cidade || '',
            empresa_nome: contaMatch.nome_empresa,
            valor_estimado: parseFloat(opp.valor_estimado) || 0,
            estagio_nome: opp.estagio_nome || '',
            estagio_cor: '#64748b',
            canal_id: opp.canal,
            canal_nome: canalNome,
            canal_cor: cor,
          })
        }
      }
    }
    oportunidades.value = mappedOpps
  } catch (e) {
    console.error('Erro ao carregar oportunidades:', e)
  }
}

function onSelecionarEstado({ uf, nome, contas: contasEstado }) {
  estadoSelecionado.value = { uf, nome, contas: contasEstado }
}

function onSelecionarConta() {}

function statusLabel(s) {
  const m = { PROSPECT: 'Prospect', CLIENTE_ATIVO: 'Cliente Ativo', INATIVO: 'Inativo' }
  return m[s] || s
}

function statusClass(s) {
  if (s === 'CLIENTE_ATIVO') return 'text-emerald-600'
  if (s === 'INATIVO') return 'text-zinc-400'
  return 'text-orange-500'
}

onMounted(async () => {
  await Promise.all([carregarContas(), carregarCanais()])
})
</script>
