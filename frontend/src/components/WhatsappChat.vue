<template>
  <!-- Modo embutido: renderiza direto no layout pai sem overlay -->
  <div v-if="mode === 'embedded'" class="flex flex-col flex-1 overflow-hidden">
    <!-- Messages Area (embedded) -->
    <div 
      ref="messageContainer" 
      class="flex-1 overflow-y-auto p-4 space-y-4 bg-[#e5ddd5] chat-bg scroll-smooth"
      @scroll="handleScroll"
    >
      <!-- conteúdo reutiliza o mesmo bloco de mensagens via slot referência -->
      <div v-if="loading && messages.length === 0" class="flex justify-center py-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
      <template v-else>
        <div v-if="messages.length === 0" class="text-center py-10">
          <div class="bg-white/80 inline-block px-4 py-2 rounded-lg text-xs text-gray-500 shadow-sm italic">Nenhuma mensagem encontrada.</div>
        </div>
        <div v-for="(msg, index) in messages" :key="msg.id || index" :class="['flex', msg.de_mim ? 'justify-end' : 'justify-start']">
          <div :class="['max-w-[85%] px-3 py-2 rounded-lg shadow-sm relative', msg.de_mim ? 'bg-[#dcf8c6] text-gray-800 rounded-tr-none' : 'bg-white text-gray-800 rounded-tl-none']">
            <div v-if="msg.tipo_mensagem === 'image' && msg.media_base64" class="mb-2">
              <img :src="msg.media_base64" alt="Imagem" class="max-w-full max-h-64 rounded-lg cursor-pointer hover:opacity-90 transition-opacity" @click="openImage(msg.media_base64)" />
            </div>
            <div v-if="msg.tipo_mensagem === 'audio'" class="mb-2">
              <audio v-if="audioUrls[msg.id]" :src="audioUrls[msg.id]" controls class="w-full max-w-[200px] sm:max-w-[250px] h-8"></audio>
              <div class="flex items-center space-x-2 mt-1">
                <button v-if="isAudioPending(msg)" @click="handleTranscribeAudio(msg)" :disabled="transcribingId === msg.id" class="text-xs bg-emerald-500 hover:bg-emerald-600 text-white px-2 py-1 rounded-full flex items-center space-x-1 disabled:opacity-50 transition-colors">
                  <span>{{ transcribingId === msg.id ? 'Transcrevendo...' : 'Transcrever' }}</span>
                </button>
                <button v-if="!audioUrls[msg.id]" @click="handlePlayAudio(msg)" :disabled="loadingAudioId === msg.id" class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded-full flex items-center space-x-1 disabled:opacity-50 transition-colors">
                  <span>{{ loadingAudioId === msg.id ? 'Carregando...' : 'Ouvir' }}</span>
                </button>
              </div>
            </div>
            <p v-if="!(msg.tipo_mensagem === 'image' && msg.media_base64 && msg.texto?.startsWith('📷'))" class="text-sm whitespace-pre-wrap break-words">{{ msg.texto }}</p>
            <div class="flex items-center justify-end space-x-1 mt-1">
              <span class="text-[9px] text-gray-400">{{ formatTime(msg.timestamp) }}</span>
              <svg v-if="msg.de_mim" class="w-3 h-3 text-blue-400" fill="currentColor" viewBox="0 0 24 24"><path d="M21 7L9 19l-5.5-5.5 1.41-1.41L9 16.17 19.59 5.59 21 7z"/></svg>
            </div>
          </div>
        </div>
      </template>
    </div>
    <!-- Input Area (embedded) -->
    <div class="p-3 bg-gray-50 border-t border-gray-200">
      <div v-if="selectedImage" class="mb-2 relative inline-block">
        <img :src="selectedImagePreview" class="h-16 w-16 object-cover rounded-lg border-2 border-emerald-500" />
        <button @click="clearImage" class="absolute -top-1.5 -right-1.5 bg-red-500 text-white rounded-full w-4 h-4 flex items-center justify-center text-[10px]">✕</button>
      </div>
      <form @submit.prevent="send" class="flex items-end space-x-2">
        <button type="button" @click="triggerFileInput" :disabled="sending" class="p-2 text-gray-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-full transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
        </button>
        <input type="file" ref="fileInput" @change="handleFileSelect" accept="image/*" class="hidden" />
        <div class="flex-1">
          <textarea v-model="newMessage" rows="1" @keydown.enter.exact.prevent="send" :placeholder="selectedImage ? 'Legenda...' : 'Digite uma mensagem...'" class="w-full bg-white border border-gray-200 rounded-2xl px-4 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none outline-none max-h-32 shadow-sm" ref="inputRef"></textarea>
        </div>
        <button type="submit" :disabled="(!newMessage.trim() && !selectedImage) || sending" class="p-2.5 bg-emerald-600 text-white rounded-full hover:bg-emerald-700 transition-all shadow-md disabled:bg-gray-300">
          <svg v-if="!sending" class="w-4 h-4 rotate-90" fill="currentColor" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          <div v-else class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
        </button>
      </form>
    </div>
  </div>

  <!-- Modo Drawer (original) -->
  <Transition v-else name="slide">
    <div v-if="show" class="fixed inset-y-0 right-0 w-full sm:w-80 md:w-96 lg:w-[28rem] bg-white shadow-2xl z-[100] flex flex-col border-l border-gray-100">
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
            :aria-label="syncing ? 'Sincronizando mensagens' : 'Sincronizar mensagens do WhatsApp'"
            title="Sincronizar mensagens"
            class="p-2 hover:bg-white/10 rounded-full transition-colors disabled:opacity-50"
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
          <button
            @click="$emit('close')"
            aria-label="Fechar chat do WhatsApp"
            title="Fechar chat"
            class="p-2 hover:bg-white/10 rounded-full transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>
      
      <!-- Seletor de Contexto (Novidade) -->
      <div v-if="oportunidadesAtivas.length > 1" class="bg-gray-100 p-2 border-b flex items-center justify-between shadow-inner">
        <div class="flex items-center space-x-2 overflow-hidden">
          <div :class="['w-2 h-2 rounded-full shadow-sm', getTipoCor(currentOportunidade?.funil_tipo)]"></div>
          <span class="text-[10px] font-bold text-gray-600 truncate">
            {{ currentOportunidade?.nome }} 
            <span class="font-normal opacity-60">({{ currentOportunidade?.estagio_nome }})</span>
          </span>
        </div>
        <button 
          @click="showContextSelector = !showContextSelector" 
          class="text-[10px] bg-white border border-gray-200 px-2 py-0.5 rounded shadow-sm hover:bg-gray-50 text-emerald-600 font-bold transition-all"
        >
          {{ showContextSelector ? 'FECHAR' : 'TROCAR' }}
        </button>
      </div>

      <!-- Lista de Oportunidades para Troca -->
      <div v-if="showContextSelector" class="bg-white border-b max-h-48 overflow-y-auto shadow-lg z-10 animate-fade-in">
        <div 
          v-for="opp in oportunidadesAtivas" 
          :key="opp.id"
          @click="switchOportunidade(opp)"
          :class="['p-3 border-b last:border-0 cursor-pointer hover:bg-emerald-50 transition-colors flex items-center justify-between',
                   currentOportunidadeId == opp.id ? 'bg-emerald-50 border-l-4 border-l-emerald-500' : '']"
        >
          <div>
            <div class="text-xs font-bold text-gray-800">{{ opp.nome }}</div>
            <div class="text-[10px] text-gray-500 flex items-center space-x-1">
              <span>{{ opp.funil_nome }}</span>
              <span>•</span>
              <span :style="{ color: opp.estagio_cor }" class="font-medium">{{ opp.estagio_nome }}</span>
            </div>
          </div>
          <div v-if="currentOportunidadeId == opp.id" class="text-emerald-600">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
          </div>
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
                  class="w-full max-w-[200px] sm:max-w-[250px] h-8"
                  aria-label="Player de áudio do WhatsApp"
                ></audio>

                <!-- Botões de ação para áudio -->
                <div class="flex items-center space-x-2 mt-1">
                  <!-- Botão Transcrever (apenas se não foi transcrito ainda) -->
                  <button
                    v-if="isAudioPending(msg)"
                    @click="handleTranscribeAudio(msg)"
                    :disabled="transcribingId === msg.id"
                    :aria-label="transcribingId === msg.id ? 'Transcrevendo áudio' : 'Transcrever áudio para texto'"
                    title="Transcrever áudio para texto"
                    class="text-xs bg-emerald-500 hover:bg-emerald-600 text-white px-2 py-1 rounded-full flex items-center space-x-1 disabled:opacity-50 transition-colors"
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

                  <!-- Botão Ouvir/Carregar áudio -->
                  <button
                    v-if="!audioUrls[msg.id]"
                    @click="handlePlayAudio(msg)"
                    :disabled="loadingAudioId === msg.id"
                    :aria-label="loadingAudioId === msg.id ? 'Carregando áudio' : 'Carregar e reproduzir áudio'"
                    title="Carregar áudio para reprodução"
                    class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded-full flex items-center space-x-1 disabled:opacity-50 transition-colors"
                  >
                    <svg v-if="loadingAudioId !== msg.id" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <svg v-else class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    <span>{{ loadingAudioId === msg.id ? 'Carregando...' : 'Ouvir' }}</span>
                  </button>
                </div>
              </div>
              
              <!-- Texto ou Caption (omite placeholder quando a imagem já está visível) -->
              <p
                v-if="!(msg.tipo_mensagem === 'image' && msg.media_base64 && msg.texto?.startsWith('📷'))"
                class="text-sm whitespace-pre-wrap break-words"
              >{{ msg.texto }}</p>

              <!-- Reações -->
              <div v-if="msg.reacoes && msg.reacoes.length" class="flex flex-wrap gap-1 mt-1.5 -mb-0.5">
                <span
                  v-for="(r, i) in msg.reacoes"
                  :key="i"
                  :title="r.de_mim ? 'Você' : 'Contato'"
                  class="inline-flex items-center bg-white/90 border border-gray-200 rounded-full px-1.5 py-0.5 text-sm shadow-sm leading-none"
                >{{ r.emoji }}</span>
              </div>

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
        <!-- Preview da imagem selecionada -->
        <div v-if="selectedImage" class="mb-3 relative inline-block">
          <img :src="selectedImagePreview" class="h-20 w-20 object-cover rounded-lg border-2 border-emerald-500" />
          <button 
            @click="clearImage" 
            class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
            title="Remover imagem"
          >
            ✕
          </button>
        </div>
        
        <form @submit.prevent="send" class="flex items-end space-x-2" aria-label="Formulário de envio de mensagem">
          <!-- Botão de Anexo -->
          <button
            type="button"
            @click="triggerFileInput"
            :disabled="sending"
            title="Enviar imagem"
            class="p-3 text-gray-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-full transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </button>
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileSelect" 
            accept="image/*" 
            class="hidden" 
          />
          
          <div class="flex-1 relative">
            <textarea
              v-model="newMessage"
              rows="1"
              @keydown.enter.exact.prevent="send"
              :placeholder="selectedImage ? 'Legenda da imagem (opcional)...' : 'Digite uma mensagem...'"
              aria-label="Campo de texto para digitar mensagem"
              class="w-full bg-white border border-gray-200 rounded-2xl px-4 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none outline-none max-h-32 shadow-sm"
              ref="inputRef"
            ></textarea>
          </div>
          <button
            type="submit"
            :disabled="(!newMessage.trim() && !selectedImage) || sending"
            :aria-label="sending ? 'Enviando mensagem' : 'Enviar mensagem'"
            title="Enviar mensagem"
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
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { whatsappService } from '@/services/whatsapp'
import api from '@/services/api'

