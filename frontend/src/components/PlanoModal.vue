<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Plano' : 'Novo Plano'"
    size="md"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Nome do Plano <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.nome"
          type="text"
          required
          class="input"
          placeholder="Ex: DAPIC LIGHT"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Preço Mensal (R$) <span class="text-red-500">*</span>
          </label>
          <input
            v-model.number="form.preco_mensal"
            type="number"
            step="0.01"
            required
            class="input font-bold text-primary-600"
            placeholder="0,00"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Preço Anual (R$)
          </label>
          <input
            v-model.number="form.preco_anual"
            type="number"
            step="0.01"
            class="input font-bold text-violet-600"
            placeholder="0,00"
          />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Descrição
        </label>
        <textarea
          v-model="form.descricao"
          rows="2"
          class="input"
          placeholder="Breve descrição do plano..."
        ></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2 flex justify-between items-center">
          Recursos / Benefícios
          <button 
            type="button" 
            @click="addRecurso"
            class="text-[10px] bg-primary-100 text-primary-600 px-2 py-1 rounded-full font-bold hover:bg-primary-200 transition-colors"
          >
            + Adicionar
          </button>
        </label>
        
        <div class="space-y-2 max-h-48 overflow-y-auto p-1">
          <div v-for="(recurso, index) in form.recursos" :key="index" class="flex gap-2">
            <input
              v-model="form.recursos[index]"
              type="text"
              class="input text-sm py-1.5"
              placeholder="Ex: 1 CNPJ"
            />
            <button 
              type="button" 
              @click="removeRecurso(index)"
              class="text-red-400 hover:text-red-600 p-1"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>
          <div v-if="form.recursos.length === 0" class="text-center py-4 text-xs text-gray-400 border-2 border-dashed border-gray-100 rounded-xl">
            Nenhum recurso adicionado.
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
  plano: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)

const form = ref({
  nome: '',
  preco_mensal: 0,
  preco_anual: 0,
  descricao: '',
  recursos: []
})

watch(() => props.plano, (newPlano) => {
  if (newPlano) {
    isEdit.value = true
    form.value = { 
      ...newPlano,
      recursos: Array.isArray(newPlano.recursos) ? [...newPlano.recursos] : []
    }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    nome: '',
    preco_mensal: 0,
    preco_anual: 0,
    descricao: '',
    recursos: []
  }
}

function addRecurso() {
  form.value.recursos.push('')
}

function removeRecurso(index) {
  form.value.recursos.splice(index, 1)
}

async function handleSubmit() {
  if (!form.value.nome || form.value.preco_mensal === undefined) return
  
  loading.value = true
  try {
    const data = { 
      ...form.value,
      // Limpar recursos vazios
      recursos: form.value.recursos.filter(r => r.trim() !== '')
    }
    
    if (isEdit.value) {
      await api.put(`/planos/${form.value.id}/`, data)
    } else {
      await api.post('/planos/', data)
    }
    
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar plano:', error)
    alert('Erro ao salvar plano: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>
