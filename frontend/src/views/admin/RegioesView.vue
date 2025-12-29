<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Regiões de Suporte</h1>
        <p class="text-sm text-gray-500">Gerencie as regiões para distribuição de leads e faturamento.</p>
      </div>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm tracking-wide font-black uppercase text-xs">
        + Nova Região
      </button>
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
              <tr v-for="regiao in regioes" :key="regiao.id" class="hover:bg-gray-50 transition-colors">
                <td class="table-cell">
                  <div class="flex items-center">
                    <div class="h-8 w-8 rounded-lg bg-primary-100 text-primary-600 flex items-center justify-center mr-3 font-bold">
                      {{ regiao.nome.charAt(0) }}
                    </div>
                    <span class="font-bold text-gray-900">{{ regiao.nome }}</span>
                  </div>
                </td>
                <td class="table-cell text-gray-500 max-w-xs truncate">{{ regiao.descricao || '-' }}</td>
                <td class="table-cell text-gray-500">{{ formatDate(regiao.data_criacao) }}</td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button @click="openEditModal(regiao)" class="text-primary-600 hover:text-primary-700 font-bold text-xs uppercase tracking-tighter">Editar</button>
                    <button @click="deleteRegiao(regiao.id)" class="text-red-500 hover:text-red-700 font-bold text-xs uppercase tracking-tighter">Excluir</button>
                  </div>
                </td>
              </tr>
              <tr v-if="regioes.length === 0">
                <td colspan="4" class="text-center py-8 text-gray-400 italic">Nenhuma região cadastrada.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="regiao in regioes" :key="regiao.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="flex justify-between items-start mb-2">
              <h3 class="font-bold text-gray-900 text-lg">{{ regiao.nome }}</h3>
              <span class="text-[10px] text-gray-400">{{ formatDate(regiao.data_criacao) }}</span>
            </div>
            
            <p class="text-sm text-gray-600 mb-4">{{ regiao.descricao || 'Sem descrição.' }}</p>

            <div class="flex justify-end space-x-6 border-t pt-3">
              <button @click="openEditModal(regiao)" class="text-xs font-bold text-primary-600 uppercase tracking-widest">Editar</button>
              <button @click="deleteRegiao(regiao.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest">Excluir</button>
            </div>
          </div>
          <div v-if="regioes.length === 0" class="p-8 text-center text-gray-400 italic">
            Nenhuma região cadastrada.
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <RegiaoModal
      :show="showModal"
      :regiao="selectedRegiao"
      @close="closeModal"
      @saved="loadRegioes"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import RegiaoModal from '@/components/RegiaoModal.vue'

const regioes = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedRegiao = ref(null)

onMounted(() => {
  loadRegioes()
})

async function loadRegioes() {
  loading.value = true
  try {
    const response = await api.get('/regioes/')
    regioes.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar regiões:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedRegiao.value = null
  showModal.value = true
}

function openEditModal(regiao) {
  selectedRegiao.value = regiao
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedRegiao.value = null
}

async function deleteRegiao(id) {
  if (!confirm('Tem certeza que deseja excluir esta região? Isso pode afetar usuários e oportunidades vinculados.')) return
  try {
    await api.delete(`/regioes/${id}/`)
    loadRegioes()
  } catch (error) {
    console.error('Erro ao excluir região:', error)
    alert('Erro ao excluir região. Verifique se existem registros vinculados.')
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}
</script>