const props = defineProps({
  show: { type: Boolean, default: false },
  number: String,
  title: String,
  oportunidade: [Number, String],
  mode: { type: String, default: 'drawer' },  // 'drawer' | 'embedded'
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

// Multicontexto
const currentOportunidadeId = ref(props.oportunidade)
const oportunidadesAtivas = ref([])
const showContextSelector = ref(false)

const currentOportunidade = computed(() => {
  return oportunidadesAtivas.value.find(o => o.id == currentOportunidadeId.value)
})

// Controle de áudios
const transcribingId = ref(null)
const loadingAudioId = ref(null)
const audioUrls = ref({})

// Controle de imagens
const fileInput = ref(null)
const selectedImage = ref(null)
const selectedImagePreview = ref('')

// Cache de áudios no localStorage
const AUDIO_CACHE_PREFIX = 'whatsapp_audio_'
const AUDIO_CACHE_MAX_AGE = 7 * 24 * 60 * 60 * 1000 // 7 dias

// Carrega áudio do cache
const loadAudioFromCache = (messageId) => {
  try {
    const cached = localStorage.getItem(AUDIO_CACHE_PREFIX + messageId)
    if (!cached) return null

    const data = JSON.parse(cached)
    const now = Date.now()

    // Verifica se ainda é válido
    if (now - data.timestamp > AUDIO_CACHE_MAX_AGE) {
      localStorage.removeItem(AUDIO_CACHE_PREFIX + messageId)
      return null
    }

    return data.url
  } catch (error) {
    console.error('[AudioCache] Erro ao carregar do cache:', error)
    return null
  }
}

// Salva áudio no cache
const saveAudioToCache = (messageId, url) => {
  try {
    const data = {
      url: url,
      timestamp: Date.now()
    }
    localStorage.setItem(AUDIO_CACHE_PREFIX + messageId, JSON.stringify(data))
  } catch (error) {
    console.error('[AudioCache] Erro ao salvar no cache:', error)
    // Se der erro (quota exceeded), limpa áudios antigos
    cleanOldAudioCache()
  }
}

// Limpa áudios antigos do cache
const cleanOldAudioCache = () => {
  try {
    const now = Date.now()
    const keysToRemove = []

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith(AUDIO_CACHE_PREFIX)) {
        const data = JSON.parse(localStorage.getItem(key))
        if (now - data.timestamp > AUDIO_CACHE_MAX_AGE) {
          keysToRemove.push(key)
        }
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key))
  } catch (error) {
    console.error('[AudioCache] Erro ao limpar cache:', error)
  }
}

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
      oportunidade: currentOportunidadeId.value,
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
      oportunidade: currentOportunidadeId.value
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

    // Comparação rápida: só atualiza se quantidade ou última msg mudou
    const lastNew = newMessages[newMessages.length - 1]
    const lastOld = messages.value[messages.value.length - 1]
    const changed = newMessages.length !== messages.value.length ||
      (lastNew?.id !== lastOld?.id)

    if (changed) {
      const hadMessages = messages.value.length > 0
      const wasAtBottom = isAtBottom.value || !hadMessages

      messages.value = newMessages

      // Carrega áudios apenas das últimas 20 mensagens para evitar travamento
      nextTick(() => {
        const recentMsgs = newMessages.slice(-20)
        recentMsgs.forEach(msg => {
          if (msg.tipo_mensagem === 'audio' && !audioUrls.value[msg.id]) {
            if (msg.media_base64) {
              audioUrls.value[msg.id] = msg.media_base64
            } else {
              const cachedUrl = loadAudioFromCache(msg.id)
              if (cachedUrl) {
                audioUrls.value[msg.id] = cachedUrl
              }
            }
          }
        })
      })

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

// Funções de upload de imagem
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Verifica se é imagem
  if (!file.type.startsWith('image/')) {
    alert('Por favor, selecione apenas imagens.')
    return
  }
  
  // Limita tamanho a 5MB
  if (file.size > 5 * 1024 * 1024) {
    alert('A imagem deve ter no máximo 5MB.')
    return
  }
  
  selectedImage.value = file
  
  // Cria preview
  const reader = new FileReader()
  reader.onload = (e) => {
    selectedImagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const clearImage = () => {
  selectedImage.value = null
  selectedImagePreview.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

const send = async () => {
  // Verifica se tem algo para enviar
  if ((!newMessage.value.trim() && !selectedImage.value) || sending.value) return
  
  sending.value = true
  try {
    let response
    
    if (selectedImage.value) {
      // Envia imagem
      const reader = new FileReader()
      const base64 = await new Promise((resolve) => {
        reader.onload = () => resolve(reader.result)
        reader.readAsDataURL(selectedImage.value)
      })
      
      response = await whatsappService.sendMedia({
        number: props.number,
        media: base64,
        mediaType: 'image',
        fileName: selectedImage.value.name,
        caption: newMessage.value,
        oportunidade: props.oportunidade
      })
      
      clearImage()
    } else {
      // Envia texto
      response = await whatsappService.sendMessage({
        number: props.number,
        text: newMessage.value,
        oportunidade: currentOportunidadeId.value
      })
    }
    
    // Adiciona localmente para feedback instantâneo
    messages.value.push(response.data)
    newMessage.value = ''
    scrollToBottom()
    
    // Foca novamente no input
    nextTick(() => inputRef.value?.focus())
  } catch (error) {
    console.error('[WhatsappChat] Erro ao enviar:', error)
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

// Verifica se um áudio está pendente de transcrição (usa regex para maior precisão)
const isAudioPending = (msg) => {
  if (msg.tipo_mensagem !== 'audio') return false
  const texto = msg.texto || ''
  // Detecta se já foi transcrito (formato: "🎤 [Áudio Xs]: texto..." onde X é número de segundos)
  return !/🎤\s*\[Áudio\s+\d+s\]:/.test(texto)
}

// Mensagens de erro amigáveis
const getErrorMessage = (errorCode) => {
  const errorMessages = {
    'could_not_download_audio': 'Não foi possível baixar o áudio do servidor. Verifique sua conexão.',
    'transcription_empty': 'O áudio não contém fala reconhecível ou está muito baixo.',
    'message not found': 'Mensagem não encontrada no banco de dados.',
    'message is not audio': 'Esta mensagem não é um áudio.',
    'timeout': 'Tempo limite excedido. O áudio pode ser muito longo.'
  }
  return errorMessages[errorCode] || 'Erro ao processar áudio. Tente novamente.'
}

// Reproduz um áudio (baixa sem transcrever)
const handlePlayAudio = async (msg) => {
  if (loadingAudioId.value === msg.id) return

  // Verifica se já tem no cache local
  const cachedUrl = loadAudioFromCache(msg.id)
  if (cachedUrl) {
    console.log('[WhatsappChat] Áudio carregado do cache:', msg.id)
    audioUrls.value[msg.id] = cachedUrl
    return
  }

  // Verifica se já está carregado na memória
  if (audioUrls.value[msg.id]) {
    return
  }

  loadingAudioId.value = msg.id

  try {
    const response = await whatsappService.getAudio(msg.id)
    console.log('[WhatsappChat] Áudio baixado:', response.data)

    if (response.data.success && response.data.audio_url) {
      audioUrls.value[msg.id] = response.data.audio_url
      saveAudioToCache(msg.id, response.data.audio_url)
    } else {
      const errorMsg = getErrorMessage(response.data.error)
      alert(errorMsg)
    }
  } catch (error) {
    console.error('[WhatsappChat] Erro ao baixar áudio:', error)
    const errorMsg = error.code === 'ECONNABORTED'
      ? getErrorMessage('timeout')
      : getErrorMessage(error.response?.data?.error || 'unknown')
    alert(errorMsg)
  } finally {
    loadingAudioId.value = null
  }
}

// Transcreve um áudio específico
const handleTranscribeAudio = async (msg) => {
  if (transcribingId.value === msg.id) return

  transcribingId.value = msg.id

  try {
    const response = await whatsappService.transcribeAudio(msg.id)
    console.log('[WhatsappChat] Resposta transcrição:', response.data)

    if (response.data.success) {
      // Atualiza o URL do áudio para reprodução
      if (response.data.audio_url) {
        audioUrls.value[msg.id] = response.data.audio_url
        saveAudioToCache(msg.id, response.data.audio_url)
      }

      // Atualiza o texto da mensagem localmente se foi transcrito
      if (response.data.updated_text && response.data.transcription) {
        const msgIndex = messages.value.findIndex(m => m.id === msg.id)
        console.log('[WhatsappChat] Atualizando mensagem index:', msgIndex, 'texto:', response.data.updated_text)
        if (msgIndex !== -1) {
          // Força reatividade criando novo objeto
          messages.value[msgIndex] = {
            ...messages.value[msgIndex],
            texto: response.data.updated_text
          }
        }
      } else if (response.data.error) {
        // Mostra erro amigável se a transcrição falhou
        const errorMsg = getErrorMessage(response.data.error)
        alert(errorMsg)

        // Mas ainda carrega o áudio para reprodução
        if (response.data.audio_url) {
          audioUrls.value[msg.id] = response.data.audio_url
          saveAudioToCache(msg.id, response.data.audio_url)
        }
      }
    }
  } catch (error) {
    console.error('[WhatsappChat] Erro ao transcrever áudio:', error)
    const errorMsg = error.code === 'ECONNABORTED'
      ? getErrorMessage('timeout')
      : getErrorMessage(error.response?.data?.error || 'unknown')
    alert(errorMsg)
  } finally {
    transcribingId.value = null
  }
}

const getTipoCor = (tipo) => {
  switch (tipo) {
    case 'VENDAS': return 'bg-blue-500'
    case 'POS_VENDA': return 'bg-purple-500'
    case 'SUPORTE': return 'bg-orange-500'
    default: return 'bg-gray-400'
  }
}

const switchOportunidade = async (opp) => {
  currentOportunidadeId.value = opp.id
  showContextSelector.value = false
  messages.value = []
  await loadMessages()
  await syncMessages()
}

const loadOportunidades = async () => {
  if (!props.number) return
  try {
    // Busca oportunidades vinculadas ao número do contato
    const response = await api.get('/oportunidades/', { 
      params: { 
        search: props.number,
        page_size: 10
      } 
    })
    oportunidadesAtivas.value = response.data.results || []
    
    // Se não tiver ID atual, pega a primeira
    if (!currentOportunidadeId.value && oportunidadesAtivas.value.length > 0) {
      currentOportunidadeId.value = oportunidadesAtivas.value[0].id
    }
  } catch (error) {
    console.error('[WhatsappChat] Erro ao carregar processos:', error)
  }
}

watch(() => props.show, async (newVal) => {
  if (newVal) {
    // Reset state
    currentOportunidadeId.value = props.oportunidade
    showContextSelector.value = false
    
    // 1) Carrega mensagens locais PRIMEIRO (rápido, não bloqueia UI)
    await loadMessages()
    scrollToBottom()
    nextTick(() => inputRef.value?.focus())

    // 2) Tarefas pesadas em background (não bloqueiam a UI)
    loadOportunidades().catch(() => {})
    syncMessages().then(() => {
      // Processa mídias pendentes após sync
      whatsappService.processPendingMedia(props.number).then(mediaResult => {
        if (mediaResult.data.processed_audio > 0 || mediaResult.data.processed_images > 0) {
          loadMessages(true)
        }
      }).catch(() => {})
    }).catch(() => {})
  }
})

// Polling para atualizar o chat com o que o Webhook insere no banco
let interval = null
onMounted(async () => {
  // Em modo embedded, watch(show) nunca dispara (show=true fixo).
  // Carregamos as mensagens aqui mesmo na montagem inicial.
  if (props.mode === 'embedded' && props.number) {
    await loadMessages()
    scrollToBottom()
    nextTick(() => inputRef.value?.focus())
    loadOportunidades().catch(() => {})
    syncMessages().then(() => {
      whatsappService.processPendingMedia(props.number).then(mediaResult => {
        if (mediaResult.data.processed_audio > 0 || mediaResult.data.processed_images > 0) {
          loadMessages(true)
        }
      }).catch(() => {})
    }).catch(() => {})
  }

  interval = setInterval(async () => {
    if (props.show && !loading.value && !syncing.value) {
      const oldLength = messages.value.length
      await loadMessages(true)

      if (messages.value.length > oldLength) {
        const hasNewReceived = messages.value.slice(oldLength).some(m => !m.de_mim)
        if (hasNewReceived) {
          markAsRead().catch(() => {})
        }
      }
    }
  }, 10000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

// Troca de contato no modo embedded: fast load primeiro, sync em background
watch(() => props.number, async (newNum, oldNum) => {
  if (newNum && newNum !== oldNum) {
    messages.value = []
    currentOportunidadeId.value = props.oportunidade
    showContextSelector.value = false

    await loadMessages()
    scrollToBottom()

    loadOportunidades().catch(() => {})
    syncMessages().then(() => {
      whatsappService.processPendingMedia(props.number).then(mediaResult => {
        if (mediaResult.data.processed_audio > 0 || mediaResult.data.processed_images > 0) {
          loadMessages(true)
        }
      }).catch(() => {})
    }).catch(() => {})
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
