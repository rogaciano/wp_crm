<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Oportunidade' : 'Nova Oportunidade'"
    size="lg"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Informações Básicas -->
      <section>
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Informações Básicas</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Nome da Oportunidade <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.nome"
              type="text"
              required
              class="input"
              placeholder="Ex: Venda de Sistema - Empresa XYZ"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Conta <span class="text-red-500">*</span>
            </label>
            <select v-model="form.conta" required class="input">
              <option value="">Selecione uma conta...</option>
              <option v-for="conta in contas" :key="conta.id" :value="conta.id">
                {{ conta.nome_empresa }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Contato Principal
            </label>
            <select v-model="form.contato_principal" class="input" :disabled="!form.conta">
              <option value="">{{ form.conta ? 'Selecione um contato...' : 'Selecione uma conta primeiro' }}</option>
              <option v-for="contato in contatosDaConta" :key="contato.id" :value="contato.id">
                {{ contato.nome }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Funil <span class="text-red-500">*</span>
            </label>
            <select v-model="form.funil" required class="input">
              <option :value="null">Selecione o funil...</option>
              <option v-for="f in funis" :key="f.id" :value="f.id">{{ f.nome }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Estágio do Funil <span class="text-red-500">*</span>
            </label>
            <select v-model="form.estagio" required class="input" :disabled="!form.funil">
              <option :value="null">{{ form.funil ? 'Selecione o estágio...' : 'Selecione um funil primeiro' }}</option>
              <option v-for="e in estagios" :key="e.id" :value="e.id">{{ e.nome }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Valor Estimado (R$)
            </label>
            <input
              v-model.number="form.valor_estimado"
              type="number"
              step="0.01"
              min="0"
              class="input"
              placeholder="0,00"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Probabilidade (%)
            </label>
            <input
              v-model.number="form.probabilidade"
              type="number"
              min="0"
              max="100"
              class="input"
              placeholder="0-100"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Data de Fechamento Esperada
            </label>
            <input
              v-model="form.data_fechamento_esperada"
              type="date"
              class="input"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Canal de Suporte (Faturamento)</label>
            <select v-model="form.canal" class="input" :disabled="!authStore.isAdmin && authStore.user?.perfil !== 'RESPONSAVEL'">
              <option :value="null">Selecione o canal...</option>
              <option v-for="canal in canais" :key="canal.id" :value="canal.id">
                {{ canal.nome }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Indicador (Opcional)</label>
            <select v-model="form.indicador_comissao" class="input">
              <option :value="null">Selecione o indicador...</option>
              <option v-for="contato in indicadores" :key="contato.id" :value="contato.id">
                {{ contato.nome }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fonte</label>
            <select v-model="form.fonte" class="input">
              <option value="">Selecione...</option>
              <option value="Site">Site</option>
              <option value="Evento">Evento</option>
              <option value="Indicação">Indicação</option>
              <option value="LinkedIn">LinkedIn</option>
              <option value="Cold Call">Cold Call</option>
              <option value="Outro">Outro</option>
            </select>
          </div>
        </div>
      </section>

      <section>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Observações Gerais
        </label>
        <textarea
          v-model="form.descricao"
          rows="4"
          class="input"
          placeholder="Outros detalhes sobre a oportunidade..."
        ></textarea>
      </section>

      <!-- Histórico de Estágios -->
      <section v-if="isEdit && historico.length > 0" class="mt-6 pt-4 border-t border-gray-100">
        <h4 class="text-sm font-bold text-gray-700 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Histórico de Estágios
        </h4>
        
        <div class="space-y-2 max-h-48 overflow-y-auto pr-2">
          <div 
            v-for="item in historico" 
            :key="item.id" 
            class="flex items-start text-xs bg-gray-50 rounded-lg p-2 border-l-4 border-primary-300"
          >
            <div class="flex-1">
              <div class="font-medium text-gray-800">
                <span v-if="item.nome_estagio_anterior" class="text-gray-500">{{ item.nome_estagio_anterior }}</span>
                <span v-else class="text-green-600 italic">Criação</span>
                <span class="mx-1 text-gray-400">→</span>
                <span class="text-primary-600 font-semibold">{{ item.nome_estagio_novo }}</span>
              </div>
              <div class="text-gray-500 mt-0.5">
                {{ item.data_mudanca_formatada }} por <span class="font-medium">{{ item.usuario_nome }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'
import { useOportunidadesStore } from '@/stores/oportunidades'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const props = defineProps({
  show: Boolean,
  oportunidade: Object,
  fixedContaId: [Number, String]
})

const emit = defineEmits(['close', 'saved'])

const form = ref({
  nome: '',
  conta: '',
  contato_principal: '',
  funil: null,
  estagio: null,
  valor_estimado: 0,
  data_fechamento_esperada: '',
  probabilidade: 0,
  descricao: '',
  canal: null,
  indicador_comissao: null,
  fonte: ''
})

const loading = ref(false)
const isEdit = ref(false)
const contas = ref([])
const contatos = ref([])
const estagios = ref([])
const canais = ref([])
const funis = ref([])
const adicionais_itens = ref([])
const historico = ref([])


const indicadores = computed(() => {
  return contatos.value.filter(c => c.tipo === 'INDICADOR' || c.tipo_contato_nome === 'INDICADOR')
})

const contatosDaConta = computed(() => {
  if (!form.value.conta) return []
  return contatos.value.filter(c => c.conta === form.value.conta)
})

const isGanho = computed(() => {
  const estagioObj = estagios.value.find(e => e.id === form.value.estagio)
  return estagioObj?.tipo === 'GANHO'
})

watch(() => props.show, async (newVal) => {
  if (newVal) {
    await loadOptions()
    if (props.fixedContaId && !isEdit.value) {
      form.value.conta = props.fixedContaId
    }
  }
})

watch(() => form.value.funil, async (newFunil) => {
  if (newFunil) {
    try {
      const response = await api.get(`/funis/${newFunil}/estagios/`)
      const raw = response.data.results || response.data
      estagios.value = raw.map(v => ({
        id: v.estagio_id,
        nome: v.nome,
        tipo: v.tipo,
        is_padrao: v.is_padrao
      }))

      // Se for novo ou não tiver estágio, pega o padrão
      if (!isEdit.value || !form.value.estagio) {
        const defaultEstagio = estagios.value.find(e => e.is_padrao) || estagios.value[0]
        if (defaultEstagio) {
          form.value.estagio = defaultEstagio.id
        }
      }
    } catch (error) {
      console.error('Erro ao carregar estágios:', error)
      estagios.value = []
    }
  } else {
    estagios.value = []
    form.value.estagio = null
  }
})

watch(() => form.value.conta, (newContaId) => {
  // Se mudar a conta, verifica se o contato principal ainda é válido
  if (form.value.contato_principal) {
    const selectedContato = contatos.value.find(c => c.id === form.value.contato_principal)
    if (selectedContato && selectedContato.conta !== newContaId) {
      form.value.contato_principal = ''
    }
  }

  if (newContaId && !isEdit.value) {
    const selectedConta = contas.value.find(c => c.id === newContaId)
    if (selectedConta && selectedConta.canal) {
      form.value.canal = selectedConta.canal
    } else {
      // Se a conta não tem canal, volta para o padrão do usuário
      form.value.canal = authStore.isAdmin ? null : (authStore.user?.canal || null)
    }
  }
})

watch(() => props.oportunidade, async (newOportunidade) => {
  if (newOportunidade) {
    isEdit.value = true
    form.value = { ...newOportunidade }
    adicionais_itens.value = newOportunidade.adicionais_detalhes?.map(d => ({
      adicional: d.adicional,
      quantidade: d.quantidade
    })) || []
    
    // Carrega histórico de estágios
    try {
      const response = await api.get(`/oportunidades/${newOportunidade.id}/historico_estagios/`)
      historico.value = response.data || []
    } catch (error) {
      console.error('Erro ao carregar histórico:', error)
      historico.value = []
    }
  } else {
    isEdit.value = false
    historico.value = []
    resetForm()
  }
}, { immediate: true })

async function loadOptions() {
  const endpoints = [
    { key: 'contas', path: '/contas/' },
    { key: 'contatos', path: '/contatos/' },
    { key: 'canais', path: '/canais/' },
    { key: 'funis', path: '/funis/' }
  ]

  for (const endpoint of endpoints) {
    try {
      const response = await api.get(endpoint.path)
      const data = response.data.results || response.data
      
      if (endpoint.key === 'funis') {
        funis.value = data.filter(f => f.tipo === 'OPORTUNIDADE')
        // Se for novo e houver funis, seleciona o primeiro por padrão
        if (!isEdit.value && funis.value.length > 0 && !form.value.funil) {
          form.value.funil = funis.value[0].id
        }
      } else {
        const refs = { contas, contatos, canais }
        refs[endpoint.key].value = data
      }
    } catch (error) {
      console.warn(`Erro ao carregar ${endpoint.key}:`, error.message)
    }
  }
}

async function copyBillingText() {
  try {
    const response = await api.get(`/oportunidades/${form.value.id}/gerar_texto_faturamento/`)
    const texto = response.data.texto
    
    await navigator.clipboard.writeText(texto)
    alert('Texto de faturamento copiado para a área de transferência! 📋')
  } catch (error) {
    console.error('Erro ao gerar texto:', error)
    alert('Erro ao gerar texto de faturamento. Verifique se o plano está selecionado.')
  }
}

// Helper para resetar e aplicar padrões
function resetForm() {
  form.value = {
    nome: '',
    conta: props.fixedContaId || '',
    contato_principal: '',
    funil: null,
    estagio: null,
    valor_estimado: 0,
    data_fechamento_esperada: '',
    probabilidade: 0,
    descricao: '',
    canal: authStore.isAdmin ? null : (authStore.user?.canal || null),
    indicador_comissao: null,
    fonte: ''
  }
  adicionais_itens.value = []
}

async function handleSubmit() {
  loading.value = true
  const oportunidadesStore = useOportunidadesStore()
  try {
    const data = { 
      ...form.value,
      adicionais_itens: adicionais_itens.value.filter(i => i.adicional)
    }
    
    // Remover campos vazios opcionais
    Object.keys(data).forEach(key => {
      if (data[key] === '' || data[key] === null || data[key] === undefined) {
        delete data[key]
      }
    })
    
    // Remover campos que não devem ser enviados na criação
    if (!isEdit.value) {
      delete data.id
      delete data.proprietario
      delete data.proprietario_nome
      delete data.data_criacao
      delete data.data_atualizacao
    }
    
    if (isEdit.value) {
      await oportunidadesStore.updateOportunidade(form.value.id, data)
    } else {
      await oportunidadesStore.createOportunidade(data)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar oportunidade:', error)
    const errorMsg = error.response?.data?.detail || 
                     JSON.stringify(error.response?.data) || 
                     error.message
    alert('Erro ao salvar oportunidade: ' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>
