<template>
  <div class="timeline-feed h-full flex flex-col">
    <!-- Header / Actions -->
    <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-white mb-3">Timeline</h3>
      
      <div class="flex gap-2">
        <button 
          @click="$emit('action', 'note')"
          class="flex-1 py-2 px-3 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          <i class="fas fa-sticky-note"></i> Nota
        </button>
        <button 
          @click="$emit('action', 'task')"
          class="flex-1 py-2 px-3 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          <i class="fas fa-check-square"></i> Tarefa
        </button>
        <button 
          @click="$emit('action', 'whatsapp')"
          class="flex-1 py-2 px-3 bg-green-100 hover:bg-green-200 text-green-800 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          <i class="fab fa-whatsapp"></i> Whats
        </button>
      </div>
    </div>

    <!-- Feed List -->
    <div class="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-gray-900 space-y-4">
      
      <div v-if="loading" class="flex justify-center py-8">
        <i class="fas fa-spinner fa-spin text-2xl text-blue-500"></i>
      </div>

      <div v-else-if="items.length === 0" class="text-center py-8 text-gray-500">
        <p>Nenhuma interação registrada.</p>
      </div>

      <div v-for="item in items" :key="item.id" class="timeline-item flex gap-3 group">
        
        <!-- Icon / Avatar Column -->
        <div class="flex flex-col items-center">
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center text-white shrink-0 shadow-sm z-10"
            :class="getIconClass(item)"
          >
            <i :class="getIcon(item)"></i>
          </div>
          <div class="w-0.5 h-full bg-gray-200 dark:bg-gray-700 -mt-2 group-last:hidden"></div>
        </div>

        <!-- Content Body -->
        <div class="flex-1 pb-6">
          <div class="flex justify-between items-start mb-1">
            <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              {{ formatTime(item.timestamp) }} - {{ formatDate(item.timestamp) }}
            </span>
            <span class="text-xs text-gray-400">
              {{ item.author }}
            </span>
          </div>

          <!-- Card Content based on Type -->
          <div 
            class="rounded-lg p-3 shadow-sm border transaction-all duration-200 hover:shadow-md"
            :class="getCardClass(item)"
          >
            <!-- WhatsApp -->
            <div v-if="item.type === 'whatsapp'" class="text-sm">
               <div class="flex items-center gap-2 mb-1 text-xs font-semibold opacity-75">
                  <span v-if="item.direction === 'outbound'">Enviada <i class="fas fa-arrow-right"></i></span>
                  <span v-else><i class="fas fa-arrow-left"></i> Recebida</span>
               </div>
               <p class="whitespace-pre-wrap">{{ item.content }}</p>
            </div>

            <!-- Atividade (Nota, Tarefa, etc) -->
            <div v-else-if="item.type === 'atividade'">
              <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-sm">{{ item.title }}</span>
                <span 
                  v-if="item.subtype === 'TAREFA'"
                  class="px-2 py-0.5 rounded text-xs font-bold"
                  :class="item.status === 'Concluída' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'"
                >
                  {{ item.status }}
                </span>
              </div>
              <p class="text-sm whitespace-pre-wrap">{{ item.content }}</p>
            </div>

            <!-- Log -->
            <div v-else-if="item.type === 'log'" class="text-xs">
              <p>{{ item.content }}</p>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../services/api'
// Native Date formatting used instead of date-fns to avoid build issues

const props = defineProps({
  model: {
    type: String, // 'oportunidade', 'contato', 'conta'
    required: true
  },
  id: {
    type: [String, Number],
    required: true
  }
})

const items = ref([])
const loading = ref(false)

const fetchTimeline = async () => {
  if (!props.id) return
  
  loading.value = true
  try {
    const response = await api.get(`/timeline/?model=${props.model}&id=${props.id}`)
    items.value = response.data.results
  } catch (error) {
    console.error('Erro ao buscar timeline:', error)
  } finally {
    loading.value = false
  }
}

watch(() => props.id, fetchTimeline)
onMounted(fetchTimeline)

// Helpers
const formatTime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const getIcon = (item) => {
  if (item.type === 'whatsapp') return 'fab fa-whatsapp'
  if (item.type === 'log') return 'fas fa-history'
  
  // Atividades
  switch(item.subtype) {
    case 'TAREFA': return 'fas fa-check'
    case 'LIGACAO': return 'fas fa-phone'
    case 'REUNIAO': return 'fas fa-users'
    case 'EMAIL': return 'fas fa-envelope'
    case 'NOTA': return 'fas fa-sticky-note'
    default: return 'fas fa-circle'
  }
}

const getIconClass = (item) => {
  if (item.type === 'whatsapp') return 'bg-green-500'
  if (item.type === 'log') return 'bg-gray-400'
  
  switch(item.subtype) {
    case 'TAREFA': return 'bg-blue-500'
    case 'NOTA': return 'bg-yellow-500'
    case 'LIGACAO': return 'bg-purple-500'
    case 'REUNIAO': return 'bg-orange-500'
    default: return 'bg-gray-500'
  }
}

const getCardClass = (item) => {
  if (item.type === 'whatsapp') {
    return item.direction === 'outbound' 
      ? 'bg-green-50 border-green-100 dark:bg-green-900/20 dark:border-green-800'
      : 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'
  }
  
  if (item.type === 'log') return 'bg-gray-50 border-gray-100 text-gray-500 dark:bg-gray-800/50 dark:border-gray-700'
  
  if (item.subtype === 'NOTA') return 'bg-yellow-50 border-yellow-100 dark:bg-yellow-900/10 dark:border-yellow-800'
  
  return 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'
}

defineExpose({ refresh: fetchTimeline })
</script>

<style scoped>
/* Custom Scrollbar for the feed */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
