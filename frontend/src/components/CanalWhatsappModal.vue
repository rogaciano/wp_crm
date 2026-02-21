<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="close">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-4 bg-gradient-to-r from-emerald-600 to-emerald-500 text-white">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-white/20 rounded-lg">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold">WhatsApp do Canal</h3>
              <p class="text-sm text-white/80">{{ canal?.nome }}</p>
            </div>
          </div>
          <button @click="close" class="p-2 hover:bg-white/10 rounded-full">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Status -->
        <div class="mb-6">
          <div class="flex items-center justify-between p-4 rounded-lg" 
               :class="status.connected ? 'bg-emerald-50' : 'bg-amber-50'">
            <div class="flex items-center space-x-3">
              <div class="w-3 h-3 rounded-full" 
                   :class="status.connected ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'"></div>
              <span class="font-medium" :class="status.connected ? 'text-emerald-700' : 'text-amber-700'">
                {{ status.connected ? 'Conectado' : 'Desconectado' }}
              </span>
            </div>
            <span class="text-xs px-2 py-1 rounded-full"
                  :class="status.connected ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">
              {{ status.state || 'unknown' }}
            </span>
          </div>
        </div>

        <!-- Instância não configurada -->
        <div v-if="!status.has_instance" class="text-center py-6">
          <div class="mb-4">
            <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
          <p class="text-gray-600 mb-4">Nenhuma instância WhatsApp configurada</p>
          <button 
            @click="conectarWhatsApp"
            :disabled="loading"
            class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50">
            <span v-if="loading">Criando instância...</span>
            <span v-else>Conectar WhatsApp</span>
          </button>
          <p class="text-xs text-gray-400 mt-2">Será criada uma instância automática para este canal</p>
        </div>

        <!-- QR Code -->
        <div v-else-if="!status.connected" class="text-center mb-6">
          <p class="text-gray-600 mb-4">Escaneie o QR Code com seu WhatsApp</p>
          
          <div v-if="qrLoading" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
          </div>
          
          <div v-else-if="qrBase64" class="inline-block p-4 bg-white border-2 border-emerald-200 rounded-xl">
            <img :src="qrBase64" alt="QR Code" class="w-48 h-48" />
          </div>
          
          <div v-else class="py-4">
            <button 
              @click="gerarQRCode"
              :disabled="qrLoading"
              class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50">
              Gerar QR Code
            </button>
          </div>
          
          <div v-if="qrBase64" class="mt-4 flex items-center justify-center gap-2 text-emerald-600">
            <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span class="text-xs">Aguardando conexão...</span>
          </div>
        </div>

        <!-- Conectado -->
        <div v-else class="text-center py-4">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 mb-4">
            <svg class="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h4 class="font-semibold text-gray-900">WhatsApp Conectado!</h4>
          <p class="text-sm text-gray-500 mt-1">{{ status.instance_name }}</p>
        </div>

        <!-- Ações -->
        <div class="flex flex-wrap gap-3" v-if="status.has_instance">
          <button 
            v-if="status.connected"
            @click="desconectar"
            :disabled="loading"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span>Desconectar</span>
          </button>

          <button 
            @click="reiniciar"
            :disabled="loading"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            title="Reiniciar instância">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>

          <button 
            @click="deletarInstancia"
            :disabled="loading"
            class="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 disabled:opacity-50"
            title="Deletar instância">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        <!-- Erro -->
        <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {{ error }}
        </div>

        <!-- Sucesso -->
        <div v-if="success" class="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-700 text-sm">
          {{ success }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  canal: Object
})

const emit = defineEmits(['close', 'updated'])

const loading = ref(false)
const qrLoading = ref(false)
const error = ref('')
const success = ref('')
const qrBase64 = ref(null)
const status = ref({ connected: false, state: 'unknown', has_instance: false })
let pollingInterval = null

function close() {
  stopPolling()
  emit('close')
}

async function checkStatus() {
  if (!props.canal?.id) return
  
  try {
    const response = await api.get(`/canais/${props.canal.id}/whatsapp/status/`)
    status.value = response.data
    
    if (response.data.connected) {
      qrBase64.value = null
      stopPolling()
      emit('updated')
    }
  } catch (err) {
    console.error('Erro ao verificar status:', err)
  }
}

async function conectarWhatsApp() {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    const response = await api.post(`/canais/${props.canal.id}/conectar-whatsapp/`)
    
    if (response.data.success) {
      success.value = response.data.message || 'Instância criada!'
      
      // Se retornou QR Code, mostra
      if (response.data.qr_base64) {
        qrBase64.value = response.data.qr_base64.startsWith('data:') 
          ? response.data.qr_base64 
          : `data:image/png;base64,${response.data.qr_base64}`
        startPolling()
      }
      
      emit('updated')
      await checkStatus()
    } else {
      error.value = response.data.error || 'Erro ao criar instância'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao criar instância'
  } finally {
    loading.value = false
  }
}

async function gerarQRCode() {
  qrLoading.value = true
  error.value = ''
  
  try {
    const response = await api.get(`/canais/${props.canal.id}/whatsapp/qrcode/`)
    if (response.data.qr_base64) {
      qrBase64.value = response.data.qr_base64.startsWith('data:') 
        ? response.data.qr_base64 
        : `data:image/png;base64,${response.data.qr_base64}`
      startPolling()
    } else {
      error.value = 'QR Code não disponível. Tente reiniciar a instância.'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao gerar QR Code'
  } finally {
    qrLoading.value = false
  }
}

async function desconectar() {
  loading.value = true
  error.value = ''
  
  try {
    await api.post(`/canais/${props.canal.id}/whatsapp/desconectar/`)
    success.value = 'Desconectado com sucesso!'
    await checkStatus()
    emit('updated')
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao desconectar'
  } finally {
    loading.value = false
  }
}

async function reiniciar() {
  loading.value = true
  error.value = ''
  qrBase64.value = null

  try {
    await api.post(`/canais/${props.canal.id}/whatsapp/reiniciar/`)
    success.value = 'Instância reiniciando... aguarde.'
    // Aguarda alguns segundos para a Evolution reiniciar antes de checar
    await new Promise(resolve => setTimeout(resolve, 4000))
    await checkStatus()
    // Se ainda não conectou, busca QR code e inicia polling
    if (!status.value.connected) {
      await gerarQRCode()
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao reiniciar'
  } finally {
    loading.value = false
  }
}

async function deletarInstancia() {
  if (!confirm('Tem certeza que deseja deletar esta instância? Esta ação não pode ser desfeita.')) {
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await api.delete(`/canais/${props.canal.id}/whatsapp/deletar-instancia/`)
    success.value = 'Instância deletada!'
    status.value = { connected: false, state: 'not_configured', has_instance: false }
    emit('updated')
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao deletar instância'
  } finally {
    loading.value = false
  }
}

function startPolling() {
  if (pollingInterval) return
  pollingInterval = setInterval(checkStatus, 3000)
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

watch(() => props.show, (newVal) => {
  if (newVal && props.canal) {
    error.value = ''
    success.value = ''
    qrBase64.value = null
    checkStatus()
  } else {
    stopPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>
