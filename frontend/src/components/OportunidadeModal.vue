<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Oportunidade' : 'Nova Oportunidade'"
    size="lg"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <div v-if="isEdit && isGanho" class="mb-6 p-4 bg-green-50 rounded-xl border border-green-100 flex items-center justify-between">
      <div class="flex items-center text-green-700 font-bold">
        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span>Oportunidade Ganha!</span>
      </div>
      <button 
        type="button"
        @click="copyBillingText"
        class="px-4 py-2 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 transition-all shadow-sm flex items-center"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m-1 4h.01M9 16h5m0 0l-1-1m1 1l-1 1" /></svg>
        Copiar Faturamento
      </button>
    </div>

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
            <select v-model="form.contato_principal" class="input">
              <option value="">Selecione um contato...</option>
              <option v-for="contato in contatos" :key="contato.id" :value="contato.id">
                {{ contato.nome }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Estágio do Funil <span class="text-red-500">*</span>
            </label>
            <select v-model="form.estagio" required class="input">
              <option value="">Selecione...</option>
              <option v-for="estagio in estagios" :key="estagio.id" :value="estagio.id">
                {{ estagio.nome }}
              </option>
            </select>
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
            <label class="block text-sm font-medium text-gray-700 mb-1">Região de Suporte</label>
            <select v-model="form.regiao" class="input">
              <option value="">Selecione...</option>
              <option v-for="reg in regioes" :key="reg.id" :value="reg.id">
                {{ reg.nome }}
              </option>
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

    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'
import { useOportunidadesStore } from '@/stores/oportunidades'

const props = defineProps({
  show: Boolean,
  oportunidade: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)
const contatos = ref([])
const estagios = ref([])
const regioes = ref([])

const form = ref({
  nome: '',
  conta: '',
  contato_principal: '',
  estagio: '',
  valor_estimado: 0,
  data_fechamento_esperada: '',
  probabilidade: 0,
  descricao: '',
  regiao: ''
})

const adicionais_itens = ref([])

const indicadores = computed(() => {
  return contatos.value.filter(c => c.tipo === 'INDICADOR')
})


const isGanho = computed(() => {
  const estagioObj = estagios.value.find(e => e.id === form.value.estagio)
  return estagioObj?.tipo === 'GANHO'
})

watch(() => props.show, async (newVal) => {
  if (newVal) {
    await loadOptions()
  }
})

watch(() => props.oportunidade, (newOportunidade) => {
  if (newOportunidade) {
    isEdit.value = true
    form.value = { ...newOportunidade }
    adicionais_itens.value = newOportunidade.adicionais_detalhes?.map(d => ({
      adicional: d.adicional,
      quantidade: d.quantidade
    })) || []
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

async function loadOptions() {
  try {
    const [contasRes, contatosRes, estagiosRes, regioesRes] = await Promise.all([
      api.get('/contas/'),
      api.get('/contatos/'),
      api.get('/estagios-funil/'),
      api.get('/regioes/')
    ])
    contas.value = contasRes.data.results || contasRes.data
    contatos.value = contatosRes.data.results || contatosRes.data
    estagios.value = estagiosRes.data.results || estagiosRes.data
    regioes.value = regioesRes.data.results || regioesRes.data
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
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

function resetForm() {
  form.value = {
    nome: '',
    conta: '',
    contato_principal: '',
    estagio: '',
    valor_estimado: 0,
    data_fechamento_esperada: '',
    probabilidade: 0,
    descricao: '',
    plano: '',
    periodo_pagamento: 'MENSAL',
    cortesia: '',
    cupom_desconto: '',
    forma_pagamento: '',
    indicador_comissao: '',
    regiao: ''
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
