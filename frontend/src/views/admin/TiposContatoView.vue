<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Tipos de Contatos</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Tipo</button>
    </div>

    <div class="card overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else>
        <!-- Desktop Table -->
        <div class="hidden md:block overflow-x-auto">
          <table class="table">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">Nome</th>
                <th class="table-header">Descrição</th>
                <th class="table-header">Data Criação</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="tipo in tipos" :key="tipo.id" class="hover:bg-gray-50">
                <td class="table-cell font-bold text-gray-900">{{ tipo.nome }}</td>
                <td class="table-cell text-gray-500 max-w-xs truncate" :title="tipo.descricao">
                  {{ tipo.descricao || 'Sem descrição' }}
                </td>
                <td class="table-cell text-gray-500 text-xs">
                  {{ formatDate(tipo.data_criacao) }}
                </td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button @click="openEditModal(tipo)" class="text-primary-600 hover:text-primary-700 font-bold text-xs uppercase tracking-widest">Editar</button>
                    <button @click="deleteTipo(tipo.id)" class="text-red-600 hover:text-red-700 font-bold text-xs uppercase tracking-widest">Excluir</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="tipo in tipos" :key="tipo.id" class="p-4 active:bg-gray-50 transition-colors">
            <h3 class="font-bold text-gray-900 mb-1">{{ tipo.nome }}</h3>
            <p v-if="tipo.descricao" class="text-sm text-gray-500 mb-2">{{ tipo.descricao }}</p>
            <p class="text-[10px] text-gray-400 font-medium">Criado em: {{ formatDate(tipo.data_criacao) }}</p>

            <div class="flex justify-end space-x-6 border-t pt-3 mt-4">
              <button @click="openEditModal(tipo)" class="text-xs font-bold text-primary-600 uppercase tracking-widest">Editar</button>
              <button @click="deleteTipo(tipo.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest">Excluir</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <TipoContatoModal
      :show="showModal"
      :tipoContato="selectedTipo"
      @close="closeModal"
      @saved="loadTipos"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import TipoContatoModal from '@/components/TipoContatoModal.vue'

const tipos = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedTipo = ref(null)

onMounted(() => {
  loadTipos()
})

async function loadTipos() {
  loading.value = true
  try {
    const response = await api.get('/tipos-contato/')
    tipos.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar tipos de contato:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedTipo.value = null
  showModal.value = true
}

function openEditModal(tipo) {
  selectedTipo.value = tipo
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedTipo.value = null
}

async function deleteTipo(id) {
  if (!confirm('Tem certeza que deseja excluir este tipo de contato? Contatos vinculados a ele ficarão sem tipo.')) return
  try {
    await api.delete(`/tipos-contato/${id}/`)
    loadTipos()
  } catch (error) {
    console.error('Erro ao excluir tipo de contato:', error)
    alert('Erro ao excluir tipo de contato.')
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}
</script>
