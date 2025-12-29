<template>
  <BaseModal
    :show="show"
    title="Converter Lead"
    @close="$emit('close')"
    @confirm="handleConvert"
    :loading="loading"
  >
    <div v-if="lead" class="space-y-4">
      <div class="p-4 bg-primary-50 rounded-xl border border-primary-100 mb-6">
        <p class="text-sm text-primary-800">
          Você está convertendo o lead <span class="font-bold">{{ lead.nome }}</span>. 
          Isso criará automaticamente uma <strong>Conta</strong> e um <strong>Contato</strong>.
        </p>
      </div>

      <div class="space-y-4">
        <div class="flex items-center">
          <input
            id="criar_oportunidade"
            v-model="form.criar_oportunidade"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label for="criar_oportunidade" class="ml-2 block text-sm font-medium text-gray-900">
            Criar uma oportunidade agora
          </label>
        </div>

        <div v-if="form.criar_oportunidade" class="space-y-4 pt-2 animate-fadeIn">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Nome da Oportunidade
            </label>
            <input
              v-model="form.nome_oportunidade"
              type="text"
              class="input"
              :placeholder="'Oportunidade - ' + lead.nome"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Valor Estimado (R$)
              </label>
              <input
                v-model.number="form.valor_estimado"
                type="number"
                step="0.01"
                min="0"
                class="input font-bold text-primary-700"
                placeholder="0,00"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Canal Responsável (Suporte)
              </label>
              <select v-model="form.canal" class="input">
                <option value="">Mesmo do Vendedor</option>
                <option v-for="canal in canais" :key="canal.id" :value="canal.id">
                  {{ canal.nome }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  lead: Object
})

const emit = defineEmits(['close', 'converted'])

const loading = ref(false)
const canais = ref([])
const form = ref({
  criar_oportunidade: true,
  nome_oportunidade: '',
  valor_estimado: 0,
  canal: ''
})

onMounted(() => {
  loadCanais()
})

async function loadCanais() {
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar canais:', error)
  }
}

watch(() => props.lead, (newLead) => {
  if (newLead) {
    form.value.nome_oportunidade = `Oportunidade - ${newLead.nome}`
    form.value.valor_estimado = 0
    form.value.criar_oportunidade = true
    form.value.canal = newLead.proprietario_canal || ''
  }
})

async function handleConvert() {
  if (!props.lead) return
  
  loading.value = true
  try {
    const data = {
      criar_oportunidade: form.value.criar_oportunidade,
      nome_oportunidade: form.value.nome_oportunidade || `Oportunidade - ${props.lead.nome}`,
      valor_estimado: form.value.valor_estimado || 0,
      canal: form.value.canal || null
    }
    
    await api.post(`/leads/${props.lead.id}/converter/`, data)
    emit('converted')
    emit('close')
  } catch (error) {
    console.error('Erro ao converter lead:', error)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message
    alert('Erro ao converter lead: ' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.animate-fadeIn {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
