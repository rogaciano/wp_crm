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

    <!-- Feedback de Erro -->
    <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg shadow-sm flex items-start justify-between transition-all">
      <div class="flex items-start gap-2">
        <svg class="w-5 h-5 flex-shrink-0 mt-0.5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <div class="font-medium text-sm whitespace-pre-wrap leading-relaxed">{{ errorMessage }}</div>
      </div>
      <button @click="errorMessage = ''" class="text-red-500 hover:text-red-800 flex-shrink-0 p-1 ml-2">
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
          <label class="block text-xs font-semibold text-gray-600 mb-1">CNPJ (Opcional)</label>
          <div class="flex gap-2">
            <input 
              type="text" 
              v-model="lead.cnpj" 
              class="input flex-1"
              placeholder="00.000.000/0000-00"
              @blur="onCnpjBlur"
            />
            <button
              type="button"
              @click="buscarCNPJ"
              :disabled="buscandoCNPJ || !lead.cnpj"
              class="px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all flex items-center text-sm font-medium"
              title="Buscar dados do CNPJ"
            >
              <svg v-if="!buscandoCNPJ" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
            </button>
          </div>
          <p v-if="cnpjStatus" class="text-xs mt-1" :class="cnpjStatusClass">{{ cnpjStatus }}</p>
        </div>
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
const errorMessage = ref("")
const contatoInputRef = ref(null)

// Configuração Persistente
const config = ref({
  origem: '',
  tags: [] // Lida com array de ids (v-model do TagInput)
})

// Formulário por Lead
const initialLead = () => ({
  cnpj: '',
  empresa: '',
  contato: '',
  telefone: '',
  observacao: '',
  isQuente: false,
  contaData: null
})

const lead = ref(initialLead())

const buscandoCNPJ = ref(false)
const cnpjStatus = ref('')
const cnpjStatusClass = ref('text-gray-500')

async function buscarCNPJ() {
  if (!lead.value.cnpj || buscandoCNPJ.value) return
  
  const cnpjLimpo = lead.value.cnpj.replace(/\D/g, '')
  
  if (cnpjLimpo.length !== 14) {
    cnpjStatus.value = 'CNPJ deve ter 14 dígitos'
    cnpjStatusClass.value = 'text-red-500'
    return
  }
  
  buscandoCNPJ.value = true
  cnpjStatus.value = 'Buscando dados...'
  cnpjStatusClass.value = 'text-blue-500'
  
  try {
    const response = await api.get(`/contas/buscar_cnpj/?cnpj=${cnpjLimpo}`)
    const data = response.data
    
    if (data.status === 'ERROR') {
      cnpjStatus.value = data.message || 'CNPJ não encontrado'
      cnpjStatusClass.value = 'text-red-500'
      return
    }
    
    // Atualiza a UI
    lead.value.empresa = data.nome || data.fantasia || lead.value.empresa
    lead.value.cnpj = cnpjLimpo.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
    
    // Guarda o resto pra enviar na criação da Conta
    lead.value.contaData = {
      cnpj: lead.value.cnpj,
      telefone_principal: data.telefone,
      email: data.email,
      endereco: [data.logradouro, data.numero, data.complemento, data.bairro].filter(Boolean).join(', '),
      cidade: data.municipio,
      estado: data.uf,
      cep: data.cep,
      setor: data.atividade_principal?.[0]?.text?.substring(0, 100)
    }

    const cnaeCode = data.atividade_principal?.[0]?.code
    const cnaeText = data.atividade_principal?.[0]?.text
    if (cnaeCode && cnaeText) {
      const cnaeLine = `CNAE: ${cnaeCode} - ${cnaeText}`
      if (lead.value.observacao) {
        if (!lead.value.observacao.includes(cnaeCode)) {
          lead.value.observacao += `\n${cnaeLine}`
        }
      } else {
        lead.value.observacao = cnaeLine
      }
    }

    cnpjStatus.value = `✓ ${data.situacao || 'Dados carregados'}`
    cnpjStatusClass.value = data.situacao === 'ATIVA' ? 'text-green-500' : 'text-amber-500'
    
    if (contatoInputRef.value) {
      setTimeout(() => { contatoInputRef.value.focus() }, 50)
    }
    
  } catch (error) {
    console.error('Erro ao buscar CNPJ:', error)
    cnpjStatus.value = 'Erro ao consultar CNPJ. Tente novamente.'
    cnpjStatusClass.value = 'text-red-500'
  } finally {
    buscandoCNPJ.value = false
  }
}

