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
        </div>
      </section>

      <!-- Detalhes da Venda / Faturamento -->
      <section class="bg-primary-50 px-4 py-6 rounded-2xl border border-primary-100">
        <h3 class="text-xs font-bold text-primary-600 uppercase tracking-widest mb-4">Detalhes da Venda & Faturamento</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <div class="flex items-center justify-center space-x-2 bg-white p-1 rounded-xl border border-primary-100 w-fit mx-auto mb-4">
              <button 
                type="button"
                @click="form.periodo_pagamento = 'MENSAL'; handlePlanoChange()"
                :class="['px-6 py-1.5 rounded-lg text-xs font-bold transition-all', form.periodo_pagamento === 'MENSAL' ? 'bg-primary-600 text-white shadow-md' : 'text-gray-500 hover:bg-gray-50']"
              >
                Mensal
              </button>
              <button 
                type="button"
                @click="form.periodo_pagamento = 'ANUAL'; handlePlanoChange()"
                :class="['px-6 py-1.5 rounded-lg text-xs font-bold transition-all', form.periodo_pagamento === 'ANUAL' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-500 hover:bg-gray-50']"
              >
                Anual
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Plano DAPIC <span class="text-red-500">*</span>
            </label>
            <select v-model="form.plano" @change="handlePlanoChange" class="input border-primary-200">
              <option value="">Selecione o plano...</option>
              <option v-for="plano in planos" :key="plano.id" :value="plano.id">
                {{ plano.nome }} (R$ {{ form.periodo_pagamento === 'ANUAL' ? plano.preco_anual : plano.preco_mensal }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ form.periodo_pagamento === 'ANUAL' ? 'Valor Anual' : 'Mensalidade' }} Acordada (R$)
            </label>
            <div class="relative">
              <input
                v-model.number="form.valor_estimado"
                type="number"
                step="0.01"
                min="0"
                class="input border-primary-200 font-bold text-primary-700 pr-12"
                placeholder="0,00"
              />
              <span class="absolute right-3 top-2.5 text-[10px] font-bold text-gray-400">
                /{{ form.periodo_pagamento === 'ANUAL' ? 'ano' : 'mês' }}
              </span>
            </div>
          </div>

          <!-- Recursos Adicionais -->
          <div class="md:col-span-2 space-y-3">
            <div class="flex justify-between items-center">
              <label class="block text-sm font-medium text-gray-700">
                Recursos Adicionais
              </label>
              <button 
                type="button" 
                @click="addAdicional"
                class="text-[10px] bg-primary-600 text-white px-3 py-1 rounded-full font-bold hover:bg-primary-700 transition-colors flex items-center shadow-sm"
              >
                + Adicionar Recurso
              </button>
            </div>

            <div v-if="adicionais_itens.length > 0" class="space-y-2">
              <div v-for="(item, index) in adicionais_itens" :key="index" class="flex items-end gap-3 bg-white p-3 rounded-xl border border-primary-100">
                <div class="flex-grow">
                  <label class="block text-[10px] font-bold text-gray-400 mb-1 uppercase flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                    Recurso
                  </label>
                  <select v-model="item.adicional" @change="handlePlanoChange" class="input text-sm py-1.5 border-gray-200 focus:border-indigo-500 focus:ring-indigo-200">
                    <option value="">Selecione...</option>
                    <option v-for="ad in planoAdicionais" :key="ad.id" :value="ad.id">
                      {{ ad.nome }} (+ R$ {{ ad.preco }}/{{ ad.unidade }})
                    </option>
                  </select>
                </div>
                <div class="w-24">
                  <label class="block text-[10px] font-bold text-gray-400 mb-1 uppercase flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16" /></svg>
                    Qtd
                  </label>
                  <input 
                    v-model.number="item.quantidade" 
                    type="number" 
                    min="1" 
                    @input="handlePlanoChange"
                    class="input text-sm py-1.5 border-gray-200 text-center focus:border-indigo-500 focus:ring-indigo-200"
                  />
                </div>
                <button 
                  type="button" 
                  @click="removeAdicional(index); handlePlanoChange()"
                  class="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors mb-0.5"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </div>
            </div>
            <div v-else class="text-center py-4 bg-white/50 border border-dashed border-primary-200 rounded-xl text-xs text-gray-400 italic">
              Nenhum recurso adicional selecionado.
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Cupom de Desconto
            </label>
            <input
              v-model="form.cupom_desconto"
              type="text"
              class="input border-primary-200"
              placeholder="Ex: BLACKFRIDAY50"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Forma de Pagamento
            </label>
            <select v-model="form.forma_pagamento" class="input border-primary-200">
              <option value="">Selecione...</option>
              <option value="CARTAO_RECORRENTE">Cartão de crédito recorrente</option>
              <option value="BOLETO">Boleto bancário</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Indicador da Comissão
            </label>
            <input
              v-model="form.indicador_comissao"
              type="text"
              class="input border-primary-200"
              placeholder="Nome de quem indicou"
            />
          </div>

          <div v-if="isAdvancedPlan">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Região de Suporte (Advanced) <span class="text-red-500">*</span>
            </label>
            <select v-model="form.suporte_regiao" class="input border-primary-200 ring-2 ring-primary-100">
              <option value="">Selecione...</option>
              <option value="MATRIZ">Matriz</option>
              <option value="PERNAMBUCO">Pernambuco</option>
              <option value="CEARA">Ceará</option>
            </select>
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Cortesias da Negociação
            </label>
            <textarea
              v-model="form.cortesia"
              rows="2"
              class="input border-primary-200"
              placeholder="Ex: 3 meses de integração grátis..."
            ></textarea>
          </div>
        </div>
      </section>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Observações Gerais
        </label>
        <textarea
          v-model="form.descricao"
          rows="3"
          class="input"
          placeholder="Outros detalhes sobre a oportunidade..."
        ></textarea>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  oportunidade: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)
