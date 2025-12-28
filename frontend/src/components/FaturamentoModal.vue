<template>
  <BaseModal
    :show="show"
    title="Faturamento da Oportunidade"
    size="lg"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <div v-if="isGanho" class="mb-6 p-4 bg-green-50 rounded-xl border border-green-100 flex items-center justify-between transition-all animate-in fade-in slide-in-from-top-4">
      <div class="flex items-center text-green-700 font-bold">
        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span>Negócio Fechado! Pronta para faturar.</span>
      </div>
      <button 
        type="button"
        @click="copyBillingText"
        class="px-4 py-2 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 transition-all shadow-sm flex items-center"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5 a2 2 0 012-2h2a2 2 0 012 2m-1 4h.01M9 16h5m0 0l-1-1m1 1l-1 1" /></svg>
        Copiar Texto p/ Faturamento
      </button>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div class="bg-primary-50 px-4 py-6 rounded-2xl border border-primary-100">
        <h3 class="text-xs font-bold text-primary-600 uppercase tracking-widest mb-4 flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Configuração de Plano e Valores
        </h3>
        
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
            <select v-model="form.plano" @change="handlePlanoChange" class="input border-primary-200 focus:ring-primary-100">
              <option value="">Selecione o plano...</option>
              <option v-for="plano in planos" :key="plano.id" :value="plano.id">
                {{ plano.nome }} (R$ {{ form.periodo_pagamento === 'ANUAL' ? plano.preco_anual : plano.preco_mensal }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ form.periodo_pagamento === 'ANUAL' ? 'Valor Anual' : 'Mensalidade' }} (R$)
            </label>
            <div class="relative">
              <input
                v-model.number="form.valor_estimado"
                type="number"
                step="0.01"
                min="0"
                class="input border-primary-200 font-bold text-primary-700 pr-12 focus:ring-primary-100"
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
                  <label class="block text-[10px] font-bold text-gray-400 mb-1 uppercase">Recurso</label>
                  <select v-model="item.adicional" @change="handlePlanoChange" class="input py-1.5 border-gray-100 text-sm">
                    <option value="">Selecione...</option>
                    <option v-for="ad in planoAdicionais" :key="ad.id" :value="ad.id">
                      {{ ad.nome }} (+ R$ {{ ad.preco }}/{{ ad.unidade }})
                    </option>
                  </select>
                </div>
                <div class="w-20">
                  <label class="block text-[10px] font-bold text-gray-400 mb-1 uppercase">Qtd</label>
                  <input v-model.number="item.quantidade" type="number" min="1" @input="handlePlanoChange" class="input py-1.5 border-gray-100 text-center text-sm" />
                </div>
                <button type="button" @click="removeAdicional(index); handlePlanoChange()" class="p-2 text-red-300 hover:text-red-500 rounded-lg">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </div>
            </div>
            <div v-else class="text-center py-4 bg-white/50 border border-dashed border-primary-200 rounded-xl text-xs text-gray-400">
              Nenhum recurso adicional.
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Região de Suporte <span class="text-red-500">*</span></label>
          <select 
            v-model="form.suporte_regiao" 
            required 
            class="input disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed"
            :disabled="!!userRegiao"
          >
            <option value="">Selecione...</option>
            <option value="MATRIZ">Matriz</option>
            <option value="PERNAMBUCO">Pernambuco</option>
            <option value="CEARA">Ceará</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Forma de Pagamento</label>
          <select v-model="form.forma_pagamento" class="input">
            <option value="">Selecione...</option>
            <option value="CARTAO_RECORRENTE">Cartão de crédito recorrente</option>
            <option value="BOLETO">Boleto bancário</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Cupom de Desconto</label>
          <input v-model="form.cupom_desconto" type="text" class="input" placeholder="Ex: PROMO2024" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Indicador / Indicação</label>
          <select v-model="form.indicador_comissao" class="input">
            <option value="">Nenhum / Direto</option>
            <option v-for="ind in indicadores" :key="ind.id" :value="ind.id">
              {{ ind.nome }}
            </option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Cortesias da Negociação</label>
          <textarea v-model="form.cortesia" rows="2" class="input" placeholder="Ex: Setup grátis, etc..."></textarea>
        </div>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'
