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

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="flex gap-4 overflow-x-auto pb-4">
      <div
        v-for="coluna in kanbanData"
        :key="coluna.estagio.id"
        class="flex-shrink-0 w-80"
      >
        <div class="bg-white rounded-lg shadow-sm">
          <!-- Header da Coluna -->
          <div
            class="p-4 border-b"
            :style="{ borderTopColor: coluna.estagio.cor, borderTopWidth: '4px' }"
          >
            <h3 class="font-semibold text-gray-900">{{ coluna.estagio.nome }}</h3>
            <p class="text-sm text-gray-600 mt-1">
              {{ coluna.oportunidades.length }} oportunidade(s)
            </p>
          </div>

          <!-- Cards -->
          <div
            class="p-3 space-y-3 min-h-[400px]"
            @drop="onDrop($event, coluna.estagio.id)"
            @dragover.prevent
            @dragenter.prevent
          >
            <div
              v-for="oportunidade in coluna.oportunidades"
              :key="oportunidade.id"
              draggable="true"
              @dragstart="onDragStart($event, oportunidade)"
              class="bg-white border border-gray-200 rounded-lg p-4 cursor-move hover:shadow-md transition-shadow"
            >
              <h4 class="font-medium text-gray-900 mb-2">{{ oportunidade.nome }}</h4>
              
              <div class="text-sm text-gray-600 space-y-1">
                <p class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  {{ oportunidade.conta_nome }}
                </p>
                
                <p v-if="oportunidade.valor_estimado" class="font-semibold text-green-600">
                  R$ {{ Number(oportunidade.valor_estimado).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </p>
                
                <p v-if="oportunidade.data_fechamento_esperada" class="text-xs">
                  Prev.: {{ formatDate(oportunidade.data_fechamento_esperada) }}
                </p>
                
                <p v-if="oportunidade.probabilidade" class="text-xs">
                  Prob.: {{ oportunidade.probabilidade }}%
                </p>
              </div>

              <div class="mt-3 pt-3 border-t flex items-center justify-between">
                <span class="text-xs text-gray-500">{{ oportunidade.proprietario_nome }}</span>
                <button
                  @click="editOportunidade(oportunidade)"
                  class="text-primary-600 hover:text-primary-700"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
              </div>
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
