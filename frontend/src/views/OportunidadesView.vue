<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Oportunidades</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Nova Oportunidade
      </button>
    </div>

    <!-- Filtro rápido -->
    <div class="card mb-6 p-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar por nome ou conta..."
        class="input"
        @input="loadOportunidades"
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
                <th class="table-header">Conta</th>
                <th class="table-header">Valor</th>
                <th class="table-header">Estágio</th>
                <th class="table-header">Previsão</th>
                <th class="table-header">Probabilidade</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="oportunidade in oportunidades" :key="oportunidade.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900">{{ oportunidade.nome }}</td>
                <td class="table-cell text-gray-500">{{ oportunidade.conta_nome }}</td>
                <td class="table-cell font-semibold text-green-600">
                  R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </td>
                <td class="table-cell">
                  <span class="px-2 py-1 text-xs rounded-full font-medium" :style="{ backgroundColor: oportunidade.estagio_cor + '20', color: oportunidade.estagio_cor }">
                    {{ oportunidade.estagio_nome }}
                  </span>
                </td>
                <td class="table-cell text-gray-500">{{ formatDate(oportunidade.data_fechamento_esperada) }}</td>
                <td class="table-cell text-gray-500">{{ oportunidade.probabilidade }}%</td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button @click="openEditModal(oportunidade)" class="text-primary-600 hover:text-primary-700 font-medium" title="Editar">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click="deleteOportunidade(oportunidade.id)" class="text-red-600 hover:text-red-700 font-medium" title="Excluir">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="oportunidade in oportunidades" :key="oportunidade.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="flex justify-between items-start mb-2">
               <div @click="openEditModal(oportunidade)" class="cursor-pointer">
                  <h3 class="font-bold text-gray-900">{{ oportunidade.nome }}</h3>
                  <p class="text-sm text-gray-500">{{ oportunidade.conta_nome }}</p>
               </div>
               <span class="px-2 py-1 text-[10px] font-bold uppercase rounded-full" :style="{ backgroundColor: oportunidade.estagio_cor + '20', color: oportunidade.estagio_cor }">
                  {{ oportunidade.estagio_nome }}
               </span>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mt-3 pt-3 border-t border-gray-50 cursor-pointer" @click="openEditModal(oportunidade)">
               <div>
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Valor Estimado</p>
                  <p class="text-sm font-bold text-green-600">R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR') }}</p>
               </div>
               <div class="text-right">
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Probabilidade</p>
                  <p class="text-sm font-bold text-gray-700">{{ oportunidade.probabilidade }}%</p>
               </div>
            </div>

            <div class="flex justify-end space-x-6 border-t pt-3 mt-4">
              <button @click="openEditModal(oportunidade)" class="text-xs font-bold text-primary-600 uppercase tracking-widest flex items-center">
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                 Editar
              </button>
              <button @click="deleteOportunidade(oportunidade.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest flex items-center">
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                 Excluir
              </button>
            </div>
          </div>
        </div>

        <div v-if="oportunidades.length === 0" class="text-center py-12 text-gray-500">
          Nenhuma oportunidade registrada.
        </div>
      </div>
    </div>

    <!-- Modal -->
    <OportunidadeModal
      :show="showModal"
      :oportunidade="selectedOportunidade"
      @close="closeModal"
      @saved="loadOportunidades"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import OportunidadeModal from '@/components/OportunidadeModal.vue'

const oportunidades = ref([])
const loading = ref(false)
const searchQuery = ref('')
const showModal = ref(false)
const selectedOportunidade = ref(null)

onMounted(() => {
  loadOportunidades()
})

async function loadOportunidades() {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await api.get('/oportunidades/', { params })
    oportunidades.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar oportunidades:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedOportunidade.value = null
  showModal.value = true
}

function openEditModal(oportunidade) {
  selectedOportunidade.value = oportunidade
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedOportunidade.value = null
}

async function deleteOportunidade(id) {
  if (!confirm('Tem certeza que deseja excluir esta oportunidade?')) return
  
  try {
    await api.delete(`/oportunidades/${id}/`)
    await loadOportunidades()
  } catch (error) {
    console.error('Erro ao excluir oportunidade:', error)
    alert('Erro ao excluir oportunidade')
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}
</script>