import { useOportunidadesStore } from '@/stores/oportunidades'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: Boolean,
  oportunidade: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const planos = ref([])
const planoAdicionais = ref([])
const contatos = ref([])
const estagios = ref([])

const authStore = useAuthStore()
const userRegiao = computed(() => authStore.user?.suporte_regiao)

const form = ref({
  plano: '',
  valor_estimado: 0,
  periodo_pagamento: 'MENSAL',
  cortesia: '',
  cupom_desconto: '',
  forma_pagamento: '',
  indicador_comissao: '',
  suporte_regiao: ''
})

const adicionais_itens = ref([])

const indicadores = computed(() => {
  return contatos.value.filter(c => c.tipo === 'INDICADOR')
})

const isGanho = computed(() => {
  const estagioObj = estagios.value.find(e => e.id === props.oportunidade?.estagio || e.id === props.oportunidade?.estagio_id)
  return estagioObj?.tipo === 'GANHO'
})

watch(() => props.show, async (newVal) => {
  if (newVal) {
    await loadOptions()
  }
})

watch(() => props.oportunidade, (newOpp) => {
  if (newOpp) {
    form.value = {
      plano: newOpp.plano || '',
      valor_estimado: newOpp.valor_estimado || 0,
      periodo_pagamento: newOpp.periodo_pagamento || 'MENSAL',
      cortesia: newOpp.cortesia || '',
      cupom_desconto: newOpp.cupom_desconto || '',
      forma_pagamento: newOpp.forma_pagamento || '',
      indicador_comissao: newOpp.indicador_comissao || '',
      suporte_regiao: newOpp.suporte_regiao || userRegiao.value || ''
    }
    adicionais_itens.value = newOpp.adicionais_detalhes?.map(d => ({
      adicional: d.adicional,
      quantidade: d.quantidade
    })) || []
  }
}, { immediate: true })

async function loadOptions() {
  try {
    const [planosRes, adicionaisRes, contatosRes, estagiosRes] = await Promise.all([
      api.get('/planos/'),
      api.get('/adicionais-plano/'),
      api.get('/contatos/'),
      api.get('/estagios-funil/')
    ])
    planos.value = planosRes.data.results || planosRes.data
    planoAdicionais.value = adicionaisRes.data.results || adicionaisRes.data
    contatos.value = contatosRes.data.results || contatosRes.data
    estagios.value = estagiosRes.data.results || estagiosRes.data
  } catch (error) {
    console.error('Erro ao carregar opções:', error)
  }
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

  if (form.value.periodo_pagamento === 'ANUAL') {
    form.value.valor_estimado = basePrice + (addOnTotal * 12)
  } else {
    form.value.valor_estimado = basePrice + addOnTotal
  }
}

function addAdicional() {
  adicionais_itens.value.push({ adicional: '', quantidade: 1 })
}

function removeAdicional(index) {
  adicionais_itens.value.splice(index, 1)
}

async function copyBillingText() {
  try {
    const response = await api.get(`/oportunidades/${props.oportunidade.id}/gerar_texto_faturamento/`)
    await navigator.clipboard.writeText(response.data.texto)
    alert('Texto de faturamento copiado! 📋')
  } catch (error) {
    alert('Erro ao gerar texto. Verifique se o plano está selecionado.')
  }
}

async function handleSubmit() {
  loading.value = true
  const store = useOportunidadesStore()
  try {
    const data = {
      ...form.value,
      adicionais_itens: adicionais_itens.value.filter(i => i.adicional)
    }
    await store.updateOportunidade(props.oportunidade.id, data)
    emit('saved')
    emit('close')
  } catch (error) {
    alert('Erro ao salvar faturamento: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>
