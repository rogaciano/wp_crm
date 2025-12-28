<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Canal' : 'Novo Canal'"
    size="md"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome do Canal</label>
        <input v-model="form.nome" type="text" required class="input" placeholder="Ex: Vendas Diretas, Parceiro X" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Responsável pelo Canal</label>
        <select v-model="form.responsavel" class="input">
          <option value="">Selecione um responsável...</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.first_name }} {{ user.last_name }} (@{{ user.username }})
          </option>
        </select>
        <p class="mt-1 text-xs text-gray-500 italic">O responsável terá acesso a todos os dados deste canal.</p>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  canal: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)
const users = ref([])

const form = ref({
  nome: '',
  responsavel: ''
})

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  try {
    const response = await api.get('/usuarios/')
    // Filtrar apenas Admins ou Responsáveis para serem donos de canal? 
    // Por enquanto permitir qualquer um para flexibilidade
    users.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar usuários:', error)
  }
}

watch(() => props.canal, (newCanal) => {
  if (newCanal) {
    isEdit.value = true
    form.value = { ...newCanal }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    nome: '',
    responsavel: ''
  }
}

async function handleSubmit() {
  if (!form.value.nome) return
  
  loading.value = true
  try {
    const data = { ...form.value }
    if (!data.responsavel) data.responsavel = null

    if (isEdit.value) {
      await api.put(`/canais/${form.value.id}/`, data)
    } else {
      await api.post('/canais/', data)
    }
    
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar canal:', error)
    alert('Erro ao salvar canal')
  } finally {
    loading.value = false
  }
}
</script>
