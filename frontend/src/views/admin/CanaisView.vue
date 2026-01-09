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
                <th class="table-header text-center">WhatsApp</th>
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
                <td class="table-cell text-center">
                  <button 
                    @click="openWhatsappModal(canal)"
                    class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                    :class="canal.whatsapp_connected 
                      ? 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200' 
                      : canal.whatsapp_instance_id 
                        ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
                    </svg>
                    {{ canal.whatsapp_connected ? 'Conectado' : canal.whatsapp_instance_id ? 'Desconectado' : 'Configurar' }}
                  </button>
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
              <button 
                @click="openWhatsappModal(canal)"
                class="px-2 py-1 rounded-full text-xs font-bold"
                :class="canal.whatsapp_connected 
                  ? 'bg-emerald-100 text-emerald-700' 
                  : 'bg-gray-100 text-gray-600'"
              >
                <svg class="w-4 h-4 inline" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
                </svg>
              </button>
            </div>
            
            <div class="space-y-1 mt-2">
              <p class="text-sm text-gray-600 flex items-center">
                <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                Responsável: <span class="ml-1 font-medium text-gray-900">{{ canal.responsavel_nome || 'N/A' }}</span>
              </p>
              <p class="text-xs text-gray-400">
                {{ canal.total_vendedores }} vendedores • Criado em {{ formatDate(canal.data_criacao) }}
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

    <!-- Modal Canal -->
    <CanalModal
      :show="showModal"
      :canal="selectedCanal"
      @close="closeModal"
      @saved="loadCanais"
    />
    
    <!-- Modal WhatsApp -->
    <CanalWhatsappModal
      :show="showWhatsappModal"
      :canal="selectedCanalWhatsapp"
      @close="closeWhatsappModal"
      @updated="loadCanais"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import CanalModal from '@/components/CanalModal.vue'
import CanalWhatsappModal from '@/components/CanalWhatsappModal.vue'

const canais = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedCanal = ref(null)
const showWhatsappModal = ref(false)
const selectedCanalWhatsapp = ref(null)

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

function openWhatsappModal(canal) {
  selectedCanalWhatsapp.value = canal
  showWhatsappModal.value = true
}

function closeWhatsappModal() {
  showWhatsappModal.value = false
  selectedCanalWhatsapp.value = null
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

