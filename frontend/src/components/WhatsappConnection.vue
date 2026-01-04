<template>
  <div class="whatsapp-connection bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 bg-gradient-to-r from-emerald-600 to-emerald-500 text-white">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-white/20 rounded-lg">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/>
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-lg">Conexão WhatsApp</h3>
            <p class="text-xs opacity-80">Gerencie a conexão com o WhatsApp</p>
          </div>
        </div>
        <button 
          @click="checkStatus" 
          :disabled="loading"
          class="p-2 hover:bg-white/10 rounded-full transition-colors"
          title="Atualizar status"
        >
          <svg :class="['w-5 h-5', loading ? 'animate-spin' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      <!-- Status da Conexão -->
      <div class="mb-6">
        <div class="flex items-center justify-between p-4 rounded-lg" 
             :class="isConnected ? 'bg-emerald-50 border border-emerald-200' : 'bg-amber-50 border border-amber-200'">
          <div class="flex items-center space-x-3">
            <div :class="['w-3 h-3 rounded-full', isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500']"></div>
            <div>
              <p class="font-medium" :class="isConnected ? 'text-emerald-800' : 'text-amber-800'">
                {{ isConnected ? 'Conectado' : 'Desconectado' }}
              </p>
              <p class="text-xs" :class="isConnected ? 'text-emerald-600' : 'text-amber-600'">
                Instância: {{ instanceName }}
              </p>
            </div>
          </div>
          <span class="text-xs px-2 py-1 rounded-full font-medium"
                :class="isConnected ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">
            {{ connectionState }}
          </span>
        </div>
      </div>

      <!-- QR Code (quando desconectado) -->
      <div v-if="!isConnected && showQRCode" class="mb-6">
        <div class="text-center">
          <p class="text-gray-600 mb-4">Escaneie o QR Code com seu WhatsApp</p>
          
          <div v-if="qrLoading" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
          </div>
          
          <div v-else-if="qrBase64" class="inline-block p-4 bg-white rounded-xl shadow-lg border">
            <img :src="qrBase64" alt="QR Code" class="w-64 h-64" />
          </div>
          
          <div v-else-if="qrError" class="text-red-500 text-sm py-4">
            {{ qrError }}
          </div>

          <p class="text-xs text-gray-400 mt-4">
            O QR Code expira em alguns segundos. Clique em "Gerar QR Code" para atualizar.
          </p>

          <!-- Polling indicator -->
          <div v-if="polling" class="mt-2 flex items-center justify-center space-x-2 text-emerald-600">
            <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span class="text-xs">Aguardando conexão...</span>
          </div>
        </div>
      </div>

      <!-- Botões de Ação -->
      <div class="flex flex-wrap gap-3">
        <button 
          v-if="!isConnected"
          @click="generateQRCode"
          :disabled="qrLoading"
          class="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:bg-gray-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
          </svg>
          <span>{{ qrLoading ? 'Gerando...' : 'Gerar QR Code' }}</span>
        </button>

        <button 
          v-if="isConnected"
          @click="disconnectWhatsApp"
          :disabled="loading"
          class="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:bg-gray-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Desconectar</span>
        </button>

        <button 
          @click="restartInstance"
          :disabled="loading"
          class="flex items-center justify-center space-x-2 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:bg-gray-50"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Reiniciar</span>
        </button>
      </div>

      <!-- Mensagem de erro -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { whatsappService } from '@/services/whatsapp'

const loading = ref(false)
const qrLoading = ref(false)
const polling = ref(false)
const error = ref('')
const qrError = ref('')

const connectionStatus = ref({
  connected: false,
  state: 'unknown',
  instance: ''
})

const qrBase64 = ref('')
const showQRCode = ref(false)

let pollingInterval = null

const isConnected = computed(() => connectionStatus.value.connected)
const connectionState = computed(() => connectionStatus.value.state || 'unknown')
const instanceName = computed(() => connectionStatus.value.instance || 'N/A')

const checkStatus = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await whatsappService.getStatus()
    connectionStatus.value = response.data
    
    // Se conectou, para o polling e limpa o QR
    if (response.data.connected) {
      stopPolling()
      qrBase64.value = ''
      showQRCode.value = false
    }
  } catch (e) {
    error.value = 'Erro ao verificar status: ' + (e.response?.data?.error || e.message)
  } finally {
    loading.value = false
  }
}

const generateQRCode = async () => {
  qrLoading.value = true
  qrError.value = ''
  showQRCode.value = true
  
  try {
    const response = await whatsappService.connect()
    
    if (response.data.already_connected) {
      connectionStatus.value = response.data.status
      showQRCode.value = false
      return
    }
    
    // Processa o QR Code
    if (response.data.qr_base64) {
      qrBase64.value = response.data.qr_base64.startsWith('data:') 
        ? response.data.qr_base64 
        : `data:image/png;base64,${response.data.qr_base64}`
    } else if (response.data.qr_code) {
      // Se só tem o código, precisaria gerar a imagem
      qrError.value = 'QR Code disponível apenas como texto'
    } else {
      qrError.value = 'QR Code não disponível'
    }
    
    // Inicia polling para verificar se conectou
    startPolling()
    
  } catch (e) {
    qrError.value = 'Erro ao gerar QR Code: ' + (e.response?.data?.error || e.message)
  } finally {
    qrLoading.value = false
  }
}

const startPolling = () => {
  if (pollingInterval) return
  
  polling.value = true
  pollingInterval = setInterval(async () => {
    try {
      const response = await whatsappService.getStatus()
      connectionStatus.value = response.data
      
      if (response.data.connected) {
        stopPolling()
        qrBase64.value = ''
        showQRCode.value = false
      }
    } catch (e) {
      console.error('Polling error:', e)
    }
  }, 3000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  polling.value = false
}

const disconnectWhatsApp = async () => {
  if (!confirm('Tem certeza que deseja desconectar o WhatsApp?')) return
  
  loading.value = true
  error.value = ''
  
  try {
    await whatsappService.disconnect()
    await checkStatus()
  } catch (e) {
    error.value = 'Erro ao desconectar: ' + (e.response?.data?.error || e.message)
  } finally {
    loading.value = false
  }
}

const restartInstance = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await whatsappService.restart()
    // Aguarda um pouco e verifica status
    setTimeout(checkStatus, 2000)
  } catch (e) {
    error.value = 'Erro ao reiniciar: ' + (e.response?.data?.error || e.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkStatus()
})

onUnmounted(() => {
  stopPolling()
})
</script>
