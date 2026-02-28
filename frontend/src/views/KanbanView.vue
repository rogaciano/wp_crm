<template>
  <div>
    <!-- Header Simples -->
    <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 font-outfit">
          {{ activeTipoFunil === 'VENDAS' ? 'Pipeline de Vendas' : (activeTipoFunil === 'POS_VENDA' ? 'Pós-Venda' : 'Suporte Técnico') }}
        </h1>
        <p class="text-gray-500 mt-1 font-medium">
          {{ selectedFunil?.nome || 'Gerencie seu processo comercial' }}
        </p>
      </div>
      
      <!-- Abas de Tipo de Funil -->
      <div class="flex bg-gray-100 p-1 rounded-2xl w-fit border border-gray-200 shadow-sm">
        <button 
          v-for="tipo in tiposFunil" 
          :key="tipo.id"
          @click="changeTipoFunil(tipo.id)"
          :class="['px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all',
                   activeTipoFunil === tipo.id ? 'bg-white text-primary-600 shadow-md' : 'text-gray-400 hover:text-gray-600']"
        >
          {{ tipo.label }}
        </button>
      </div>
    </div>

    <!-- Floating Toolbar (canto superior direito) -->
    <div class="fixed top-4 right-4 z-50 flex items-center gap-2 bg-white/95 backdrop-blur-sm rounded-2xl p-2 shadow-xl border border-gray-100">
      <!-- Funnel Selector -->
      <select 
        v-model="activeFunilId" 
        @change="onFunilChange"
        class="bg-gray-50 border-0 rounded-xl px-3 py-2 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all cursor-pointer"
      >
        <option v-for="funil in filteredFunis" :key="funil.id" :value="funil.id">
          {{ funil.nome }}
        </option>
      </select>

      <!-- Canal Selector (For Admin) -->
      <select 
        v-if="authStore.isAdmin"
        v-model="activeCanalId" 
        @change="onCanalChange"
        class="bg-gray-50 border-0 rounded-xl px-3 py-2 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all cursor-pointer"
      >
        <option :value="null">Todos os Canais</option>
        <option v-for="canal in canais" :key="canal.id" :value="canal.id">
          {{ canal.nome }}
        </option>
      </select>

      <!-- Status Selector -->
      <select 
        v-model="activeStatus" 
        @change="loadKanban"
        class="bg-gray-50 border-0 rounded-xl px-3 py-2 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all cursor-pointer"
      >
        <option value="ABERTO">Em aberto</option>
        <option value="GANHO">Concluídos (Ganho)</option>
        <option value="PERDIDO">Cancelados (Perdido)</option>
        <option value="">Todos os status</option>
      </select>

      <div class="relative">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Buscar oportunidade, conta..."
          class="bg-gray-50 border-0 rounded-xl pl-9 pr-3 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all w-52"
        />
        <svg class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35m0 0A7.5 7.5 0 1 0 6 6a7.5 7.5 0 0 0 10.65 10.65Z" />
        </svg>
      </div>

      <!-- Botão Nova Oportunidade -->
      <button 
        @click="openCreateModal" 
        class="bg-primary-600 hover:bg-primary-700 text-white rounded-xl px-4 py-2 text-sm font-bold shadow-lg shadow-primary-600/30 hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span class="hidden sm:inline">Nova</span>
      </button>
    </div>

    <!-- Mobile Stage Selector -->
    <div class="lg:hidden flex gap-2 overflow-x-auto pb-4 custom-scrollbar snap-x no-scrollbar">
      <button 
        v-for="coluna in kanbanColumns" 
        :key="'tab-' + coluna.estagio.id"
        @click="scrollToStage(coluna.estagio.id)"
        class="flex-shrink-0 px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest border transition-all whitespace-nowrap"
        :style="{ 
          borderColor: coluna.estagio.cor, 
          backgroundColor: activeStage === coluna.estagio.id ? coluna.estagio.cor : 'transparent',
          color: activeStage === coluna.estagio.id ? '#fff' : coluna.estagio.cor
        }"
      >
        {{ coluna.estagio.nome }} ({{ coluna.items.length }})
      </button>
    </div>

    <div v-if="loading" class="text-center py-24">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-100 border-b-primary-600"></div>
      <p class="mt-4 text-gray-400 font-bold uppercase text-[10px] tracking-widest">Sincronizando pipeline...</p>
    </div>

    <div v-if="error" class="mb-6 p-5 bg-red-50 text-red-600 rounded-2xl border border-red-100 flex items-center gap-3">
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
      <span class="font-bold text-sm">{{ error }}</span>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !kanbanData.length && !error" class="text-center py-24">
      <div class="bg-gray-50 rounded-2xl p-8 max-w-md mx-auto border border-dashed border-gray-200">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-500 font-medium">Nenhum funil ou oportunidade encontrada para esta categoria.</p>
        <p class="text-gray-400 text-xs mt-2">Certifique-se de que os funis estão configurados e ativos no painel administrativo.</p>
      </div>
    </div>

    <div v-else 
      ref="kanbanContainer"
      class="flex gap-3 lg:gap-4 overflow-x-auto pb-8 snap-x snap-mandatory custom-scrollbar min-h-[calc(100vh-250px)]"
      @scroll="updateActiveStage"
    >
      <div
        v-for="coluna in kanbanColumns"
        :key="coluna.estagio.id"
        :id="'stage-' + coluna.estagio.id"
        class="flex-shrink-0 w-[260px] sm:w-[300px] lg:w-[320px] snap-center"
      >
        <div class="bg-white/50 rounded-3xl border border-gray-100 h-full flex flex-col group/col">
          <!-- Header da Coluna -->
          <div
            class="p-5 border-b border-gray-100 bg-white rounded-t-3xl shadow-sm"
            :style="{ borderTopColor: coluna.estagio.cor, borderTopWidth: '4px' }"
          >
            <div class="flex justify-between items-center">
              <h3 class="font-black text-gray-800 uppercase text-[10px] tracking-widest truncate">{{ coluna.estagio.nome }}</h3>
              <span class="text-[10px] font-black bg-gray-50 px-2 py-0.5 rounded-lg border border-gray-100 text-gray-400">
                {{ coluna.items.length }}
              </span>
            </div>
            <p v-if="activeTipoFunil === 'VENDAS'" class="text-[10px] text-primary-600 font-black uppercase tracking-widest mt-2">
               Vol: R$ {{ calcularTotalColuna(coluna.items).toLocaleString() }}
            </p>
          </div>

          <!-- Cards -->
          <div
            class="p-4 space-y-4 flex-1 overflow-y-auto custom-scrollbar"
            style="max-height: calc(100vh - 350px);"
            @drop="onDrop($event, coluna.estagio.id)"
            @dragover.prevent
            @dragenter.prevent
          >
            <div
              v-for="item in coluna.items"
              :key="item.id"
              draggable="true"
              @dragstart="onDragStart($event, item)"
              @click="editItem(item)"
              class="bg-white border border-gray-100 rounded-2xl p-4 cursor-grab active:cursor-grabbing hover:shadow-xl hover:shadow-gray-100 hover:border-primary-100 transition-all duration-300 group relative"
            >
              <!-- Badge de tipo -->
              <span 
                class="absolute top-4 right-4 text-[8px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border"
                :class="activeTipoFunil === 'VENDAS' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-blue-50 text-blue-600 border-blue-100'"
              >
                {{ activeTipoFunil === 'VENDAS' ? 'OPORTUNIDADE' : 'ATENDIMENTO' }}
              </span>

              <span
                v-if="item.status_cliente_display"
                class="absolute top-10 right-4 text-[8px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border"
                :class="item.status_cliente === 'CLIENTE_ATIVO'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : (item.status_cliente === 'INATIVO'
                    ? 'bg-amber-50 text-amber-700 border-amber-200'
                    : 'bg-sky-50 text-sky-700 border-sky-200')"
              >
                {{ item.status_cliente_display }}
              </span>
              
              <h4 class="font-black text-gray-800 mb-3 leading-tight group-hover:text-primary-600 transition-colors pr-24">{{ item.nome }}</h4>
              
              <div class="text-[11px] text-gray-500 space-y-2.5">
                <p class="flex items-center font-bold text-gray-400">
                  <svg class="w-3.5 h-3.5 mr-2 opacity-50 font-black" fill="currentColor" viewBox="0 0 24 24"><path d="M21 13v10h-6v-6h-6v6h-6v-10l9-9z"/></svg>
                  <span class="truncate">{{ (item.conta_nome && item.conta_nome !== 'N/A') ? item.conta_nome : 'Empresa não vinculada' }}</span>
                </p>
                <p v-if="item.origem_nome || item.fonte" class="flex items-center font-bold text-blue-400/80">
                  <svg class="w-3.5 h-3.5 mr-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 015.656 0l4-4a4 4 0 01-5.656-5.656l-1.102 1.101" /></svg>
                  <span class="truncate">{{ item.origem_nome || item.fonte }}</span>
                </p>
                <p v-if="item.contato_nome" class="flex items-center font-bold text-gray-400">
                  <svg class="w-3.5 h-3.5 mr-2 opacity-50" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2a5 5 0 105 5 5 5 0 00-5-5zm0 12c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5z"/></svg>
                  <span class="truncate">{{ item.contato_nome }}</span>
                </p>
                
                <div v-if="activeTipoFunil === 'VENDAS'" class="mt-4 pt-4 border-t border-gray-50 flex justify-between items-end">
                  <div>
                    <p v-if="item.valor_estimado && activeTipoFunil === 'VENDAS'" class="text-sm font-black text-green-600">
                      R$ {{ Number(item.valor_estimado).toLocaleString('pt-BR') }}
                    </p>
                    <p v-if="item.data_fechamento_esperada" class="text-[9px] font-black text-gray-300 uppercase tracking-tighter mt-1">
                      {{ formatDate(item.data_fechamento_esperada) }}
                    </p>
                  </div>
                  <div class="text-right flex flex-col items-end">
                    <div v-if="item.probabilidade" class="w-12 h-1 bg-gray-100 rounded-full overflow-hidden mb-1">
                       <div class="h-full bg-primary-500" :style="{ width: item.probabilidade + '%' }"></div>
                    </div>
                    <span class="text-[9px] font-black text-gray-400 uppercase tracking-tighter">{{ item.probabilidade || 0 }}% Prob.</span>
                  </div>
                </div>

                <div v-if="item.indicador_nome" class="mt-2 flex items-center gap-1.5 px-2 py-1 rounded-lg bg-indigo-50/50 w-fit">
                   <span class="text-[8px] font-black text-indigo-400 uppercase tracking-widest">Ind: {{ item.indicador_nome }}</span>
                </div>
              </div>

              <!-- Ações flutuantes -->
              <div class="absolute -top-3 left-1/2 -translate-x-1/2 flex scale-90 space-x-1 opacity-0 group-hover:opacity-100 transition-all duration-300 z-10 pointer-events-none group-hover:pointer-events-auto">
                 <button @click.stop="openWhatsapp(item)" class="action-btn text-green-600 bg-white border border-green-100 shadow-lg relative" title="WhatsApp">
                   <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
                   <span v-if="item.whatsapp_nao_lidas > 0" class="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[8px] font-black text-white ring-2 ring-white">
                     {{ item.whatsapp_nao_lidas }}
                   </span>
                 </button>
                 <button @click.stop="openFaturamentoModal(item)" class="action-btn text-emerald-600 bg-white border border-emerald-100 shadow-lg" title="Faturamento">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                 </button>
                 <button v-if="item.plano" @click.stop="openPropostaPreview(item.id)" class="action-btn text-purple-600 bg-white border border-purple-100 shadow-lg" title="Gerar Proposta">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1.01.293.707V19a2 2 0 01-2 2z" /></svg>
                 </button>
                 <button v-if="item.plano" @click.stop="copyBillingInfo(item.id)" class="action-btn text-indigo-600 bg-white border border-indigo-100 shadow-lg" title="Copiar Faturamento">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m-1 4h.01M9 16h5m0 0l-1-1m1 1l-1 1" /></svg>
                 </button>
                 <button @click.stop="editItem(item)" class="action-btn text-primary-600 bg-white border border-primary-100 shadow-lg" title="Editar">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                 </button>
                 <button @click.stop="deleteOportunidade(item.id)" class="action-btn text-red-600 bg-white border border-red-100 shadow-lg" title="Excluir">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                 </button>
              </div>
            </div>
            
            <!-- Empty column hint -->
            <div v-if="coluna.items.length === 0" class="h-32 border-2 border-dashed border-gray-100 rounded-3xl flex items-center justify-center bg-white/30 group-hover/col:border-primary-100 transition-colors">
               <p class="text-[10px] text-gray-300 font-black uppercase tracking-widest italic tracking-tighter">
                 {{ activeTipoFunil === 'VENDAS' ? 'Pronto para novos negócios' : 'Tudo em dia por aqui' }}
               </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <OportunidadeModal
      :show="showModal"
      :oportunidade="selectedOportunidade"
      :fixed-funil-id="activeFunilId"
      :fixed-estagio-id="activeContextEstagioId"
      @close="closeModal"
      @saved="handleSaved"
    />

    <WhatsappChat
      :show="showWhatsapp"
      :number="whatsappData.number"
      :title="whatsappData.title"
      :oportunidade="whatsappData.oportunidade"
      @close="showWhatsapp = false"
      @messagesRead="whatsappStore.fetchUnreadCounts"
    />

    <FaturamentoModal
      :show="showFaturamentoModal"
      :oportunidade="selectedFaturamento"
      @close="showFaturamentoModal = false"
      @saved="handleSaved"
    />


  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useOportunidadesStore } from '@/stores/oportunidades'
