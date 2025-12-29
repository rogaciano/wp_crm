<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Região' : 'Nova Região'"
    size="md"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nome da Região <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="input"
          placeholder="Ex: Pernambuco, Ceará, Sul..."
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Descrição / Observações
        </label>
        <textarea
          v-model="form.descricao"
          rows="3"
          class="input"
          placeholder="Opcional: Detalhes sobre a região ou abrangência..."
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
  regiao: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)

const form = ref({
  nome: '',
  descricao: ''
})

watch(() => props.regiao, (newRegiao) => {
  if (newRegiao) {
    isEdit.value = true
    form.value = { ...newRegiao }
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
  if (!form.value.nome) return
  
  loading.value = true
  try {
    if (isEdit.value) {
      await api.put(`/regioes/${form.value.id}/`, form.value)
    } else {
      await api.post('/regioes/', form.value)
    }
    
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar região:', error)
    alert('Erro ao salvar região: ' + (error.response?.data?.nome || error.message))
  } finally {
    loading.value = false
  }
}
</script>
