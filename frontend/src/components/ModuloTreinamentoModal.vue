<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
    <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-gray-900">
            {{ isEditing ? 'Editar Módulo' : 'Novo Módulo de Treinamento' }}
          </h2>
          <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div>
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Nome do Módulo *</label>
            <input v-model="form.nome" type="text" class="input" placeholder="Ex: Módulo Financeiro" required />
          </div>

          <div>
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Descrição</label>
            <textarea v-model="form.descricao" class="input" rows="3" placeholder="Conteúdo e escopo do módulo..."></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Carga Horária (min)</label>
              <input v-model.number="form.carga_horaria_estimada" type="number" class="input" min="1" placeholder="60" />
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Ordem</label>
              <input v-model.number="form.ordem" type="number" class="input" min="0" placeholder="0" />
            </div>
          </div>

          <div class="flex items-center gap-3">
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="form.ativo" class="sr-only peer" />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
            <span class="text-sm font-medium text-gray-700">Módulo ativo</span>
          </div>

          <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {{ error }}
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button type="button" @click="$emit('close')" class="btn btn-white">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Salvando...' : (isEditing ? 'Salvar Alterações' : 'Criar Módulo') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  modulo: Object
})

const emit = defineEmits(['close', 'saved'])

const isEditing = computed(() => !!props.modulo?.id)

const form = ref({
  nome: '',
  descricao: '',
  carga_horaria_estimada: 60,
  ordem: 0,
  ativo: true
})

const saving = ref(false)
const error = ref('')

watch(() => props.show, (val) => {
  if (val) {
    error.value = ''
    if (props.modulo) {
      form.value = {
        nome: props.modulo.nome || '',
        descricao: props.modulo.descricao || '',
        carga_horaria_estimada: props.modulo.carga_horaria_estimada || 60,
        ordem: props.modulo.ordem || 0,
        ativo: props.modulo.ativo !== false
      }
    } else {
      form.value = { nome: '', descricao: '', carga_horaria_estimada: 60, ordem: 0, ativo: true }
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''
  try {
    if (isEditing.value) {
      await api.patch(`/modulos-treinamento/${props.modulo.id}/`, form.value)
    } else {
      await api.post('/modulos-treinamento/', form.value)
    }
    emit('saved')
    emit('close')
  } catch (err) {
    console.error('Erro ao salvar módulo:', err)
    error.value = err.response?.data?.detail || 'Erro ao salvar módulo de treinamento.'
  } finally {
    saving.value = false
  }
}
</script>
