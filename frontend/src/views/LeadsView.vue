<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Leads</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Novo Lead
      </button>
    </div>

    <!-- Filtros -->
    <div class="card mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por nome, email ou empresa..."
          class="input"
          @input="loadLeads"
        />
        <select v-model="statusFilter" class="input" @change="loadLeads">
          <option value="">Todos os Status</option>
          <option value="Novo">Novo</option>
          <option value="Contatado">Contatado</option>
          <option value="Qualificado">Qualificado</option>
          <option value="Convertido">Convertido</option>
          <option value="Descartado">Descartado</option>
        </select>
        <select v-model="fonteFilter" class="input" @change="loadLeads">
          <option value="">Todas as Fontes</option>
          <option value="Site">Site</option>
          <option value="Evento">Evento</option>
          <option value="Indicação">Indicação</option>
          <option value="LinkedIn">LinkedIn</option>
        </select>
      </div>
    </div>

    <!-- Tabela (Desktop) / Cards (Mobile) -->
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
                <th class="table-header">Empresa</th>
                <th class="table-header">Status</th>
                <th class="table-header">Fonte</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="lead in leads" :key="lead.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900">{{ lead.nome }}</td>
                <td class="table-cell text-gray-500">{{ lead.email }}</td>
                <td class="table-cell text-gray-500">{{ lead.telefone }}</td>
                <td class="table-cell text-gray-500">{{ lead.empresa }}</td>
                <td class="table-cell">
                  <span :class="getStatusClass(lead.status)">
                    {{ lead.status }}
                  </span>
                </td>
                <td class="table-cell text-gray-500 italic">{{ lead.fonte }}</td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button
                      v-if="lead.status !== 'Convertido'"
                      @click="converterLead(lead)"
                      class="text-green-600 hover:text-green-700 transition-colors"
                      title="Converter Lead"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                      </svg>
                    </button>
                    <button
                      @click="openEditModal(lead)"
                      class="text-primary-600 hover:text-primary-700 transition-colors"
                      title="Editar"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      @click="deleteLead(lead)"
                      class="text-red-600 hover:text-red-700 transition-colors"
                      title="Excluir"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Swipeable Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="lead in leads" :key="lead.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="flex justify-between items-start mb-2">
              <div>
                <h3 class="font-bold text-gray-900">{{ lead.nome }}</h3>
                <p class="text-sm text-gray-500">{{ lead.empresa || 'Sem empresa' }}</p>
              </div>
              <span :class="getStatusClass(lead.status)">
                {{ lead.status }}
              </span>
            </div>
            
            <div class="space-y-1 mb-4">
              <div class="flex items-center text-xs text-gray-500">
                <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                {{ lead.email || 'N/A' }}
              </div>
              <div class="flex items-center text-xs text-gray-500">
                <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                {{ lead.telefone || 'N/A' }}
              </div>
            </div>

            <div class="flex justify-end space-x-4 border-t pt-3 mt-2">
              <button
                v-if="lead.status !== 'Convertido'"
                @click="converterLead(lead)"
                class="flex items-center text-xs font-bold text-green-600 uppercase tracking-wider"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                Converter
              </button>
              <button
                @click="openEditModal(lead)"
                class="flex items-center text-xs font-bold text-primary-600 uppercase tracking-wider"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                Editar
              </button>
              <button
                @click="deleteLead(lead)"
                class="flex items-center text-xs font-bold text-red-600 uppercase tracking-wider"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                Excluir
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="leads.length === 0 && !loading" class="text-center py-12 text-gray-500">
        Nenhum lead encontrado
      </div>

      <!-- Modal -->
      <LeadModal
        :show="showModal"
        :lead="selectedLead"
        @close="closeModal"
        @saved="handleSaved"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import LeadModal from '@/components/LeadModal.vue'

const leads = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedLead = ref(null)
const searchQuery = ref('')
const statusFilter = ref('')
const fonteFilter = ref('')

onMounted(() => {
  loadLeads()
})

async function loadLeads() {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      status: statusFilter.value,
      fonte: fonteFilter.value
    }
    const response = await api.get('/leads/', { params })
    leads.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar leads:', error)
  } finally {
    loading.value = false
  }
}

function getStatusClass(status) {
  const classes = {
    'Novo': 'px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800',
    'Contatado': 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800',
    'Qualificado': 'px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800',
    'Convertido': 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800',
    'Descartado': 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800'
  }
  return classes[status] || 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800'
}

function openCreateModal() {
  selectedLead.value = null
  showModal.value = true
}

function openEditModal(lead) {
  selectedLead.value = lead
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedLead.value = null
}

function handleSaved() {
  loadLeads()
}

async function converterLead(lead) {
  if (!confirm(`Deseja converter o lead "${lead.nome}"?`)) return
  
  try {
    await api.post(`/leads/${lead.id}/converter/`, {
      criar_oportunidade: true,
      nome_oportunidade: `Oportunidade - ${lead.nome}`
    })
    alert('Lead convertido com sucesso!')
    loadLeads()
  } catch (error) {
    console.error('Erro ao converter lead:', error)
    alert('Erro ao converter lead')
  }
}

async function deleteLead(lead) {
  if (!confirm(`Deseja excluir o lead "${lead.nome}"?`)) return
  
  try {
    await api.delete(`/leads/${lead.id}/`)
    loadLeads()
  } catch (error) {
    console.error('Erro ao excluir lead:', error)
    alert('Erro ao excluir lead')
  }
}
</script>