import { useAuthStore } from '@/stores/auth'
import { useWhatsappStore } from '@/stores/whatsapp'
import { storeToRefs } from 'pinia'
import OportunidadeModal from '@/components/OportunidadeModal.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'
import FaturamentoModal from '@/components/FaturamentoModal.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const whatsappStore = useWhatsappStore()

const oportunidadesStore = useOportunidadesStore()
const { kanbanData, loading, error, funis } = storeToRefs(oportunidadesStore)

const activeFunilId = ref(null)
const activeCanalId = ref(null)
const canais = ref([])
const showModal = ref(false)
const selectedOportunidade = ref(null)
const draggedItem = ref(null)
const activeContextEstagioId = ref(null)
const activeStatus = ref('')
const searchTerm = ref('')

const activeTipoFunil = ref(route.query.tipo || 'VENDAS')
const tiposFunil = [
  { id: 'VENDAS', label: 'Vendas' },
  { id: 'POS_VENDA', label: 'Pós-Venda' },
  { id: 'SUPORTE', label: 'Suporte' }
]

// Monitora mudanças na URL para trocar o tipo de funil (ex: vindo do menu lateral)
watch(() => route.query.tipo, (newTipo) => {
  if (newTipo && newTipo !== activeTipoFunil.value) {
    activeTipoFunil.value = newTipo
    setInitialFunil()
  }
})

