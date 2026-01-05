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
      <div 
        ref="messageContainer" 
        class="flex-1 overflow-y-auto p-4 space-y-4 bg-[#e5ddd5] chat-bg scroll-smooth"
        @scroll="handleScroll"
      >
        <div v-if="loading && messages.length === 0" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
        </div>
        
        <template v-else>
          <div v-if="messages.length === 0" class="text-center py-10">
            <div class="bg-white/80 inline-block px-4 py-2 rounded-lg text-xs text-gray-500 shadow-sm italic">
              Nenhuma mensagem encontrada.
            </div>
          </div>

          <div 
            v-for="(msg, index) in messages" 
            :key="msg.id || index" 
            :class="['flex', msg.de_mim ? 'justify-end' : 'justify-start']"
          >
            <div :class="['max-w-[85%] px-3 py-2 rounded-lg shadow-sm relative', 
                          msg.de_mim ? 'bg-[#dcf8c6] text-gray-800 rounded-tr-none' : 'bg-white text-gray-800 rounded-tl-none']">
              
              <!-- Imagem -->
              <div v-if="msg.tipo_mensagem === 'image' && msg.media_base64" class="mb-2">
                <img 
                  :src="msg.media_base64" 
                  alt="Imagem" 
                  class="max-w-full max-h-64 rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                  @click="openImage(msg.media_base64)"
                />
              </div>
              
              <!-- Áudio com controles -->
              <div v-if="msg.tipo_mensagem === 'audio'" class="mb-2">
                <!-- Player de áudio (se disponível) -->
                <audio 
                  v-if="audioUrls[msg.id]" 
                  :src="audioUrls[msg.id]" 
                  controls 
                  class="w-full max-w-[250px] h-8"
                ></audio>
                
                <!-- Botões de ação para áudio não transcrito -->
                <div v-if="isAudioPending(msg)" class="flex items-center space-x-2 mt-1">
                  <button 
                    @click="handleTranscribeAudio(msg)"
                    :disabled="transcribingId === msg.id"
                    class="text-xs bg-emerald-500 hover:bg-emerald-600 text-white px-2 py-1 rounded-full flex items-center space-x-1 disabled:opacity-50"
                  >
                    <svg v-if="transcribingId !== msg.id" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                    </svg>
                    <svg v-else class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    <span>{{ transcribingId === msg.id ? 'Transcrevendo...' : 'Transcrever' }}</span>
                  </button>
                  
                  <button 
                    v-if="!audioUrls[msg.id]"
                    @click="handleTranscribeAudio(msg, true)"
                    :disabled="transcribingId === msg.id"
                    class="text-xs bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded-full flex items-center space-x-1 disabled:opacity-50"
                  >
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>Ouvir</span>
                  </button>
                </div>
              </div>
              
              <!-- Texto ou Caption -->
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

const emit = defineEmits(['close', 'messagesRead'])

const messages = ref([])
const loading = ref(false)
const sending = ref(false)
const syncing = ref(false)
const newMessage = ref('')
const messageContainer = ref(null)
const inputRef = ref(null)
const isAtBottom = ref(true)

// Controle de áudios
const transcribingId = ref(null)
const audioUrls = ref({})

// Detecta se o usuário está no final do scroll
const handleScroll = () => {
  if (!messageContainer.value) return
  const { scrollTop, scrollHeight, clientHeight } = messageContainer.value
  const threshold = 100 // pixels do fundo
  isAtBottom.value = scrollHeight - scrollTop - clientHeight < threshold
}

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

    // Marca como lidas após sincronizar (se houver mensagens novas)
    await markAsRead()

  } catch (error) {
    console.error('[WhatsappChat] Erro ao sincronizar mensagens:', error)
  } finally {
    syncing.value = false
  }
}

const markAsRead = async () => {
  try {
    const response = await whatsappService.marcarLidas({
      number: props.number,
      lead: props.lead,
      oportunidade: props.oportunidade
    })
    // Se marcou mensagens novas como lidas, avisa o layout para atualizar o contador
    if (response.data.updated_count > 0) {
      emit('messagesRead')
    }
  } catch (error) {
    console.error('[WhatsappChat] Erro ao marcar como lidas:', error)
  }
}

