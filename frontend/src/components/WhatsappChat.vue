<template>
  <Transition name="slide">
    <div v-if="show" class="fixed inset-y-0 right-0 w-full sm:w-96 bg-white shadow-2xl z-[100] flex flex-col border-l border-gray-100">
      <!-- Header -->
      <div class="p-4 bg-emerald-600 text-white flex items-center justify-between shadow-md">
        <div class="flex items-center space-x-3">
          <div class="bg-white/20 p-2 rounded-full">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
          </div>
          <div>
            <h3 class="font-bold text-sm">{{ title }}</h3>
            <p class="text-[10px] opacity-80 uppercase tracking-wider">{{ number }}</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <!-- Botão de Sincronização -->
          <button 
            @click="syncMessages" 
            :disabled="syncing"
            class="p-2 hover:bg-white/10 rounded-full transition-colors"
            title="Sincronizar mensagens"
          >
            <svg 
              :class="['w-5 h-5', syncing ? 'animate-spin' : '']" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <!-- Botão de Fechar -->
          <button @click="$emit('close')" class="p-2 hover:bg-white/10 rounded-full transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>

      <!-- Messages Area -->
      <div ref="messageContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-[#e5ddd5] chat-bg">
        <div v-if="loading" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
        </div>
        
        <template v-else>
          <div v-if="messages.length === 0" class="text-center py-10">
            <div class="bg-white/80 inline-block px-4 py-2 rounded-lg text-xs text-gray-500 shadow-sm italic">
              Nenhuma mensagem encontrada.
            </div>
          </div>

          <div v-for="msg in messages" :key="msg.id" :class="['flex', msg.de_mim ? 'justify-end' : 'justify-start']">
            <div :class="['max-w-[85%] px-3 py-2 rounded-lg shadow-sm relative', 
                          msg.de_mim ? 'bg-[#dcf8c6] text-gray-800 rounded-tr-none' : 'bg-white text-gray-800 rounded-tl-none']">
              <p class="text-sm whitespace-pre-wrap break-words">{{ msg.texto }}</p>
              <div class="flex items-center justify-end space-x-1 mt-1">
                <span class="text-[9px] text-gray-400">{{ formatTime(msg.timestamp) }}</span>
                <svg v-if="msg.de_mim" class="w-3 h-3 text-blue-400" fill="currentColor" viewBox="0 0 24 24"><path d="M21 7L9 19l-5.5-5.5 1.41-1.41L9 16.17 19.59 5.59 21 7z"/></svg>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Input Area -->
      <div class="p-4 bg-gray-50 border-t border-gray-200">
        <form @submit.prevent="send" class="flex items-end space-x-2">
          <div class="flex-1 relative">
            <textarea
              v-model="newMessage"
              rows="1"
              @keydown.enter.exact.prevent="send"
              placeholder="Digite uma mensagem..."
              class="w-full bg-white border border-gray-200 rounded-2xl px-4 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none outline-none max-h-32 shadow-sm"
              ref="inputRef"
            ></textarea>
          </div>
          <button 
            type="submit" 
            :disabled="!newMessage.trim() || sending"
            class="p-3 bg-emerald-600 text-white rounded-full hover:bg-emerald-700 transition-all shadow-md disabled:bg-gray-300 disabled:shadow-none translate-y-[-2px]"
          >
            <svg v-if="!sending" class="w-5 h-5 rotate-90" fill="currentColor" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            <div v-else class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          </button>
        </form>
      </div>
    </div>
  </Transition>
  <div v-if="show" @click="$emit('close')" class="fixed inset-0 bg-black/20 z-[90] backdrop-blur-[1px]"></div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { whatsappService } from '@/services/whatsapp'

const props = defineProps({
  show: Boolean,
  number: String,
  title: String,
  lead: [Number, String],
  oportunidade: [Number, String]
})

const emit = defineEmits(['close'])

const messages = ref([])
const loading = ref(false)
const sending = ref(false)
const syncing = ref(false)
const newMessage = ref('')
const messageContainer = ref(null)
const inputRef = ref(null)

// Sincroniza mensagens da Evolution API para o banco local
const syncMessages = async () => {
  if (!props.number || syncing.value) return

  console.log('[WhatsappChat] Iniciando sincronização para número:', props.number)
  syncing.value = true
  try {
    const response = await whatsappService.syncMessages({
      number: props.number,
      lead: props.lead,
      oportunidade: props.oportunidade,
      limit: 50
    })

    console.log('[WhatsappChat] Sync result:', response.data)
    console.log('[WhatsappChat] Mensagens importadas:', response.data.imported)
    console.log('[WhatsappChat] Mensagens já existentes:', response.data.skipped)

    // Recarrega as mensagens do banco local
    await loadMessages()

  } catch (error) {
    console.error('[WhatsappChat] Erro ao sincronizar mensagens:', error)
  } finally {
    syncing.value = false
  }
}

const loadMessages = async () => {
  if (!props.number) return
  loading.value = true
  try {
    console.log('[WhatsappChat] Carregando mensagens para número:', props.number)
    const response = await whatsappService.getMessages({
      number: props.number,
      ordering: 'timestamp'
    })
    console.log('[WhatsappChat] Resposta da API:', response.data)
    console.log('[WhatsappChat] Total de mensagens:', response.data.results?.length || response.data.length)
    messages.value = response.data.results || response.data
    console.log('[WhatsappChat] Mensagens carregadas:', messages.value.length)
    scrollToBottom()
  } catch (error) {
    console.error('[WhatsappChat] Erro ao carregar mensagens:', error)
  } finally {
    loading.value = false
  }
}

const send = async () => {
  if (!newMessage.value.trim() || sending.value) return
  
  sending.value = true
  try {
    const response = await whatsappService.sendMessage({
      number: props.number,
      text: newMessage.value,
      lead: props.lead,
      oportunidade: props.oportunidade
    })
    
    // Adiciona localmente para feedback instantâneo
    messages.value.push(response.data)
    newMessage.value = ''
    scrollToBottom()
    
    // Foca novamente no input
    nextTick(() => inputRef.value?.focus())
  } catch (error) {
    alert('Erro ao enviar mensagem. Verifique a conexão com o WhatsApp.')
  } finally {
    sending.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

const formatTime = (ts) => {
  if (!ts) return ''
  const date = new Date(ts)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

watch(() => props.show, async (newVal) => {
  if (newVal) {
    // Primeiro sincroniza da Evolution API, depois carrega do banco local
    await syncMessages()
    nextTick(() => inputRef.value?.focus())
  }
})

// Polling para sincronizar periodicamente enquanto o chat estiver aberto
let interval = null
onMounted(() => {
  interval = setInterval(async () => {
    if (props.show && !syncing.value && !loading.value) {
      // Sincroniza a cada 15 segundos para buscar novas mensagens
      await syncMessages()
    }
  }, 15000)
})

watch(() => props.number, async () => {
  if (props.show) await syncMessages()
})
</script>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(100%);
}

.chat-bg {
  background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png');
  background-repeat: repeat;
  background-blend-mode: overlay;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.1);
  border-radius: 2px;
}
</style>
