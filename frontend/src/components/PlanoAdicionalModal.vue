<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Recurso Adicional' : 'Novo Recurso Adicional'"
    size="sm"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nome do Recurso <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="input"
          placeholder="Ex: Usuário adicional"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Preço (R$) <span class="text-red-500">*</span>
          </label>
          <input
            v-model.number="form.preco"
            type="number"
            step="0.01"
            required
            class="input font-bold text-emerald-600"
            placeholder="0,00"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Unidade
          </label>
          <input
            v-model="form.unidade"
            type="text"
            class="input"
            placeholder="Ex: usuário, CNPJ"
          />
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
  adicional: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)

const form = ref({
  nome: '',
  preco: 0,
  unidade: 'unidade'
})

watch(() => props.adicional, (newVal) => {
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
    preco: 0,
    unidade: 'unidade'
  }
}

async function handleSubmit() {
  if (!form.value.nome || form.value.preco === undefined) return
  
  loading.value = true
  try {
    if (isEdit.value) {
      await api.put(`/adicionais-plano/${form.value.id}/`, form.value)
    } else {
      await api.post('/adicionais-plano/', form.value)
    }
    
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar adicional:', error)
    alert('Erro ao salvar adicional')
  } finally {
    loading.value = false
  }
}
</script>
