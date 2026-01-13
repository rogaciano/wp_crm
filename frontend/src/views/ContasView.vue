<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Contas</h1>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Nova Conta/Empresa
      </button>
    </div>

    <!-- Filtros -->
    <div class="card mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por nome, CNPJ ou email..."
          class="input flex-1"
          @input="loadContas"
        />
        <select 
          v-model="selectedCanal" 
          @change="loadContas"
          class="input sm:w-48"
        >
          <option :value="null">Todos os Canais</option>
          <option v-for="canal in canais" :key="canal.id" :value="canal.id">
            {{ canal.nome }}
          </option>
        </select>
      </div>
    </div>

    <!-- Grid de Cards -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="conta in contas"
        :key="conta.id"
        class="card hover:shadow-lg transition-shadow cursor-pointer"
        @click="viewConta(conta.id)"
      >
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">{{ conta.nome_empresa }}</h3>
            <p v-if="conta.cnpj" class="text-sm text-gray-500">CNPJ: {{ conta.cnpj }}</p>
          </div>
          <span class="px-2 py-1 text-xs rounded-full bg-primary-100 text-primary-800">
            {{ conta.setor || 'N/A' }}
          </span>
        </div>

        <div class="space-y-2 text-sm text-gray-600">
          <p v-if="conta.telefone_principal" class="flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            {{ conta.telefone_principal }}
          </p>
          
          <p v-if="conta.email" class="flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            {{ conta.email }}
          </p>
          
          <p v-if="conta.cidade" class="flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {{ conta.cidade }}, {{ conta.estado }}
          </p>
        </div>

        <div class="mt-4 pt-4 border-t flex justify-between items-center">
          <div class="flex space-x-4 text-sm text-gray-600">
            <span>{{ conta.total_contatos }} contatos</span>
            <span>{{ conta.total_oportunidades }} oportunidades</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="contas.length === 0 && !loading" class="text-center py-12 text-gray-500">
      Nenhuma conta encontrada
    </div>

    <!-- Modal -->
    <ContaModal
      :show="showModal"
      :conta="selectedConta"
      @close="closeModal"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import ContaModal from '@/components/ContaModal.vue'

const router = useRouter()
const contas = ref([])
const canais = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedConta = ref(null)
const searchQuery = ref('')
const selectedCanal = ref(null)

onMounted(async () => {
  await loadCanais()
  await loadContas()
})

async function loadCanais() {
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar canais:', error)
  }
}

async function loadContas() {
  loading.value = true
  try {
    const params = { search: searchQuery.value }
    if (selectedCanal.value) {
      params.canal = selectedCanal.value
    }
    const response = await api.get('/contas/', { params })
    contas.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar contas:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedConta.value = null
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedConta.value = null
}

function handleSaved() {
  loadContas()
}

function viewConta(id) {
  router.push(`/contas/${id}`)
}
</script>
