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
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar nome, email..."
          class="input"
          @input="onSearchInput"
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
          <option value="Cold Call">Cold Call</option>
          <option value="Outro">Outro</option>
        </select>
        <select v-model="funilFilter" class="input" @change="loadLeads">
          <option value="">Todos os Funis</option>
          <option v-for="f in funisOptions" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
        <select v-if="authStore.isAdmin" v-model="canalFilter" class="input" @change="loadLeads">
          <option value="">Todos os Canais</option>
          <option v-for="c in canaisOptions" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </div>
    </div>

    <!-- Indicadores (KPIs) -->
    <div v-if="!error" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 border-l-4" :style="{ borderLeftColor: kpi.color }">
        <div class="flex items-center justify-between mb-3">
          <div class="p-2 rounded-lg" :style="{ backgroundColor: kpi.color + '15' }">
            <component :is="kpi.icon" class="w-5 h-5" :style="{ color: kpi.color }" />
          </div>
          <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">{{ kpi.label }}</span>
        </div>
        <div>
          <div class="text-xl font-black text-gray-900 leading-none">
            {{ kpi.value }}{{ kpi.suffix }}
          </div>
          <div class="text-[10px] text-gray-500 mt-2 font-bold uppercase tracking-tight">
            {{ kpi.sub }}
          </div>
        </div>
      </div>
    </div>

    <!-- Tabela (Desktop) / Cards (Mobile) -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="error" class="p-6 text-center">
        <div class="text-red-500 font-bold mb-2 flex items-center justify-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          Erro ao carregar dados
        </div>
        <p class="text-gray-600 text-sm">{{ error }}</p>
        <button @click="loadLeads" class="mt-4 text-primary-600 font-bold hover:underline">Tentar novamente</button>
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
                <th class="table-header">Convertido Para</th>
                <th class="table-header text-center sticky right-0 bg-gray-50">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="lead in leads" :key="lead.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900 max-w-[180px] truncate" :title="lead.nome">{{ lead.nome }}</td>
                <td class="table-cell text-gray-500 max-w-[180px] truncate" :title="lead.email">{{ lead.email }}</td>
                <td class="table-cell text-gray-500">{{ lead.telefone }}</td>
                <td class="table-cell text-gray-500 max-w-[150px] truncate" :title="lead.empresa">{{ lead.empresa }}</td>
                <td class="table-cell">
                  <span 
                    class="px-2 py-1 text-[10px] font-black rounded-full uppercase tracking-wider"
                    :style="{ backgroundColor: lead.estagio_cor + '20', color: lead.estagio_cor }"
                  >
                    {{ lead.estagio_nome || lead.status }}
                  </span>
                </td>
                <td class="table-cell text-gray-500 italic">{{ lead.fonte }}</td>
                <td class="table-cell">
                  <span v-if="lead.oportunidade_convertida" class="text-xs text-green-600 font-medium" :title="lead.oportunidade_convertida_nome">
                    {{ lead.oportunidade_convertida_canal || 'Sem Canal' }}
                  </span>
                  <span v-else class="text-gray-400 text-xs">-</span>
                </td>
                <td class="table-cell sticky right-0 bg-white">
                  <div class="flex justify-center items-center gap-1">
                    <button
                      @click="openWhatsapp(lead)"
                      class="p-1.5 text-emerald-500 hover:bg-emerald-50 rounded-lg relative"
                      title="WhatsApp"
                    >
                      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
                      <span v-if="lead.whatsapp_nao_lidas > 0" class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-black text-white ring-2 ring-white">
                        {{ lead.whatsapp_nao_lidas }}
                      </span>
                    </button>
                    <button
                      v-if="lead.status !== 'Convertido'"
                      @click="converterLead(lead)"
                      class="p-1.5 text-green-600 hover:bg-green-50 rounded-lg"
                      title="Converter Lead"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                      </svg>
                    </button>
                    <button
                      @click="openEditModal(lead)"
                      class="p-1.5 text-primary-600 hover:bg-primary-50 rounded-lg"
                      title="Editar"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      @click="deleteLead(lead)"
                      class="p-1.5 text-red-600 hover:bg-red-50 rounded-lg"
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
              <span 
                class="px-2 py-0.5 text-[9px] font-black rounded-full uppercase tracking-tighter"
                :style="{ backgroundColor: lead.estagio_cor + '20', color: lead.estagio_cor }"
              >
                {{ lead.estagio_nome || lead.status }}
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
                @click="openWhatsapp(lead)"
                class="flex items-center text-xs font-bold text-emerald-600 uppercase tracking-wider relative"
              >
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
                WhatsApp
                <span v-if="lead.whatsapp_nao_lidas > 0" class="ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-black text-white">
                  {{ lead.whatsapp_nao_lidas }}
                </span>
              </button>
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

      <LeadConversionModal
        :show="showConversionModal"
        :lead="leadToConvert"
        @close="closeConversionModal"
        @converted="handleConverted"
      />

      <!-- WhatsApp -->
      <WhatsappChat
        :show="showWhatsapp"
        :number="whatsappData.number"
        :title="whatsappData.title"
        :lead="whatsappData.lead"
        @close="showWhatsapp = false"
        @messagesRead="whatsappStore.fetchUnreadCounts"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import LeadModal from '@/components/LeadModal.vue'