const filteredFunis = computed(() => {
  return funis.value.filter(f => f.tipo === activeTipoFunil.value)
})

function normalizeSearchText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
}

const normalizedSearchTerm = computed(() => normalizeSearchText(searchTerm.value).trim())

const kanbanColumns = computed(() => {
  const term = normalizedSearchTerm.value
  if (!term) return kanbanData.value

  return kanbanData.value.map((coluna) => ({
    ...coluna,
    items: (coluna.items || []).filter((item) => {
      const searchable = [
        item.nome,
        item.conta_nome,
        item.contato_nome,
        item.origem_nome,
        item.fonte
      ]
        .map(normalizeSearchText)
        .join(' ')

      return searchable.includes(term)
    })
  }))
})

const activeStage = ref(null)
const kanbanContainer = ref(null)

const showWhatsapp = ref(false)
const whatsappData = ref({
  number: '',
  title: '',
  oportunidade: null
})

const showFaturamentoModal = ref(false)
const selectedFaturamento = ref(null)

const selectedFunil = computed(() => {
  return funis.value.find(f => f.id === activeFunilId.value) || filteredFunis.value[0]
})

function calcularTotalColuna(oportunidades) {
  return oportunidades.reduce((acc, curr) => acc + (Number(curr.valor_estimado) || 0), 0)
}

