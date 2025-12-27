<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Pipeline de Vendas</h1>
        <p class="text-gray-500 mt-1">Gerencie suas oportunidades no funil</p>
      </div>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Nova Oportunidade
      </button>
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
        {{ coluna.estagio.nome }} ({{ coluna.oportunidades.length }})
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
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
                {{ coluna.oportunidades.length }}
              </span>
            </div>
            <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">
               Total: R$ {{ calcularTotalColuna(coluna.oportunidades).toLocaleString() }}
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
              v-for="oportunidade in coluna.oportunidades"
              :key="oportunidade.id"
              draggable="true"
              @dragstart="onDragStart($event, oportunidade)"
              @click="editOportunidade(oportunidade)"
              class="bg-white border border-gray-100 rounded-xl p-4 cursor-grab active:cursor-grabbing hover:shadow-md hover:border-primary-100 transition-all duration-200 group relative"
            >
              <h4 class="font-bold text-gray-900 mb-2 leading-tight group-hover:text-primary-600">{{ oportunidade.nome }}</h4>
              
              <div class="text-[11px] text-gray-500 space-y-2">
                <p class="flex items-center font-medium">
                  <svg class="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  {{ oportunidade.conta_nome }}
                </p>
                
                <div class="flex justify-between items-end mt-4">
                  <div>
                    <p v-if="oportunidade.valor_estimado" class="text-sm font-black text-green-600">
                      R$ {{ Number(oportunidade.valor_estimado).toLocaleString('pt-BR') }}
                    </p>
                    <p v-if="oportunidade.data_fechamento_esperada" class="text-[10px] font-bold text-gray-400 mt-1">
                      {{ formatDate(oportunidade.data_fechamento_esperada) }}
                    </p>
                  </div>
                  <div class="text-right">
                    <div v-if="oportunidade.probabilidade" class="w-12 h-1 bg-gray-100 rounded-full overflow-hidden mb-1">
                       <div class="h-full bg-primary-500" :style="{ width: oportunidade.probabilidade + '%' }"></div>
                    </div>
                    <span class="text-[9px] font-black text-gray-400 uppercase tracking-tighter">{{ oportunidade.probabilidade }}%</span>
                  </div>
                </div>
              </div>

              <!-- Quick Edit Icon (Desktop only hint) -->
              <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                 <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
              </div>
            </div>
            
            <!-- Empty column hint -->
            <div v-if="coluna.oportunidades.length === 0" class="h-32 border-2 border-dashed border-gray-50 rounded-xl flex items-center justify-center">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useOportunidadesStore } from '@/stores/oportunidades'
import OportunidadeModal from '@/components/OportunidadeModal.vue'

const oportunidadesStore = useOportunidadesStore()
const kanbanData = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedOportunidade = ref(null)
const draggedItem = ref(null)

const activeStage = ref(null)
const kanbanContainer = ref(null)

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
  const width = container.offsetWidth
  
  // Find which column is most visible
  const index = Math.round(scrollLeft / 280) // 280 is mobile column width
  if (kanbanData.value[index]) {
    activeStage.value = kanbanData.value[index].estagio.id
  }
}

onMounted(async () => {
  await loadKanban()
})

async function loadKanban() {
  loading.value = true
  await oportunidadesStore.fetchKanban()
  kanbanData.value = oportunidadesStore.kanbanData
  loading.value = false
}

function onDragStart(event, oportunidade) {
  draggedItem.value = oportunidade
  event.dataTransfer.effectAllowed = 'move'
}

async function onDrop(event, novoEstagioId) {
  event.preventDefault()
  
  if (!draggedItem.value) return
  
  const oportunidadeId = draggedItem.value.id
  const estagioAtualId = draggedItem.value.estagio
  
  if (estagioAtualId === novoEstagioId) return
  
  try {
    await oportunidadesStore.mudarEstagio(oportunidadeId, novoEstagioId)
    await loadKanban()
  } catch (error) {
    console.error('Erro ao mover oportunidade:', error)
    alert('Erro ao mover oportunidade')
  }
  
  draggedItem.value = null
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR')
}

function openCreateModal() {
  selectedOportunidade.value = null
  showModal.value = true
}

function editOportunidade(oportunidade) {
  selectedOportunidade.value = oportunidade
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedOportunidade.value = null
}

async function handleSaved() {
  await loadKanban()
}
</script>
