<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Usuário' : 'Novo Usuário'"
    size="md"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
          <input v-model="form.first_name" type="text" required class="input" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sobrenome</label>
          <input v-model="form.last_name" type="text" required class="input" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
        <input v-model="form.username" type="text" required class="input" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
        <input v-model="form.email" type="email" required class="input" />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Perfil</label>
          <select v-model="form.perfil" required class="input">
            <option value="ADMIN">Administrador</option>
            <option value="RESPONSAVEL">Responsável</option>
            <option value="VENDEDOR">Vendedor</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Canal</label>
          <select v-model="form.canal" :required="form.perfil !== 'ADMIN'" class="input">
            <option value="">Nenhum / Admin</option>
            <option v-for="canal in canais" :key="canal.id" :value="canal.id">
              {{ canal.nome }}
            </option>
          </select>
        </div>
      </div>


      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
        <input v-model="form.telefone" type="text" class="input" placeholder="(00) 00000-0000" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Senha {{ isEdit ? '(deixe em branco para não alterar)' : '' }}
        </label>
        <input v-model="form.password" type="password" :required="!isEdit" class="input" />
      </div>

      <div v-if="isEdit" class="flex items-center space-x-2">
        <input v-model="form.is_active" type="checkbox" id="is_active" class="rounded text-primary-600 focus:ring-primary-500" />
        <label for="is_active" class="text-sm font-medium text-gray-700">Usuário Ativo</label>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Permissões de Funis</label>
        <div class="max-h-36 overflow-y-auto border border-gray-200 rounded-lg p-2 space-y-1">
          <label
            v-for="funil in funis"
            :key="funil.id"
            class="flex items-center gap-2 text-sm text-gray-700"
          >
            <input
              type="checkbox"
              :value="funil.id"
              v-model="form.funis_acesso"
              class="rounded text-primary-600 focus:ring-primary-500"
            />
            <span>{{ funil.nome }} <span class="text-xs text-gray-400">({{ getTipoFunilLabel(funil.tipo) }})</span></span>
          </label>
          <div v-if="!funis.length" class="text-xs text-gray-400">Nenhum funil disponível.</div>
        </div>
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
  usuario: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)
const canais = ref([])
const funis = ref([])

const form = ref({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  perfil: 'VENDEDOR',
  canal: '',
  telefone: '',
  password: '',
  is_active: true,
  funis_acesso: [],
})

onMounted(() => {
  loadCanais()
  loadFunis()
})

async function loadCanais() {
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar canais:', error)
  }
}

async function loadFunis() {
  try {
    const response = await api.get('/funis/')
    funis.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar funis:', error)
  }
}

function getTipoFunilLabel(tipo) {
  const labels = {
    VENDAS: 'Vendas',
    POS_VENDA: 'Pós-Venda',
    SUPORTE: 'Suporte'
  }
  return labels[tipo] || tipo
}

watch(() => props.usuario, (newUsuario) => {
  if (newUsuario) {
    isEdit.value = true
    form.value = { 
      ...newUsuario,
      funis_acesso: (newUsuario.funis_acesso || []).map(id => Number(id)),
      password: '' // Não carregar hash da senha
    }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    perfil: 'VENDEDOR',
    canal: '',
    telefone: '',
    password: '',
    is_active: true,
    funis_acesso: []
  }
}

async function handleSubmit() {
  loading.value = true
  try {
    const data = { ...form.value }
    if (isEdit.value && !data.password) {
      delete data.password
    }
    if (!data.canal) delete data.canal

    if (isEdit.value) {
      await api.put(`/usuarios/${form.value.id}/`, data)
    } else {
      await api.post('/usuarios/', data)
    }
    
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar usuário:', error)
    alert('Erro ao salvar usuário: ' + (error.response?.data?.detail || JSON.stringify(error.response?.data)))
  } finally {
    loading.value = false
  }
}
</script>
