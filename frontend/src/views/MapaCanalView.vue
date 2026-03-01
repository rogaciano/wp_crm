<template>
  <div class="space-y-6 pb-12">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-zinc-200 pb-6">
      <div>
        <h1 class="text-3xl font-bold text-zinc-900 font-display tracking-tight">
          Meu Mapa
        </h1>
        <p class="text-zinc-500 font-medium mt-1">
          Distribuição geográfica dos seus clientes
          <span v-if="canal" :style="{ color: canal.cor }" class="font-bold">— {{ canal.nome }}</span>
        </p>
      </div>

      <!-- KPIs -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="bg-white border border-zinc-200 rounded-md px-4 py-2 text-center shadow-sm">
          <p class="text-2xl font-bold font-display" :style="{ color: canal?.cor || '#F97316' }">{{ contas.length }}</p>
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Contas</p>
        </div>
        <div class="bg-white border border-zinc-200 rounded-md px-4 py-2 text-center shadow-sm">
          <p class="text-2xl font-bold font-display text-blue-600">{{ oportunidades.length }}</p>
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Oportunidades</p>
        </div>
        <div class="bg-white border border-zinc-200 rounded-md px-4 py-2 text-center shadow-sm">
          <p class="text-2xl font-bold font-display text-emerald-600">{{ estadosCobertos }}</p>
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Estados</p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-24">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-2 border-zinc-200 border-t-primary-600"></div>
      <p class="mt-4 text-zinc-400 font-medium text-sm">Carregando mapa...</p>
    </div>

    <!-- Sem canal -->
    <div v-else-if="!canal" class="bg-white border border-zinc-200 rounded-md p-12 text-center shadow-sm">
      <svg class="w-16 h-16 mx-auto text-zinc-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <h3 class="font-bold text-zinc-700 mb-1">Nenhum canal vinculado</h3>
      <p class="text-sm text-zinc-400">Você não está vinculado a nenhum canal de vendas.</p>
    </div>

    <!-- Mapa + Painel lateral -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Mapa -->
      <div class="lg:col-span-2 bg-white border border-zinc-200 rounded-md shadow-sm overflow-hidden">
        <!-- Filtro de tipo -->
        <div class="flex items-center gap-2 p-4 border-b border-zinc-100">
          <button
            v-for="opt in filtroOpcoes"
            :key="opt.valor"
            @click="filtroTipo = opt.valor"
            :class="['px-3 py-1.5 text-xs font-semibold rounded-full transition-all border',
              filtroTipo === opt.valor
                ? 'text-white border-transparent'
                : 'bg-white text-zinc-600 border-zinc-200 hover:border-zinc-300']"
            :style="filtroTipo === opt.valor ? { backgroundColor: canal.cor, borderColor: canal.cor } : {}"
          >
            {{ opt.label }}
          </button>
        </div>
        <MapaBrasil
          :contas="contasExibidas"
          :oportunidades="oportunidadesExibidas"
          :zoom-estado="canal.estado"
          :cor-canal="canal.cor"
          :mostrar-oportunidades="filtroTipo !== 'contas'"
          height="540px"
          @selectEstado="onSelecionarEstado"
          @selectConta="onSelecionarConta"
        />
      </div>

      <!-- Painel lateral -->
      <div class="bg-white border border-zinc-200 rounded-md shadow-sm flex flex-col">
        <div class="p-5 border-b border-zinc-100">
          <!-- Badge de cor do canal -->
          <div class="flex items-center gap-2 mb-3">
            <span class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: canal.cor }"></span>
            <span class="text-xs font-bold text-zinc-500 uppercase tracking-wider">{{ canal.nome }}</span>
          </div>
          <h3 class="font-bold text-zinc-900 text-sm font-display">
            {{ estadoSelecionado ? `📍 ${estadoSelecionado.nome}` : 'Selecione um estado' }}
          </h3>
          <p v-if="estadoSelecionado" class="text-xs text-zinc-400 mt-0.5">
            {{ estadoSelecionado.contas?.length || 0 }} empresa(s) no estado
          </p>
          <p v-else class="text-xs text-zinc-400 mt-0.5">Clique em um pin no mapa</p>
        </div>

        <!-- Abas Contas / Oportunidades -->
        <div v-if="estadoSelecionado" class="flex border-b border-zinc-100">
          <button
            v-for="aba in abas"
            :key="aba.valor"
            @click="abaAtiva = aba.valor"
            :class="['flex-1 py-2 text-xs font-bold transition-colors',
              abaAtiva === aba.valor ? 'border-b-2 text-zinc-900' : 'text-zinc-400 hover:text-zinc-600']"
            :style="abaAtiva === aba.valor ? { borderColor: canal.cor } : {}"
          >
            {{ aba.label }} ({{ aba.count }})
          </button>
        </div>

        <div class="flex-1 overflow-y-auto divide-y divide-zinc-50">
          <!-- Estado não selecionado -->
          <div v-if="!estadoSelecionado" class="p-8 text-center">
            <svg class="w-10 h-10 mx-auto text-zinc-200 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p class="text-sm text-zinc-400">Clique em um marcador no mapa</p>
          </div>

          <!-- Contas do estado -->
          <template v-else-if="abaAtiva === 'contas'">
            <router-link
              v-for="conta in estadoSelecionado.contas"
              :key="conta.id"
              :to="`/contas/${conta.id}`"
              class="block px-5 py-3 hover:bg-zinc-50 transition-colors group"
            >
              <div class="flex items-start gap-2">
                <span class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" :style="{ backgroundColor: canal.cor }"></span>
                <div>
                  <p class="font-semibold text-sm text-zinc-900 group-hover:text-primary-600 transition-colors">
                    {{ conta.nome_empresa }}
                  </p>
                  <p class="text-xs text-zinc-400 mt-0.5">{{ conta.cidade || estadoSelecionado.uf }}</p>
                </div>
              </div>
            </router-link>
            <p v-if="!estadoSelecionado.contas?.length" class="p-5 text-sm text-zinc-400 text-center">Nenhuma conta neste estado</p>
          </template>

          <!-- Oportunidades do estado -->
          <template v-else>
            <router-link
              v-for="opp in oppsDoEstado"
              :key="opp.id"
              :to="`/negocios/${opp.id}`"
              class="block px-5 py-3 hover:bg-zinc-50 transition-colors group"
            >
              <div class="flex items-start gap-2">
                <span class="w-2 h-2 rounded-sm rotate-45 mt-1.5 flex-shrink-0" :style="{ backgroundColor: canal.cor }"></span>
                <div>
                  <p class="font-semibold text-sm text-zinc-900 group-hover:text-primary-600 transition-colors">
                    {{ opp.nome }}
                  </p>
                  <p class="text-xs text-zinc-400 mt-0.5">{{ opp.empresa_nome }} · {{ opp.estagio_nome }}</p>
                  <p v-if="opp.valor_estimado > 0" class="text-xs font-bold mt-0.5" :style="{ color: canal.cor }">
                    R$ {{ opp.valor_estimado.toLocaleString('pt-BR') }}
                  </p>
                </div>
              </div>
            </router-link>
            <p v-if="!oppsDoEstado.length" class="p-5 text-sm text-zinc-400 text-center">Nenhuma oportunidade neste estado</p>
          </template>
        </div>

        <!-- Ranking de estados -->
        <div v-if="resumoEstados.length > 0" class="border-t border-zinc-100 p-4">
          <p class="text-[10px] font-bold text-zinc-400 uppercase tracking-wider mb-3">Ranking de Estados</p>
          <div class="space-y-2 max-h-40 overflow-y-auto">
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

