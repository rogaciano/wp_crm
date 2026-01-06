<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Contatos</h1>
      <button @click="openModal()" class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Contato</button>
    </div>

    <!-- Cards de Estatísticas/Filtros -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <!-- Card Total -->
      <div
        @click="filterByTipo(null)"
        :class="['card cursor-pointer transition-all duration-200 hover:shadow-lg border-2', selectedTipo === null ? 'border-primary-500 bg-primary-50' : 'border-transparent hover:border-gray-300']"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total de Contatos</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total }}</p>
          </div>
          <div class="h-12 w-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Cards por Tipo -->
      <div
        v-for="(tipo, index) in stats.por_tipo"
        :key="tipo.id || 'sem-tipo'"
        @click="filterByTipo(tipo.id)"
        :class="['card cursor-pointer transition-all duration-200 hover:shadow-lg border-2', selectedTipo === tipo.id ? 'border-primary-500 bg-primary-50' : 'border-transparent hover:border-gray-300']"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">{{ tipo.nome }}</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">{{ tipo.total }}</p>
          </div>
          <div
            :class="['h-12 w-12 rounded-lg flex items-center justify-center', getTipoColor(index)]"
          >
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-6">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar por nome, email ou cargo..."
        class="input"
        @input="loadContatos"
      />
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
                <th class="table-header">Email</th>
                <th class="table-header">Telefone</th>
                <th class="table-header">Cargo</th>
                <th class="table-header">Empresa</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="contato in contatos" :key="contato.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900">{{ contato.nome }}</td>
                <td class="table-cell text-gray-500">{{ contato.email }}</td>
                <td class="table-cell text-gray-500">{{ contato.telefone }}</td>
                <td class="table-cell text-gray-500">{{ contato.cargo }}</td>
                <td class="table-cell text-gray-500 font-medium">{{ contato.conta_nome }}</td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button @click="openModal(contato)" class="text-primary-600 hover:text-primary-700 font-medium">Editar</button>
                    <button @click="deleteContato(contato.id)" class="text-red-600 hover:text-red-700 font-medium">Excluir</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="contato in contatos" :key="contato.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="mb-3">
              <h3 class="font-bold text-gray-900">{{ contato.nome }}</h3>
              <p class="text-sm text-primary-600 font-medium">{{ contato.cargo || 'Contato' }}</p>
              <p class="text-xs text-gray-500 mt-1">Empresa: {{ contato.conta_nome || 'N/A' }}</p>
            </div>

            <div class="space-y-1.5 mb-4">
              <div v-if="contato.email" class="flex items-center text-xs text-gray-500">
                <svg class="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                {{ contato.email }}
              </div>
              <div v-if="contato.telefone" class="flex items-center text-xs text-gray-500">
                <svg class="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                {{ contato.telefone }}
              </div>
            </div>

            <div class="flex justify-end space-x-6 border-t pt-3 mt-2">
              <button @click="openModal(contato)" class="text-xs font-bold text-primary-600 uppercase tracking-widest flex items-center">
                 <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                 Editar
              </button>
              <button @click="deleteContato(contato.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest flex items-center">
                 <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                 Excluir
              </button>
            </div>
          </div>
        </div>

        <div v-if="contatos.length === 0" class="text-center py-12 text-gray-500">
          Nenhum contato encontrado.
        </div>
      </div>
    </div>

    <ContatoModal
      :show="showModal"
      :contato="selectedContato"
      @close="showModal = false"
      @saved="loadContatos"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import ContatoModal from '@/components/ContatoModal.vue'

const contatos = ref([])
const searchQuery = ref('')
const showModal = ref(false)
const selectedContato = ref(null)
const loading = ref(false)
const stats = ref({ total: 0, por_tipo: [] })
const selectedTipo = ref(null)

// Cores para os cards de tipos (gradientes bonitos)
const tipoColors = [
  'bg-gradient-to-br from-purple-500 to-purple-600',
  'bg-gradient-to-br from-green-500 to-green-600',
  'bg-gradient-to-br from-orange-500 to-orange-600',
  'bg-gradient-to-br from-pink-500 to-pink-600',
  'bg-gradient-to-br from-indigo-500 to-indigo-600',
  'bg-gradient-to-br from-red-500 to-red-600',
  'bg-gradient-to-br from-teal-500 to-teal-600',
  'bg-gradient-to-br from-yellow-500 to-yellow-600',
]

onMounted(() => {
  loadEstatisticas()
  loadContatos()
})

async function loadEstatisticas() {
  try {
    const response = await api.get('/contatos/estatisticas/')
    stats.value = response.data
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error)
  }
}

async function loadContatos() {
  loading.value = true
  try {
    const params = { search: searchQuery.value }

    // Adiciona filtro por tipo se selecionado
    if (selectedTipo.value !== null) {
      params.tipo_contato = selectedTipo.value
    }

    const response = await api.get('/contatos/', { params })
    contatos.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar contatos:', error)
  } finally {
    loading.value = false
  }
}

function getTipoColor(index) {
  return tipoColors[index % tipoColors.length]
}

function filterByTipo(tipoId) {
  selectedTipo.value = tipoId
  loadContatos()
}

function openModal(contato = null) {
  selectedContato.value = contato
  showModal.value = true
}

async function deleteContato(id) {
  if (!confirm('Tem certeza que deseja excluir este contato?')) return

  try {
    await api.delete(`/contatos/${id}/`)
    loadContatos()
    loadEstatisticas()
  } catch (error) {
    console.error('Erro ao excluir contato:', error)
    alert('Erro ao excluir contato')
  }
}
</script>
