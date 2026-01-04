<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">WhatsApp</h1>
        <p class="text-gray-500 text-sm">Gerencie a conexão e configurações do WhatsApp</p>
      </div>
    </div>

    <!-- Componente de Conexão -->
    <WhatsappConnection />

    <!-- Informações Adicionais -->
    <div class="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100">
        <h3 class="font-semibold text-gray-900">Configurações da Integração</h3>
      </div>
      <div class="p-6 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">API URL</p>
            <p class="font-mono text-sm text-gray-700">{{ apiUrl }}</p>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Instância</p>
            <p class="font-mono text-sm text-gray-700">{{ instanceId }}</p>
          </div>
        </div>

        <div class="border-t border-gray-100 pt-4">
          <h4 class="font-medium text-gray-900 mb-3">Webhook URL</h4>
          <div class="flex items-center space-x-2">
            <input 
              type="text" 
              :value="webhookUrl" 
              readonly 
              class="flex-1 px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg font-mono text-sm"
            />
            <button 
              @click="copyWebhookUrl"
              class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-2">
            Configure esta URL no webhook da Evolution API para receber mensagens em tempo real.
          </p>
        </div>

        <!-- Instruções -->
        <div class="border-t border-gray-100 pt-4">
          <h4 class="font-medium text-gray-900 mb-3">Como Configurar o Webhook</h4>
          <ol class="list-decimal list-inside space-y-2 text-sm text-gray-600">
            <li>Acesse o painel da Evolution API</li>
            <li>Vá em <strong>Configurations → Events → Webhook</strong></li>
            <li>Ative o Webhook (toggle "Enabled")</li>
            <li>Cole a URL do webhook acima</li>
            <li>Marque o evento <strong>MESSAGES_UPSERT</strong></li>
            <li>Salve as configurações</li>
          </ol>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="showToast" 
         class="fixed bottom-4 right-4 bg-emerald-600 text-white px-4 py-2 rounded-lg shadow-lg transition-all">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import WhatsappConnection from '@/components/WhatsappConnection.vue'

const showToast = ref(false)
const toastMessage = ref('')

// Estas informações poderiam vir de uma API de configuração
// Por enquanto, vamos usar valores padrão baseados no ambiente
const apiUrl = computed(() => {
  // Em produção, poderia vir de uma API
  return 'https://evo.matutec.com.br'
})

const instanceId = computed(() => {
  return 'informsistemas'
})

const webhookUrl = computed(() => {
  // Usa a URL atual como base
  const baseUrl = window.location.origin
  return `${baseUrl}/api/webhooks/whatsapp/`
})

const copyWebhookUrl = () => {
  navigator.clipboard.writeText(webhookUrl.value)
  toastMessage.value = 'URL copiada!'
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 2000)
}
</script>