const loading = ref(true)
const canal = ref(null)
const contas = ref([])
const oportunidades = ref([])
const estadoSelecionado = ref(null)
const abaAtiva = ref('contas')
const filtroTipo = ref('ambos')

const filtroOpcoes = [
  { label: 'Todos', valor: 'ambos' },
  { label: '⚫ Contas', valor: 'contas' },
  { label: '◆ Oportunidades', valor: 'oportunidades' },
]

const abas = computed(() => [
  { label: 'Contas', valor: 'contas', count: estadoSelecionado.value?.contas?.length || 0 },
  { label: 'Oportunidades', valor: 'oportunidades', count: oppsDoEstado.value.length },
])

const contasExibidas = computed(() =>
  filtroTipo.value === 'oportunidades' ? [] : contas.value
)

const oportunidadesExibidas = computed(() =>
  filtroTipo.value === 'contas' ? [] : oportunidades.value
)

const estadosCobertos = computed(() => {
  const ufs = new Set([
    ...contas.value.map(c => c.estado?.toUpperCase()).filter(Boolean),
    ...oportunidades.value.map(o => o.estado?.toUpperCase()).filter(Boolean),
  ])
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

const oppsDoEstado = computed(() => {
  if (!estadoSelecionado.value) return []
  return oportunidades.value.filter(o => o.estado === estadoSelecionado.value.uf)
})

async function carregar() {
  loading.value = true
  try {
    const res = await api.get('/mapa/canal/')
    canal.value = res.data.canal
    contas.value = res.data.contas || []
    oportunidades.value = res.data.oportunidades || []
  } catch (e) {
    console.error('Erro ao carregar mapa do canal:', e)
  } finally {
    loading.value = false
  }
}

function onSelecionarEstado({ uf, nome, contas: contasEstado }) {
  estadoSelecionado.value = { uf, nome, contas: contasEstado }
  abaAtiva.value = 'contas'
}

function onSelecionarConta() {}

onMounted(carregar)
</script>