const contas = ref([])
const contatos = ref([])
const estagios = ref([])
const planos = ref([])

const form = ref({
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
  suporte_regiao: ''
})

const planoAdicionais = ref([])
const adicionais_itens = ref([])

const isAdvancedPlan = computed(() => {
  const pianoSel = planos.value.find(p => p.id === form.value.plano)
  return pianoSel?.nome?.includes('ADVANCED')
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
    const [contasRes, contatosRes, estagiosRes, planosRes, adicionaisRes] = await Promise.all([
      api.get('/contas/'),
      api.get('/contatos/'),
      api.get('/estagios-funil/'),
      api.get('/planos/'),
      api.get('/adicionais-plano/')
    ])
    contas.value = contasRes.data.results || contasRes.data
    contatos.value = contatosRes.data.results || contatosRes.data
    estagios.value = estagiosRes.data.results || estagiosRes.data
    planos.value = planosRes.data.results || planosRes.data
    planoAdicionais.value = adicionaisRes.data.results || adicionaisRes.data
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
}

function addAdicional() {
  adicionais_itens.value.push({ adicional: '', quantidade: 1 })
}

function removeAdicional(index) {
  adicionais_itens.value.splice(index, 1)
}

function handlePlanoChange() {
  const plano = planos.value.find(p => p.id === form.value.plano)
  if (!plano) return

  let basePrice = 0
  if (form.value.periodo_pagamento === 'ANUAL' && plano.preco_anual) {
    basePrice = parseFloat(plano.preco_anual)
  } else {
    basePrice = parseFloat(plano.preco_mensal)
  }

  let addOnTotal = 0
  adicionais_itens.value.forEach(item => {
    const ad = planoAdicionais.value.find(a => a.id === item.adicional)
    if (ad) {
      addOnTotal += parseFloat(ad.preco) * (item.quantidade || 0)
    }
  })

  // Se for anual, os adicionais (geralmente mensais) são multiplicados por 12
  if (form.value.periodo_pagamento === 'ANUAL') {
    form.value.valor_estimado = basePrice + (addOnTotal * 12)
  } else {
    form.value.valor_estimado = basePrice + addOnTotal
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
    suporte_regiao: ''
  }
  adicionais_itens.value = []
}

async function handleSubmit() {
  loading.value = true
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
      await api.put(`/oportunidades/${form.value.id}/`, data)
    } else {
      await api.post('/oportunidades/', data)
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
