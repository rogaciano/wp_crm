<template>
  <div class="px-4 py-8 mx-auto max-w-4xl min-h-screen flex flex-col gap-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-black text-gray-800">Captação de Eventos</h1>
      <p class="text-sm text-gray-500">Adição rápida de prospecções</p>
    </div>

    <!-- Feedback de Sucesso -->
    <div v-if="showSuccess" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg shadow-sm flex items-center justify-between transition-all">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
        <span class="font-medium text-sm">Lead registrado com sucesso! Oportunidade criada.</span>
      </div>
      <button @click="showSuccess = false" class="text-green-500 hover:text-green-700">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
    </div>

    <!-- Configuração do Evento -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div class="flex items-center gap-2 mb-4">
         <svg class="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
         <h2 class="text-sm font-bold text-gray-700 tracking-wider">CONFIGURAÇÃO PADRÃO (FIXA)</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Fonte / Origem</label>
          <select v-model="config.origem" class="input w-full bg-gray-50 border-gray-200">
            <option value="">Selecione uma Origem...</option>
            <option v-for="origem in origens" :key="origem.id" :value="origem.id">{{ origem.nome }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Tag do Evento</label>
          <TagInput v-model="config.tags" :readonly="false" placeholder="Adicionar Tag..." />
        </div>
      </div>
    </div>

    <!-- Formulário do Lead -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 relative">
      <!-- Temperatura Discreta -->
      <div class="absolute top-5 right-5 flex items-center justify-center">
         <button 
           type="button" 
           @click="toggleTemperatura" 
           class="w-6 h-6 rounded-full flex items-center justify-center transition-all focus:outline-none ring-2 ring-offset-1"
           :class="lead.isQuente ? 'bg-red-50 hover:bg-red-100 ring-red-100' : 'bg-blue-50 hover:bg-blue-100 ring-blue-100'"
           title="Define a temperatura (frio/quente)"
         >
            <div class="w-2 h-2 rounded-full" :class="lead.isQuente ? 'bg-red-400' : 'bg-blue-300'"></div>
         </button>
      </div>

      <div class="flex items-center gap-2 mb-6">
         <svg class="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
         <h2 class="text-lg font-black text-gray-800">Novo Contato Rápido</h2>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Empresa</label>
          <input 
            type="text" 
            v-model="lead.empresa" 
            class="input w-full"
            placeholder="Nome da Empresa (opcional mas recomendado)" 
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Nome do Contato <span class="text-red-500">*</span></label>
          <input 
            type="text" 
            v-model="lead.contato" 
            class="input w-full"
            placeholder="Ex: João Silva" 
            required
            ref="contatoInputRef"
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Telefone / WhatsApp <span class="text-red-500">*</span></label>
          <!-- Utilizando o PhoneInput que já tem suporte a mascaras e classes -->
          <PhoneInput
            v-model="lead.telefone" 
            required
            input-class="input w-full"
            placeholder="(11) 99999-9999"
          />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Observação (Segmento, Notas, etc)</label>
          <textarea 
            v-model="lead.observacao" 
            rows="2"
            class="input w-full resize-none"
            placeholder="Insira o segmento ou outras notas adicionais..." 
          ></textarea>
        </div>

        <div class="pt-4 mt-2 border-t border-gray-100 flex justify-end">
          <button 
            type="submit" 
            class="btn btn-primary w-full md:w-auto text-base py-2.5 px-8 shadow-md hover:shadow-lg transition-shadow bg-primary-600 hover:bg-primary-700 font-bold"
            :disabled="loading"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5 text-white pr-1" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
              Salvando...
            </span>
            <span v-else>Salvar e Próximo</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import TagInput from '@/components/TagInput.vue'
import PhoneInput from '@/components/PhoneInput.vue'

const authStore = useAuthStore()

// References
const origens = ref([])
const funnelPadrao = ref(null)
const defaultEstagioId = ref(null)

const loading = ref(false)
const showSuccess = ref(false)
const contatoInputRef = ref(null)

// Configuração Persistente
const config = ref({
  origem: '',
  tags: [] // Lida com array de ids (v-model do TagInput)
})

// Formulário por Lead
const initialLead = () => ({
  empresa: '',
  contato: '',
  telefone: '',
  observacao: '',
  isQuente: false
})

const lead = ref(initialLead())

function toggleTemperatura() {
  lead.value.isQuente = !lead.value.isQuente
}

async function loadDefaults() {
  try {
    const [resOrigens, resFunis] = await Promise.all([
      api.get('/origens/', { params: { page_size: 100 } }),
      api.get('/funis/')
    ])

    const origensLista = resOrigens.data.results || resOrigens.data
    origens.value = origensLista
    if (origensLista.length > 0) {
      config.value.origem = origensLista[0].id
    }

    const funisLista = resFunis.data.results || resFunis.data
    if (funisLista.length > 0) {
      funnelPadrao.value = funisLista[0]
      const resEstagios = await api.get(`/funis/${funnelPadrao.value.id}/estagios/`)
      const estagios = resEstagios.data.results || resEstagios.data
      if (estagios.length > 0) {
        defaultEstagioId.value = estagios[0].estagio
      }
    }
  } catch (err) {
    console.error('Erro ao buscar padrões para captação:', err)
  }
}

async function handleSubmit() {
  if (!lead.value.contato.trim() || !lead.value.telefone) {
    alert("Nome e Telefone são obrigatórios")
    return
  }

  loading.value = true
  showSuccess.value = false

  try {
    let contaId = null

    // 1. Criar Conta (Empresa)
    if (lead.value.empresa.trim()) {
      const resConta = await api.post('/contas/', {
        nome_empresa: lead.value.empresa.trim(),
        proprietario: authStore.user.id
      })
      contaId = resConta.data.id
    }

    // 2. Criar Contato
    const telefones = [{
        numero: lead.value.telefone,
        tipo: 'CELULAR',
        principal: true
    }]

    const resContato = await api.post('/contatos/', {
      nome: lead.value.contato.trim(),
      conta: contaId,
      proprietario: authStore.user.id,
      telefones_input: telefones,
      tags: config.value.tags,
      notas: lead.value.observacao // Salva a observação nas notas do contato
    })
    const contatoId = resContato.data.id

    // 3. Criar Oportunidade
    const nomeOp = contaId 
      ? `Prospecção - ${lead.value.empresa.trim()}`
      : `Prospecção - ${lead.value.contato.trim()}`

    const payloadOp = {
      nome: nomeOp,
      proprietario: authStore.user.id,
      valor_estimado: 0,
      probabilidade: lead.value.isQuente ? 80 : 0,
      descricao: lead.value.observacao, // Salva observação também na oportunidade
      conta: contaId,
      contato_principal: contatoId,
      origem: config.value.origem || null,
      funil: funnelPadrao.value?.id || null,
      estagio: defaultEstagioId.value || null
    }

    await api.post('/oportunidades/', payloadOp)

    // Sucesso
    showSuccess.value = true
    setTimeout(() => { showSuccess.value = false }, 5000)

    // Reseta form (mas preserva as configs de Tag/Origem)
    lead.value = initialLead()

    // Foca novamente no contato
    if (contatoInputRef.value) {
      setTimeout(() => { contatoInputRef.value.focus() }, 50)
    }

  } catch (err) {
    console.error('Erro no salvamento:', err)
    let msg = err.message;
    if (err.response && err.response.data) {
        msg = typeof err.response.data === 'object' ? JSON.stringify(err.response.data, null, 2) : err.response.data;
    }
    alert("Erro detalhado: " + msg)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDefaults()
})
</script>
