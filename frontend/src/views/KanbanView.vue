<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">
          {{ selectedFunil?.tipo === 'LEAD' ? 'Funil SDR (Leads)' : 'Pipeline de Vendas' }}
        </h1>
        <p class="text-gray-500 mt-1">
          {{ selectedFunil?.nome || 'Gerencie seu processo' }}
        </p>
      </div>
      
      <div class="flex flex-col sm:flex-row gap-2">
        <!-- Funnel Selector -->
        <select 
          v-model="activeFunilId" 
          @change="onFunilChange"
          class="bg-white border border-gray-200 rounded-xl px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option v-for="funil in funis" :key="funil.id" :value="funil.id">
            {{ funil.nome }}
          </option>
        </select>

        <!-- Canal Selector (For Admin) -->
        <select 
          v-if="authStore.isAdmin"
          v-model="activeCanalId" 
          @change="onCanalChange"
          class="bg-white border border-gray-200 rounded-xl px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option :value="null">Todos os Canais</option>
          <option v-for="canal in canais" :key="canal.id" :value="canal.id">
            {{ canal.nome }}
          </option>
        </select>

        <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
          {{ selectedFunil?.tipo === 'LEAD' ? '+ Novo Lead' : '+ Nova Oportunidade' }}
        </button>
      </div>
    </div>

    <!-- Mobile Stage Selector -->
    <div class="lg:hidden flex gap-2 overflow-x-auto pb-4 custom-scrollbar snap-x no-scrollbar">
      <button 
        v-for="coluna in kanbanData" 
        :key="'tab-' + coluna.estagio.id"
        @click="scrollToStage(coluna.estagio.id)"
        class="flex-shrink-0 px-4 py-2 rounded-full text-xs font-bold border transition-all whitespace-nowrap"
        :style="{ 
          borderColor: coluna.estagio.cor, 
          backgroundColor: activeStage === coluna.estagio.id ? coluna.estagio.cor : 'transparent',
          color: activeStage === coluna.estagio.id ? '#fff' : coluna.estagio.cor
        }"
      >
        {{ coluna.estagio.nome }} ({{ coluna.items.length }})
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-if="error" class="mb-4 p-4 bg-red-50 text-red-600 rounded-xl border border-red-100">
      {{ error }}
    </div>

    <div v-else 
      ref="kanbanContainer"
      class="flex gap-4 overflow-x-auto pb-8 snap-x snap-mandatory custom-scrollbar min-h-[calc(100vh-250px)]"
      @scroll="updateActiveStage"
    >
      <div
        v-for="coluna in kanbanData"
        :key="coluna.estagio.id"
        :id="'stage-' + coluna.estagio.id"
        class="flex-shrink-0 w-[280px] sm:w-80 snap-center"
      >
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 h-full flex flex-col">
          <!-- Header da Coluna -->
          <div
            class="p-4 border-b border-gray-50 bg-gray-50/30 rounded-t-2xl"
            :style="{ borderTopColor: coluna.estagio.cor, borderTopWidth: '4px' }"
          >
            <div class="flex justify-between items-center">
              <h3 class="font-bold text-gray-900 truncate">{{ coluna.estagio.nome }}</h3>
              <span class="text-[10px] font-black bg-white px-2 py-0.5 rounded-full border border-gray-100">
                {{ coluna.items.length }}
              </span>
            </div>
            <p v-if="selectedFunil?.tipo === 'OPORTUNIDADE'" class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">
               Total: R$ {{ calcularTotalColuna(coluna.items).toLocaleString() }}
            </p>
          </div>

          <!-- Cards -->
          <div
            class="p-3 space-y-3 flex-1 overflow-y-auto custom-scrollbar"
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
              class="bg-white border border-gray-100 rounded-xl p-4 cursor-grab active:cursor-grabbing hover:shadow-md hover:border-primary-100 transition-all duration-200 group relative"
            >
              <h4 class="font-bold text-gray-900 mb-2 leading-tight group-hover:text-primary-600">{{ item.nome }}</h4>
              
              <div class="text-[11px] text-gray-500 space-y-2">
                <p class="flex items-center font-medium">
                  <svg class="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path v-if="selectedFunil?.tipo === 'OPORTUNIDADE'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  {{ selectedFunil?.tipo === 'OPORTUNIDADE' ? item.conta_nome : (item.email || item.empresa || 'N/A') }}
                </p>
                
                <div v-if="selectedFunil?.tipo === 'OPORTUNIDADE'" class="flex justify-between items-end mt-4">
                  <div>
                    <p v-if="item.valor_estimado" class="text-sm font-black text-green-600">
                      R$ {{ Number(item.valor_estimado).toLocaleString('pt-BR') }}
                    </p>
                    <p v-if="item.data_fechamento_esperada" class="text-[10px] font-bold text-gray-400 mt-1">
                      {{ formatDate(item.data_fechamento_esperada) }}
                    </p>
                  </div>
                  <div class="text-right">
                    <div v-if="item.probabilidade" class="w-12 h-1 bg-gray-100 rounded-full overflow-hidden mb-1">
                       <div class="h-full bg-primary-500" :style="{ width: item.probabilidade + '%' }"></div>
                    </div>
                    <span class="text-[9px] font-black text-gray-400 uppercase tracking-tighter">{{ item.probabilidade }}%</span>
                  </div>
                </div>

                <div class="mt-4 flex flex-col space-y-1">
                   <p v-if="item.indicador_nome" class="text-[9px] font-bold text-indigo-400 uppercase tracking-tighter flex items-center">
                     <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                     Ind: {{ item.indicador_nome }}
                   </p>
                   <p class="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">{{ item.fonte || 'Fonte não informada' }}</p>
                </div>
              </div>

              <div class="absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                 <button 
                  v-if="selectedFunil?.tipo === 'OPORTUNIDADE'"
                  @click.stop="copyBillingInfo(item.id)" 
                  class="p-1 bg-white shadow-sm border border-gray-100 rounded text-indigo-500 hover:text-indigo-700 hover:border-indigo-100 transition-all"
                  title="Copiar texto de faturamento"
                 >
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m-1 4h.01M9 16h5m0 0l-1-1m1 1l-1 1" /></svg>
                 </button>
                 <button @click.stop="editItem(item)" class="p-1 bg-white shadow-sm border border-gray-100 rounded text-gray-300 hover:text-primary-500 hover:border-primary-100 transition-all">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                 </button>
                 <button 
                  @click.stop="openWhatsapp(item)" 
                  class="p-1 bg-white shadow-sm border border-gray-100 rounded text-emerald-500 hover:text-emerald-700 hover:border-emerald-100 transition-all relative"
                  title="Abrir WhatsApp"
                 >
                   <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
                   <span v-if="item.whatsapp_nao_lidas > 0" class="absolute -top-1.5 -right-1.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-red-500 text-[8px] font-black text-white ring-2 ring-white">
                     {{ item.whatsapp_nao_lidas }}
                   </span>
                 </button>
              </div>
            </div>
            
            <!-- Empty column hint -->
            <div v-if="coluna.items.length === 0" class="h-32 border-2 border-dashed border-gray-50 rounded-xl flex items-center justify-center">
               <p class="text-xs text-gray-300 font-bold uppercase tracking-widest">Vazio</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <OportunidadeModal
      :show="showModal"
      :oportunidade="selectedOportunidade"
      @close="closeModal"
      @saved="handleSaved"
    />

    <LeadModal
      :show="showLeadModal"
      :lead="selectedLead"
      :initialFunilId="activeFunilId"
      @close="showLeadModal = false"
      @saved="handleSaved"
    />

    <WhatsappChat
      :show="showWhatsapp"
      :number="whatsappData.number"
      :title="whatsappData.title"
      :lead="whatsappData.lead"
      :oportunidade="whatsappData.oportunidade"
      @close="showWhatsapp = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useOportunidadesStore } from '@/stores/oportunidades'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import OportunidadeModal from '@/components/OportunidadeModal.vue'
