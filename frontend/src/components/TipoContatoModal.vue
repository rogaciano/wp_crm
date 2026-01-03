<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Tipo de Contato' : 'Novo Tipo de Contato'"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nome <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="input"
          placeholder="Ex: Padrão, Indicador, Decisor, Influenciador"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Descrição
        </label>
        <textarea
          v-model="form.descricao"
          rows="3"
          class="input"
          placeholder="Descreva o propósito deste tipo de contato..."
        ></textarea>
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
  tipoContato: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)

const form = ref({
  nome: '',
  descricao: ''
})

watch(() => props.tipoContato, (newVal) => {
  if (newVal) {
    isEdit.value = true
    form.value = { ...newVal }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    nome: '',
    descricao: ''
  }
}

async function handleSubmit() {
  loading.value = true
  try {
    if (isEdit.value) {
      await api.put(`/tipos-contato/${form.value.id}/`, form.value)
    } else {
      await api.post('/tipos-contato/', form.value)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar tipo de contato:', error)
    alert('Erro ao salvar tipo de contato: ' + (error.response?.data?.detail || 'Erro desconhecido'))
  } finally {
    loading.value = false
  }
}
</script>
