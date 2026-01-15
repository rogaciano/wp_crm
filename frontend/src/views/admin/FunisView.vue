<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Gestão de Funis</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Funil</button>
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
                <th class="table-header">Status</th>
                <th class="table-header text-center">Acesso</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="funil in funis" :key="funil.id" class="hover:bg-gray-50">
                <td class="table-cell font-bold text-gray-900">{{ funil.nome }}</td>
                <td class="table-cell">
                  <span 
                    class="px-2 py-0.5 text-[9px] font-black rounded-full uppercase tracking-tighter"
                    :class="funil.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                  >
                    {{ funil.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td class="table-cell text-center text-xs text-gray-500 font-medium">
                  {{ funil.usuarios?.length || 0 }} usuários
                </td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button @click="openEditModal(funil)" class="text-primary-600 hover:text-primary-700 font-bold text-xs uppercase tracking-widest">Editar</button>
                    <button @click="deleteFunil(funil.id)" class="text-red-600 hover:text-red-700 font-bold text-xs uppercase tracking-widest">Excluir</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="funil in funis" :key="funil.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="flex justify-between items-start mb-2">
              <h3 class="font-bold text-gray-900">{{ funil.nome }}</h3>
              <span 
                class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-tighter"
                :class="funil.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
              >
                {{ funil.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </div>
            
            <div class="flex items-center space-x-2 mt-2">
              <span class="text-[10px] text-gray-400 font-bold uppercase">{{ funil.usuarios?.length || 0 }} usuários com acesso</span>
            </div>

            <div class="flex justify-end space-x-6 border-t pt-3 mt-4">
              <button @click="openEditModal(funil)" class="text-xs font-bold text-primary-600 uppercase tracking-widest">Editar</button>
              <button @click="deleteFunil(funil.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest">Excluir</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <FunilModal
      :show="showModal"
      :funil="selectedFunil"
      @close="closeModal"
      @saved="loadFunis"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import FunilModal from '@/components/FunilModal.vue'

const funis = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedFunil = ref(null)

onMounted(() => {
  loadFunis()
})

async function loadFunis() {
  loading.value = true
  try {
    const response = await api.get('/funis/')
    funis.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar funis:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedFunil.value = null
  showModal.value = true
}

function openEditModal(funil) {
  selectedFunil.value = funil
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedFunil.value = null
}

async function deleteFunil(id) {
  if (!confirm('Tem certeza que deseja excluir este funil? Todos os estágios associados serão afetados.')) return
  try {
    await api.delete(`/funis/${id}/`)
    loadFunis()
  } catch (error) {
    console.error('Erro ao excluir funil:', error)
    alert('Erro ao excluir funil. Verifique se existem registros vinculados.')
  }
}
</script>
