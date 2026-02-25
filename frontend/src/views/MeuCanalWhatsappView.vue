<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Conexão WhatsApp</h1>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="!meuCanal" class="card p-8 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h2 class="text-xl font-semibold text-gray-700 mb-2">Sem Canal Vinculado</h2>
      <p class="text-gray-500">Você não está vinculado a nenhum canal de vendas.</p>
    </div>

    <div v-else class="max-w-2xl mx-auto">
      <!-- Card do Canal -->
      <div class="card overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-emerald-600 to-emerald-500 text-white">
          <div class="flex items-center space-x-3">
            <div class="p-2 bg-white/20 rounded-lg">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold text-lg">WhatsApp do Canal</h3>
              <p class="text-sm text-white/80">{{ meuCanal.nome }}</p>
            </div>
          </div>
        </div>

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

          <!-- Sem instância configurada -->
          <div v-if="!status.has_instance" class="text-center py-6">
            <div class="mb-4">
              <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <p class="text-gray-600 mb-4">Nenhuma instância WhatsApp configurada</p>
            <button 
              @click="conectarWhatsApp"
              :disabled="actionLoading"
              class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50">
              <span v-if="actionLoading">Criando instância...</span>
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
          <div class="flex flex-wrap gap-3 justify-center" v-if="status.has_instance">
            <button 
              v-if="status.connected"
              @click="desconectar"
              :disabled="actionLoading"
              class="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Desconectar</span>
            </button>

            <button 
              @click="reiniciar"
              :disabled="actionLoading"
              class="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Reiniciar</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const loading = ref(true)
const actionLoading = ref(false)
const qrLoading = ref(false)
const error = ref('')
const success = ref('')
const meuCanal = ref(null)
const qrBase64 = ref(null)
const status = ref({ connected: false, state: 'unknown', has_instance: false })
let pollingInterval = null

onMounted(async () => {
  await loadMeuCanal()
})

onUnmounted(() => {
  stopPolling()
})

async function loadMeuCanal() {
  loading.value = true
  try {
    // Busca o canal do usuário (responsável ou vínculo)
    const response = await api.get('/canais/')
    const canais = response.data.results || response.data
    meuCanal.value = canais.length > 0 ? canais[0] : null
    
    if (meuCanal.value) {
      await checkStatus()
    }
  } catch (err) {
    console.error('Erro ao carregar canal:', err)
  } finally {
    loading.value = false
  }
}

async function checkStatus() {
  if (!meuCanal.value?.id) return
  
  try {
    const response = await api.get(`/canais/${meuCanal.value.id}/whatsapp/status/`)
    status.value = response.data
    
    if (response.data.connected) {
      qrBase64.value = null
      stopPolling()
    }
  } catch (err) {
    console.error('Erro ao verificar status:', err)
  }
}

async function conectarWhatsApp() {
  actionLoading.value = true
  error.value = ''
  success.value = ''
  
  try {
    const response = await api.post(`/canais/${meuCanal.value.id}/conectar-whatsapp/`)
    
    if (response.data.success) {
      success.value = response.data.message || 'Instância criada!'
      
      if (response.data.qr_base64) {
        qrBase64.value = response.data.qr_base64.startsWith('data:') 
          ? response.data.qr_base64 
          : `data:image/png;base64,${response.data.qr_base64}`
        startPolling()
      }
      
      await checkStatus()
    } else {
      error.value = response.data.error || 'Erro ao criar instância'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao criar instância'
  } finally {
    actionLoading.value = false
  }
}

async function gerarQRCode() {
  qrLoading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await api.get(`/canais/${meuCanal.value.id}/whatsapp/qrcode/`)
    if (response.data.qr_base64) {
      qrBase64.value = response.data.qr_base64.startsWith('data:')
        ? response.data.qr_base64
        : `data:image/png;base64,${response.data.qr_base64}`
      startPolling()
    } else {
      error.value = 'QR Code não disponível. A instância pode ainda estar reiniciando — aguarde alguns segundos e tente novamente.'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao gerar QR Code. Tente reiniciar a instância.'
  } finally {
    qrLoading.value = false
  }
}

async function desconectar() {
  actionLoading.value = true
  error.value = ''
  
  try {
    await api.post(`/canais/${meuCanal.value.id}/whatsapp/desconectar/`)
    success.value = 'Desconectado com sucesso!'
    await checkStatus()
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao desconectar'
  } finally {
    actionLoading.value = false
  }
}

async function reiniciar() {
  actionLoading.value = true
  error.value = ''
  success.value = ''
  qrBase64.value = null

  try {
    const response = await api.post(`/canais/${meuCanal.value.id}/whatsapp/reiniciar/`)

    if (response.data.success === false) {
      error.value = response.data.error || 'Falha ao reiniciar a instância.'
      return
    }

    success.value = 'Instância reiniciando... aguarde.'
    // Aguarda a Evolution reiniciar (6s é mais seguro que 4s)
    await new Promise(resolve => setTimeout(resolve, 6000))
    await checkStatus()

    if (status.value.connected) {
      success.value = 'WhatsApp reconectado com sucesso!'
    } else {
      success.value = 'Reiniciado! Clique em "Gerar QR Code" para reconectar.'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao reiniciar'
  } finally {
    actionLoading.value = false
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
</script>