const loadMessages = async (silent = false) => {
  if (!props.number) return
  if (!silent) loading.value = true
  
  try {
    const response = await whatsappService.getMessages({
      number: props.number,
      ordering: 'timestamp'
    })
    
    const newMessages = response.data.results || response.data
    
    // Só atualiza se houver mudança real para evitar re-renders desnecessários
    if (JSON.stringify(newMessages) !== JSON.stringify(messages.value)) {
      const hadMessages = messages.value.length > 0
      const wasAtBottom = isAtBottom.value || !hadMessages
      
      messages.value = newMessages
      
      // Rola para o fundo apenas se o usuário já estava lá ou se é o primeiro load
      if (wasAtBottom) {
        scrollToBottom()
      }
    }
  } catch (error) {
    console.error('[WhatsappChat] Erro ao carregar mensagens:', error)
  } finally {
    if (!silent) loading.value = false
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

const openImage = (base64) => {
  // Abre a imagem em uma nova aba
  const win = window.open()
  if (win) {
    win.document.write(`<img src="${base64}" style="max-width: 100%; height: auto;">`)
    win.document.title = 'Imagem WhatsApp'
  }
}

// Verifica se um áudio está pendente de transcrição
const isAudioPending = (msg) => {
  if (msg.tipo_mensagem !== 'audio') return false
  const pendingTexts = ['🎤 [Áudio]', '🎤 [Áudio não transcrito]', '[audioMessage]']
  return pendingTexts.some(t => msg.texto === t || msg.texto?.startsWith(t))
}

// Transcreve um áudio específico
const handleTranscribeAudio = async (msg, onlyPlay = false) => {
  if (transcribingId.value === msg.id) return
  
  transcribingId.value = msg.id
  
  try {
    const response = await whatsappService.transcribeAudio(msg.id)
    
    if (response.data.success) {
      // Atualiza o URL do áudio para reprodução
      if (response.data.audio_url) {
        audioUrls.value[msg.id] = response.data.audio_url
      }
      
      // Atualiza o texto da mensagem localmente
      if (response.data.updated_text && !onlyPlay) {
        const msgIndex = messages.value.findIndex(m => m.id === msg.id)
        if (msgIndex !== -1) {
          messages.value[msgIndex].texto = response.data.updated_text
        }
      }
    }
  } catch (error) {
    console.error('[WhatsappChat] Erro ao transcrever áudio:', error)
    alert('Erro ao processar áudio. Tente novamente.')
  } finally {
    transcribingId.value = null
  }
}

watch(() => props.show, async (newVal) => {
  if (newVal) {
    // Primeiro sincroniza da Evolution API, depois carrega do banco local
    await syncMessages()
    
    // Processa mídias pendentes (áudios não transcritos, imagens sem preview)
    try {
      const mediaResult = await whatsappService.processPendingMedia(props.number)
      if (mediaResult.data.processed_audio > 0 || mediaResult.data.processed_images > 0) {
        console.log('[WhatsappChat] Mídias processadas:', mediaResult.data)
        // Recarrega mensagens para pegar as atualizações
        await loadMessages()
      }
    } catch (error) {
      console.error('[WhatsappChat] Erro ao processar mídias:', error)
    }
    
    scrollToBottom()
    nextTick(() => inputRef.value?.focus())
  }
})

// Polling para atualizar o chat com o que o Webhook insere no banco
let interval = null
onMounted(() => {
  interval = setInterval(async () => {
    if (props.show && !loading.value && !syncing.value) {
      // Busca no banco local de forma silenciosa
      const oldLength = messages.value.length
      await loadMessages(true) // silent=true
      
      if (messages.value.length > oldLength) {
        const hasNewReceived = messages.value.slice(oldLength).some(m => !m.de_mim)
        if (hasNewReceived) {
          await markAsRead()
        }
      }
    }
  }, 5000)
})

// Sincronização PESADA (com a API externa) apenas no início ou se o número mudar
watch(() => props.number, async (newNum) => {
  if (props.show && newNum) {
    await syncMessages()
  }
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