function scrollToStage(stageId) {
  activeStage.value = stageId
  const el = document.getElementById('stage-' + stageId)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }
}

function updateActiveStage() {
  if (!kanbanContainer.value || !kanbanColumns.value.length) return
  const container = kanbanContainer.value
  const scrollLeft = container.scrollLeft
  
  // Find which column is most visible
  const index = Math.round(scrollLeft / 280) // 280 is mobile column width
  if (kanbanColumns.value[index]) {
    activeStage.value = kanbanColumns.value[index].estagio.id
  }
}

onMounted(async () => {
  await fetchFunnels()
  if (authStore.isAdmin) {
    await fetchCanais()
  }
})

async function fetchCanais() {
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data
  } catch (err) {
    console.error('Erro ao carregar canais:', err)
  }
}

async function fetchFunnels() {
  await oportunidadesStore.fetchFunis()
  await setInitialFunil()
}

function setInitialFunil() {
  if (filteredFunis.value.length > 0) {
    // Tenta encontrar um funil que o usuário tem acesso direto dentro do tipo filtrado
    const userFunisIds = authStore.user?.funis_acesso || []
    const userFunil = filteredFunis.value.find(f => userFunisIds.includes(f.id))
    
    activeFunilId.value = userFunil ? userFunil.id : filteredFunis.value[0].id
    loadKanban()
  } else {
    activeFunilId.value = null
    oportunidadesStore.kanbanData = []
  }
}

