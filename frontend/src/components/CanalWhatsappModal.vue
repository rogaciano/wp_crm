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

        <!-- Formulário de Configuração (quando não tem instância ou quer editar) -->
        <div v-if="showConfig" class="mb-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Instance ID</label>
            <input 
              v-model="configForm.instance_id"
              type="text"
              placeholder="Nome da instância no Evolution"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
            <p class="text-xs text-gray-500 mt-1">Ex: pernambuco, wp_vendas</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <input 
              v-model="configForm.api_key"
              type="password"
              placeholder="API Key da instância"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
            <p class="text-xs text-gray-500 mt-1">Encontre no painel do Evolution</p>
          </div>
          <div class="flex gap-2">
            <button 
              @click="salvarConfiguracao"
              :disabled="loading || !configForm.instance_id || !configForm.api_key"
              class="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50">
              {{ loading ? 'Salvando...' : 'Salvar e Testar' }}
            </button>
            <button 
              v-if="canal?.whatsapp_instance_id"
              @click="showConfig = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
              Cancelar
            </button>
          </div>
        </div>

        <!-- Instância não configurada -->
        <div v-else-if="!canal?.whatsapp_instance_id" class="text-center py-6">
          <div class="mb-4">
            <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
          <p class="text-gray-600 mb-4">Nenhuma instância WhatsApp configurada</p>
          <button 
            @click="showConfig = true"
            class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700">
            Configurar Instância
          </button>
        </div>

        <!-- QR Code -->
        <div v-else-if="!status.connected && showQR" class="text-center mb-6">
          <p class="text-gray-600 mb-4">Escaneie o QR Code com seu WhatsApp</p>
          
          <div v-if="qrLoading" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
          </div>
          
          <div v-else-if="qrBase64" class="inline-block p-4 bg-white border-2 border-emerald-200 rounded-xl">
            <img :src="qrBase64" alt="QR Code" class="w-48 h-48" />
          </div>
          
          <div v-else class="py-8 text-gray-400">
            <p>Clique em "Gerar QR Code" para conectar</p>
          </div>
          
          <div class="mt-4 flex items-center justify-center gap-2 text-emerald-600">
            <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span class="text-xs">Aguardando conexão...</span>
          </div>
        </div>

        <!-- Ações -->
        <div class="flex flex-wrap gap-3" v-if="canal?.whatsapp_instance_id && !showConfig">
          <button 
            v-if="!status.connected"
            @click="gerarQRCode"
            :disabled="qrLoading"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
            </svg>
            <span>{{ qrLoading ? 'Gerando...' : 'Gerar QR Code' }}</span>
          </button>

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
            @click="showConfig = true"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            title="Editar configuração">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>

          <button 
            @click="reiniciar"
            :disabled="loading"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            title="Reiniciar instância">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
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
const showQR = ref(false)
const showConfig = ref(false)
const qrBase64 = ref(null)
const status = ref({ connected: false, state: 'unknown' })
const configForm = ref({ instance_id: '', api_key: '' })
let pollingInterval = null

function close() {
  stopPolling()
  showConfig.value = false
  emit('close')
}

async function checkStatus() {
  if (!props.canal?.id) return
  
  try {
    const response = await api.get(`/canais/${props.canal.id}/whatsapp/status/`)
    status.value = response.data
    
    if (response.data.connected) {
      showQR.value = false
      qrBase64.value = null
      stopPolling()
      emit('updated')
    }
  } catch (err) {
    console.error('Erro ao verificar status:', err)
  }
}

async function salvarConfiguracao() {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    const response = await api.post(`/canais/${props.canal.id}/whatsapp/configurar/`, {
      instance_id: configForm.value.instance_id,
      api_key: configForm.value.api_key
    })
    
    if (response.data.success) {
      success.value = response.data.message || 'Configuração salva!'
      showConfig.value = false
      emit('updated')
      await checkStatus()
    } else {
      error.value = response.data.error || 'Erro ao salvar configuração'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao salvar configuração'
  } finally {
    loading.value = false
  }
}

async function gerarQRCode() {
  qrLoading.value = true
  error.value = ''
  showQR.value = true
  
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
  
  try {
    await api.post(`/canais/${props.canal.id}/whatsapp/reiniciar/`)
    success.value = 'Instância reiniciada!'
    await checkStatus()
  } catch (err) {
    error.value = err.response?.data?.error || 'Erro ao reiniciar'
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
    // Preenche o form com dados existentes
    configForm.value.instance_id = props.canal.whatsapp_instance_id || ''
    configForm.value.api_key = '' // Não mostramos a API Key existente
    error.value = ''
    success.value = ''
    showQR.value = false
    showConfig.value = !props.canal.whatsapp_instance_id
    checkStatus()
  } else {
    stopPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>
