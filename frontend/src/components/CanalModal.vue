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
        <input v-model="form.nome" @input="generateSlug" type="text" required class="input" placeholder="Ex: Vendas Diretas, Parceiro X" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Slug (URL do Diagnóstico)
          <span class="text-gray-400 font-normal">- usado no link público</span>
        </label>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">/d/</span>
          <input 
            v-model="form.slug" 
            type="text" 
            class="input flex-1" 
            placeholder="ex: pernambuco"
            pattern="[a-z0-9-]+"
          />
        </div>
        <p class="mt-1 text-xs text-gray-500 italic">
          Link: <code class="bg-gray-100 px-1 rounded">{{ baseUrl }}/d/{{ form.slug || 'slug-do-canal' }}</code>
        </p>
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
import { ref, watch, onMounted, computed } from 'vue'
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
  slug: '',
  responsavel: ''
})

// URL base para mostrar no preview
const baseUrl = computed(() => {
  return window.location.origin
})

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  try {
    const response = await api.get('/usuarios/')
    users.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar usuários:', error)
  }
}

// Gera slug automaticamente a partir do nome (apenas se ainda não tem slug)
function generateSlug() {
  if (!isEdit.value || !form.value.slug) {
    form.value.slug = form.value.nome
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove acentos
      .replace(/[^a-z0-9]+/g, '-')     // Substitui não alfanuméricos por -
      .replace(/^-+|-+$/g, '')          // Remove - do início/fim
  }
}

watch(() => props.canal, (newCanal) => {
  if (newCanal) {
    isEdit.value = true
    form.value = { 
      ...newCanal,
      slug: newCanal.slug || ''
    }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    nome: '',
    slug: '',
    responsavel: ''
  }
}

async function handleSubmit() {
  if (!form.value.nome) return
  
  loading.value = true
  try {
    const data = { 
      ...form.value,
      slug: form.value.slug || null
    }
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
