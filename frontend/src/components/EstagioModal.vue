<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Definição de Estágio' : 'Nova Definição de Estágio'"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nome do Estágio <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="input"
          placeholder="Ex: Qualificação, Proposta, Novo Lead"
        />
        <p class="text-[10px] text-gray-400 mt-1">Este nome será único no sistema e poderá ser usado em múltiplos funis.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Tipo Global <span class="text-red-500">*</span>
          </label>
          <select v-model="form.tipo" required class="input">
            <option value="ABERTO">Aberto (Em andamento / Em atendimento)</option>
            <option value="GANHO">Ganho / Sucesso (Resolvido)</option>
            <option value="PERDIDO">Perdido / Insucesso (Cancelado / Descartado)</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Cor Padrão
          </label>
          <div class="flex space-x-2">
            <input
              v-model="form.cor"
              type="color"
              class="w-10 h-10 p-1 rounded-lg border border-gray-200 cursor-pointer"
            />
            <input
              v-model="form.cor"
              type="text"
              class="input flex-1"
              placeholder="#000000"
            />
          </div>
        </div>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  estagio: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)

const form = ref({
  nome: '',
  tipo: 'ABERTO',
  cor: '#3B82F6'
})

watch(() => props.estagio, (newEstagio) => {
  if (newEstagio) {
    isEdit.value = true
    form.value = { ...newEstagio }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    nome: '',
    tipo: 'ABERTO',
    cor: '#3B82F6'
  }
}

async function handleSubmit() {
  loading.value = true
  try {
    if (isEdit.value) {
      await api.put(`/estagios-funil/${form.value.id}/`, form.value)
    } else {
      await api.post('/estagios-funil/', form.value)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar definição de estágio:', error)
    alert('Erro ao salvar estágio: ' + (error.response?.data?.detail || JSON.stringify(error.response?.data) || 'Erro desconhecido'))
  } finally {
    loading.value = false
  }
}
</script>