import LeadConversionModal from '@/components/LeadConversionModal.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'
import { useAuthStore } from '@/stores/auth'
import { useWhatsappStore } from '@/stores/whatsapp'

const authStore = useAuthStore()
const whatsappStore = useWhatsappStore()

// Ícones simples
const IconUsers = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354l1.108 3.541H16.8l-2.909 2.112 1.108 3.541-2.909-2.112-2.909 2.112 1.108-3.541-2.909-2.112h3.692L12 4.354z" /></svg>' }
const IconNew = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }
const IconTarget = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>' }
const IconPie = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" /></svg>' }

const leads = ref([])
const loading = ref(false)
const error = ref(null)
const showModal = ref(false)
const showConversionModal = ref(false)
const selectedLead = ref(null)
const leadToConvert = ref(null)
const searchQuery = ref('')
const statusFilter = ref('')
const fonteFilter = ref('')
const funilFilter = ref('')
const canalFilter = ref('')
const funisOptions = ref([])
const canaisOptions = ref([])

// WhatsApp
const showWhatsapp = ref(false)
const whatsappData = ref({
  number: '',
  title: '',
  lead: null
})

const stats = ref({
  total: 0,
  novos: 0,
  qualificados: 0,
  convertidos: 0,
  taxa_conversao: 0
})

const kpiCards = computed(() => [
  { 
    label: 'Total de Leads', 
    value: stats.value.total, 
    sub: 'Cadastrados no sistema', 
    icon: IconUsers, 
    color: '#6366F1' 
  },
  { 
    label: 'Novos Leads', 
    value: stats.value.novos, 
    sub: 'Aguardando contato', 
    icon: IconNew, 
    color: '#3B82F6' 
  },
  { 
    label: 'Qualificados', 
    value: stats.value.qualificados, 
    sub: 'Prontos para conversão', 
    icon: IconTarget, 
    color: '#8B5CF6' 
  },
  { 
    label: 'Taxa de Conversão', 
    value: stats.value.taxa_conversao, 
    suffix: '%',
    sub: 'Leads x Oportunidades', 
    icon: IconPie, 
    color: '#10B981' 
  }
])

onMounted(() => {
  loadLeads()
  loadFilterOptions()
})

async function loadFilterOptions() {
  try {
    const [funisRes, canaisRes] = await Promise.all([
      api.get('/funis/', { params: { tipo: 'LEAD' } }),
      authStore.isAdmin ? api.get('/canais/') : Promise.resolve({ data: [] })
    ])
    funisOptions.value = funisRes.data.results || funisRes.data
    canaisOptions.value = canaisRes.data.results || canaisRes.data
  } catch (err) {
    console.error('Erro ao carregar opções de filtro:', err)
  }
}

async function loadLeads() {
  loading.value = true
  error.value = null
  try {
    const params = {
      search: searchQuery.value,
      status: statusFilter.value,
      fonte: fonteFilter.value,
      funil: funilFilter.value,
      canal: canalFilter.value
    }
    
    const [listRes, statsRes] = await Promise.all([
      api.get('/leads/', { params }),
      api.get('/leads/stats/', { params })
    ])
    
    leads.value = listRes.data.results || listRes.data
    stats.value = statsRes.data
  } catch (err) {
    console.error('Erro ao carregar leads:', err)
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
function onSearchInput() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadLeads()
  }, 500)
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

function converterLead(lead) {
  leadToConvert.value = lead
  showConversionModal.value = true
}

function closeConversionModal() {
  showConversionModal.value = false
  leadToConvert.value = null
}

function handleConverted() {
  alert('Lead convertido com sucesso!')
  loadLeads()
}

function openWhatsapp(lead) {
  if (!lead.telefone) {
    alert('Lead sem telefone cadastrado.')
    return
  }
  // Remove formatação do telefone (mantém apenas números)
  let cleanNumber = lead.telefone.replace(/\D/g, '')

  // Adiciona código do país (55) se não estiver presente
  if (!cleanNumber.startsWith('55') && cleanNumber.length <= 11) {
    cleanNumber = '55' + cleanNumber
  }

  whatsappData.value = {
    number: cleanNumber,
    title: lead.nome,
    lead: lead.id
  }
  showWhatsapp.value = true
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
