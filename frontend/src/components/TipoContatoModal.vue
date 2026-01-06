<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Tipo de Contato' : 'Novo Tipo de Contato'"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="flex items-start gap-4">
        <!-- Campo Emoji -->
        <div class="w-24 flex-shrink-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Emoji
          </label>
          <div class="relative">
            <input
              v-model="form.emoji"
              type="text"
              maxlength="4"
              class="input text-center text-3xl h-16"
              placeholder="👤"
            />
          </div>
          <p class="text-xs text-gray-400 mt-1 text-center">Copie e cole</p>
        </div>
        
        <!-- Campo Nome -->
        <div class="flex-1">
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
          <!-- Preview do tipo -->
          <div class="mt-2 p-2 bg-gray-50 rounded-lg inline-flex items-center gap-2 text-sm text-gray-600">
            <span class="text-xl">{{ form.emoji || '👤' }}</span>
            <span>{{ form.nome || 'Nome do tipo' }}</span>
          </div>
        </div>
      </div>

      <!-- Emojis sugeridos -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Sugestões de Emoji</label>
        <div class="flex flex-wrap gap-2">
          <button 
            v-for="emoji in emojisSugeridos" 
            :key="emoji"
            type="button"
            @click="form.emoji = emoji"
            class="w-10 h-10 text-xl flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
            :class="form.emoji === emoji ? 'bg-primary-100 ring-2 ring-primary-500' : 'bg-gray-50'"
          >
            {{ emoji }}
          </button>
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

const emojisSugeridos = ['👤', '💼', '🎯', '💰', '📞', '🤝', '⭐', '👑', '🔑', '📋', '💎', '🚀']

const form = ref({
  nome: '',
  emoji: '',
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
    emoji: '',
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