function onCnpjBlur() {
  const cnpjLimpo = lead.value.cnpj?.replace(/\D/g, '') || ''
  if (cnpjLimpo.length === 14 && !lead.value.empresa) {
    buscarCNPJ()
  }
}

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
        // FunilEstagioSerializer retorna estagio_id 
        defaultEstagioId.value = estagios[0].estagio_id || estagios[0].estagio || estagios[0].id
      }
    }
  } catch (err) {
    console.error('Erro ao buscar padrões para captação:', err)
  }
}

async function handleSubmit() {
  if (!lead.value.contato.trim() || !lead.value.telefone) {
    errorMessage.value = "Nome e Telefone são obrigatórios"
    return
  }
  if (!funnelPadrao.value || !defaultEstagioId.value) {
    errorMessage.value = "Nenhum Funil padrão encontrado. Verifique as configurações."
    return
  }

  loading.value = true
  showSuccess.value = false
  errorMessage.value = ""

  try {
    // 0. Checar se CNPJ já Existe (Evitar erro de duplicidade de Conta)
    try {
      if (lead.value.cnpj) {
        const cnpjBusca = lead.value.cnpj.trim()
        const resCnpj = await api.get('/contas/checar_cnpj/', { params: { cnpj: cnpjBusca } })
        
        if (resCnpj.data.exists) {
          const contaExistente = resCnpj.data.conta;
          
          const origemSelecionada = origens.value.find(o => o.id === config.value.origem);
          const nomeOrigem = origemSelecionada ? origemSelecionada.nome : 'Evento/Origem Genérica';
          
          const payloadAtividade = {
            titulo: `Tentativa de cadastro rápido no evento ${nomeOrigem}`,
            tipo: 'TAREFA',
            status: 'PENDENTE',
            descricao: `Lead ${lead.value.contato} (${lead.value.telefone}) tentou cadastro no evento ${nomeOrigem}, mas a Empresa já existe no sistema com o CNPJ informado. \nNotas do evento: ${lead.value.observacao || ''}`,
            content_type: contaExistente.content_type_id,
            object_id: contaExistente.id,
            proprietario: authStore.user.id
          };
          
          await api.post('/atividades/', payloadAtividade);
          
          showSuccess.value = true;
          errorMessage.value = '';
          setTimeout(() => { showSuccess.value = false }, 5000);
          
          // Resetar o formulário
          lead.value = initialLead();
          cnpjStatus.value = '';
          if (contatoInputRef.value) {
            setTimeout(() => { contatoInputRef.value.focus() }, 50)
          }
          loading.value = false;
          
          return; // Interrompe o fluxo normal
        }
      }
    } catch (errBuscaCnpj) {
      console.error('Erro ao checar CNPJ:', errBuscaCnpj)
    }

    // 1. Checar se Contato Existe pelo Telefone (Evitar duplicação antes de criar qualquer coisa)
    try {
      const telefoneBusca = lead.value.telefone.trim()
      const resPhone = await api.get('/contatos/checar_telefone/', { params: { telefone: telefoneBusca } })
      
      if (resPhone.data.exists) {
        const contatoExistente = resPhone.data.contato;
        
        // Em vez de mudar a empresa do contato, o usuário pediu para criarmos uma Tarefa (Atividade)
        // para que a equipe saiba que ele passou no estande com dados diferentes.
        const origemSelecionada = origens.value.find(o => o.id === config.value.origem);
        const nomeOrigem = origemSelecionada ? origemSelecionada.nome : 'Evento/Origem Genérica';
        const nomeEmpresaOriginal = contatoExistente.conta_nome || 'Nenhuma/Desconhecida';
        const nomeEmpresaInformada = lead.value.empresa.trim() || lead.value.cnpj || 'Nenhuma';
        
        const payloadAtividade = {
          titulo: `Cadastro rápido no evento ${nomeOrigem}`,
          tipo: 'TAREFA',
          status: 'PENDENTE',
          descricao: `Contato evento ${nomeOrigem}, com o contato já cadastrado no sistema, vinculando a empresa [${nomeEmpresaOriginal}], mas no evento mostrou a empresa [${nomeEmpresaInformada}]. \nNotas do evento: ${lead.value.observacao || ''}`,
          content_type: contatoExistente.content_type_id,
          object_id: contatoExistente.id,
          proprietario: authStore.user.id
        };
        
        await api.post('/atividades/', payloadAtividade);
        
        showSuccess.value = true;
        errorMessage.value = '';
        setTimeout(() => { showSuccess.value = false }, 5000);
        
        // Resetar o formulário
        lead.value = initialLead();
        cnpjStatus.value = '';
        if (contatoInputRef.value) {
          setTimeout(() => { contatoInputRef.value.focus() }, 50)
        }
        loading.value = false;
        
        return; // Interrompe o fluxo normal
      }
    } catch (errBusca) {
      console.error('Erro ao checar telefone:', errBusca)
      // Se a checagem falhar, prossegue normalmente e deixa o backend validar na criação
    }

    let contaId = null
    const userCanal = authStore.user?.canal || null

    // 2. Criar Conta (Empresa)
    if (lead.value.empresa.trim() || lead.value.cnpj) {
      let contaPayload = {
        nome_empresa: lead.value.empresa.trim() || lead.value.cnpj,
        proprietario: authStore.user.id,
        canal: userCanal
      }
      
      if (lead.value.contaData) {
        contaPayload = {
          ...contaPayload,
          ...lead.value.contaData,
          nome_empresa: lead.value.empresa.trim() || lead.value.cnpj // ensure updated name
        }
      }
      
      if (lead.value.cnpj) {
        contaPayload.cnpj = lead.value.cnpj
      }

      const resConta = await api.post('/contas/', contaPayload)
      contaId = resConta.data.id
    }

    // 3. Criar Contato novo
    let contatoId = null;
    const telefones = [{
        numero: lead.value.telefone,
        tipo: 'CELULAR',
        principal: true
    }]

    const resContato = await api.post('/contatos/', {
      nome: lead.value.contato.trim(),
      conta: contaId,
      proprietario: authStore.user.id,
      canal: userCanal,
      telefones_input: telefones,
      tags: config.value.tags,
      notas: lead.value.observacao // Salva a observação nas notas do contato
    })
    contatoId = resContato.data.id

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
      canal: userCanal,
      origem: config.value.origem || null,
      funil: funnelPadrao.value.id,
      estagio: defaultEstagioId.value
    }

    await api.post('/oportunidades/', payloadOp)

    // Sucesso
    showSuccess.value = true
    setTimeout(() => { showSuccess.value = false }, 5000)

    // Reseta form (mas preserva as configs de Tag/Origem)
    lead.value = initialLead()
    cnpjStatus.value = ''

    // Foca novamente no contato
    if (contatoInputRef.value) {
      setTimeout(() => { contatoInputRef.value.focus() }, 50)
    }

  } catch (err) {
    console.error('Erro no salvamento:', err)
    
    let msg = "Não foi possível salvar o registro."
    
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'object') {
        const errList = []
        for (const key in data) {
          const value = data[key]
          let prefix = ''
          
          if (key !== 'non_field_errors' && key !== 'detail') {
              // Traduzir chaves comuns para uma leitura melhor
              let fieldName = key
              if (key === 'nome_empresa') fieldName = 'Empresa'
              if (key === 'nome') fieldName = 'Nome do Contato'
              if (key === 'telefones_input') fieldName = 'Telefone'
              prefix = `${fieldName}: `
          }
          
          if (Array.isArray(value)) {
            errList.push(`${prefix}${value.join(', ')}`)
          } else {
            errList.push(`${prefix}${value}`)
          }
        }
        if (errList.length > 0) {
           msg = errList.join('\n')
        }
      } else {
        msg = data
      }
    } else {
       msg = err.message
    }
    
    errorMessage.value = msg
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDefaults()
})
</script>