import LeadModal from '@/components/LeadModal.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'
import api from '@/services/api'

const authStore = useAuthStore()

const oportunidadesStore = useOportunidadesStore()
const { kanbanData, loading, error, funis } = storeToRefs(oportunidadesStore)

const activeFunilId = ref(null)
const activeCanalId = ref(null)
const canais = ref([])
const showModal = ref(false)
const showLeadModal = ref(false)
const selectedOportunidade = ref(null)
const selectedLead = ref(null)
const draggedItem = ref(null)

const showWhatsapp = ref(false)
const whatsappData = ref({
  number: '',
  title: '',
  lead: null,
  oportunidade: null
})

const activeStage = ref(null)
const kanbanContainer = ref(null)

const selectedFunil = computed(() => {
  return funis.value.find(f => f.id === activeFunilId.value) || funis.value[0]
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
  if (!kanbanContainer.value || !kanbanData.value.length) return
  const container = kanbanContainer.value
  const scrollLeft = container.scrollLeft
  
  // Find which column is most visible
  const index = Math.round(scrollLeft / 280) // 280 is mobile column width
  if (kanbanData.value[index]) {
    activeStage.value = kanbanData.value[index].estagio.id
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
  const list = await oportunidadesStore.fetchFunis()
  if (list && list.length > 0) {
    activeFunilId.value = list[0].id
    await loadKanban()
  }
}

async function loadKanban() {
  await oportunidadesStore.fetchKanban(activeFunilId.value, activeCanalId.value)
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
    if (selectedFunil.value?.tipo === 'LEAD') {
      await api.patch(`/leads/${itemId}/mudar_estagio/`, { estagio_id: novoEstagioId })
      await loadKanban()
    } else {
      await oportunidadesStore.mudarEstagio(itemId, novoEstagioId)
    }
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

function openCreateModal() {
  if (selectedFunil.value?.tipo === 'LEAD') {
    selectedLead.value = null
    showLeadModal.value = true
  } else {
    selectedOportunidade.value = null
    showModal.value = true
  }
}

function editItem(item) {
  if (selectedFunil.value?.tipo === 'LEAD') {
    selectedLead.value = item
    showLeadModal.value = true
  } else {
    selectedOportunidade.value = item
    showModal.value = true
  }
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
    alert('Erro ao gerar texto de faturamento. Verifique se o plano está selecionado na oportunidade.')
  }
}

function openWhatsapp(item) {
  const number = selectedFunil.value?.tipo === 'LEAD' ? item.telefone : item.contato_telefone
  if (!number) {
    alert('Contato sem telefone cadastrado.')
    return
  }
  
  // Remove formatação do telefone
  let cleanNumber = number.replace(/\D/g, '')
  if (!cleanNumber.startsWith('55') && cleanNumber.length <= 11) {
    cleanNumber = '55' + cleanNumber
  }

  whatsappData.value = {
    number: cleanNumber,
    title: item.nome,
    lead: selectedFunil.value?.tipo === 'LEAD' ? item.id : null,
    oportunidade: selectedFunil.value?.tipo === 'OPORTUNIDADE' ? item.id : null
  }
  showWhatsapp.value = true
}
</script>