async function changeTipoFunil(tipo) {
  activeTipoFunil.value = tipo
  setInitialFunil()
}

async function loadKanban() {
  await oportunidadesStore.fetchKanban(activeFunilId.value, activeCanalId.value, activeStatus.value)
  if (kanbanData.value?.length) {
    activeStage.value = kanbanData.value[0].estagio.id
  }
}

async function onCanalChange() {
  await loadKanban()
}

async function onFunilChange() {
  await loadKanban()
}

function onDragStart(event, item) {
  draggedItem.value = item
  event.dataTransfer.effectAllowed = 'move'
}

async function onDrop(event, novoEstagioId) {
  event.preventDefault()
  if (!draggedItem.value) return
  
  const itemId = draggedItem.value.id
  const estagioAtualId = draggedItem.value.estagio
  
  if (estagioAtualId === novoEstagioId) return
  
  try {
    await oportunidadesStore.mudarEstagio(itemId, novoEstagioId)
    await loadKanban()
  } catch (error) {
    console.error('Erro ao mover item:', error)
  }
  
  draggedItem.value = null
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR')
}



// ...

function openCreateModal(estagioId = null) {
  selectedOportunidade.value = null
  activeContextEstagioId.value = typeof estagioId === 'number' ? estagioId : null
  showModal.value = true
}

function openEditModal(item) {
  selectedOportunidade.value = item
  showModal.value = true
}

async function deleteOportunidade(id) {
  if (!confirm('Tem certeza que deseja excluir esta oportunidade?')) return
  
  try {
    await api.delete(`/oportunidades/${id}/`)
    await loadKanban()
  } catch (error) {
    console.error('Erro ao excluir oportunidade:', error)
    alert('Erro ao excluir oportunidade')
  }
}

function editItem(item) {
  router.push({ name: 'oportunidade-detail', params: { id: item.id } })
}

function closeModal() {
  showModal.value = false
  selectedOportunidade.value = null
}

async function handleSaved() {
  await loadKanban()
}

async function copyBillingInfo(id) {
  try {
    const response = await api.get(`/oportunidades/${id}/gerar_texto_faturamento/`)
    const texto = response.data.texto
    
    await navigator.clipboard.writeText(texto)
    alert('Texto de faturamento copiado para a área de transferência! 📋')
  } catch (error) {
    console.error('Erro ao gerar texto:', error)
    alert('Erro ao gerar texto de faturamento.')
  }
}

function openWhatsapp(item) {
  let phone = item.contato_telefone || item.contato_celular
  if (!phone) {
    alert('Contato sem telefone cadastrado neta oportunidade.')
    return
  }
  
  let cleanNumber = phone.replace(/\D/g, '')
  if (!cleanNumber.startsWith('55') && cleanNumber.length <= 11) {
    cleanNumber = '55' + cleanNumber
  }

  whatsappData.value = {
    number: cleanNumber,
    title: item.nome,
    oportunidade: item.id
  }
  showWhatsapp.value = true
}

function openFaturamentoModal(item) {
  selectedFaturamento.value = item
  showFaturamentoModal.value = true
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
</script>

<style scoped>
.font-outfit { font-family: 'Outfit', sans-serif; }
.btn { @apply px-5 py-2.5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all active:scale-95 flex items-center justify-center gap-2; }
.btn-primary { @apply bg-primary-600 text-white hover:bg-primary-700 shadow-primary-100; }
.action-btn { @apply p-2 rounded-xl transition-all hover:scale-110 active:scale-90 pointer-events-auto; }
.custom-scrollbar::-webkit-scrollbar { height: 6px; width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { @apply bg-gray-200 rounded-full; }
</style>
