<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Gestão de Canais</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Canal</button>
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
                <th class="table-header">Responsável</th>
                <th class="table-header text-center">Vendedores</th>
                <th class="table-header">Data Criação</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="canal in canais" :key="canal.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900">{{ canal.nome }}</td>
                <td class="table-cell text-gray-500">{{ canal.responsavel_nome || 'Sem responsável' }}</td>
                <td class="table-cell text-center">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ canal.total_vendedores }}
                  </span>
                </td>
                <td class="table-cell text-gray-500">{{ formatDate(canal.data_criacao) }}</td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button @click="openEditModal(canal)" class="text-primary-600 hover:text-primary-700 font-medium">Editar</button>
                    <button @click="deleteCanal(canal.id)" class="text-red-600 hover:text-red-700 font-medium">Excluir</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="canal in canais" :key="canal.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="flex justify-between items-start mb-2">
              <h3 class="font-bold text-gray-900 text-lg">{{ canal.nome }}</h3>
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-primary-100 text-primary-800 uppercase">
                {{ canal.total_vendedores }} Vendedores
              </span>
            </div>
            
            <div class="space-y-1 mt-2">
              <p class="text-sm text-gray-600 flex items-center">
                <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                Responsável: <span class="ml-1 font-medium text-gray-900">{{ canal.responsavel_nome || 'N/A' }}</span>
              </p>
              <p class="text-xs text-gray-400 flex items-center">
                <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                Criado em: {{ formatDate(canal.data_criacao) }}
              </p>
            </div>

            <div class="flex justify-end space-x-6 border-t pt-3 mt-4">
              <button @click="openEditModal(canal)" class="text-xs font-bold text-primary-600 uppercase tracking-widest">Editar</button>
              <button @click="deleteCanal(canal.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest">Excluir</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <CanalModal
      :show="showModal"
      :canal="selectedCanal"
      @close="closeModal"
      @saved="loadCanais"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import CanalModal from '@/components/CanalModal.vue'

const canais = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedCanal = ref(null)

onMounted(() => {
  loadCanais()
})

async function loadCanais() {
  loading.value = true
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar canais:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedCanal.value = null
  showModal.value = true
}

function openEditModal(canal) {
  selectedCanal.value = canal
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedCanal.value = null
}

async function deleteCanal(id) {
  if (!confirm('Tem certeza que deseja excluir este canal?')) return
  try {
    await api.delete(`/canais/${id}/`)
    loadCanais()
  } catch (error) {
    console.error('Erro ao excluir canal:', error)
    alert('Erro ao excluir canal')
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}
</script>
