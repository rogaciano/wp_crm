<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Contas</h1>
      <div class="flex gap-2 flex-wrap w-full sm:w-auto">
        <button @click="showBatchModal = true" class="btn btn-secondary w-full sm:w-auto text-sm">
          Endereços em Lote
        </button>
        <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
          + Nova Conta/Empresa
        </button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="card mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por nome, CNPJ ou email..."
          class="input flex-1"
          @input="debouncedSearch"
        />
        <select 
          v-model="selectedCanal" 
          @change="resetAndLoad"
          class="input sm:w-48"
        >
          <option :value="null">Todos os Canais</option>
          <option v-for="canal in canais" :key="canal.id" :value="canal.id">
            {{ canal.nome }}
          </option>
        </select>
        <select
          v-model="selectedVisaoComercial"
          @change="resetAndLoad"
          class="input sm:w-56"
        >
          <option value="">Todas as Visões</option>
          <option value="PROSPECT">Oportunidades</option>
          <option value="CLIENTE_ATIVO">Clientes Ativos</option>
          <option value="INATIVO">Ex-clientes</option>
          <option value="UPGRADE">Clientes com Upgrade</option>
        </select>
      </div>
    </div>

    <!-- Lista de Contas -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="space-y-3">
      <div class="flex items-center justify-between">
        <div class="text-xs font-bold uppercase tracking-widest text-gray-500">
          {{ totalCount }} conta(s) encontrada(s) · Página {{ currentPage }} de {{ totalPages }}
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500">Por página:</label>
          <select v-model.number="pageSize" @change="resetAndLoad" class="input !w-20 !py-1 text-xs">
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
      </div>

      <div class="card p-0 overflow-hidden">
        <div class="overflow-auto">
          <table class="min-w-[1200px] w-full divide-y divide-gray-100">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-gray-500">Empresa</th>
                <th class="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-gray-500">Marca(s)</th>
                <th class="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-gray-500">Contato</th>
                <th class="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-gray-500">Local/Setor</th>
                <th class="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-gray-500">Canal/Proprietário</th>
                <th class="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-gray-500">Relacionamentos</th>
                <th class="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-gray-500">Criada em</th>
                <th class="px-4 py-3 text-right text-[10px] font-black uppercase tracking-widest text-gray-500">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 bg-white">
              <tr v-for="conta in contas" :key="conta.id" class="hover:bg-gray-50/80 transition-colors">
                <td class="px-4 py-3 align-top">
                  <p class="font-bold text-gray-900">{{ conta.nome_empresa }}</p>
                  <div class="flex items-center gap-2 mt-0.5">
                    <p class="text-xs text-gray-500">CNPJ: {{ conta.cnpj || 'Não informado' }}</p>
                    <span
                      class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wide"
                      :class="statusBadgeClass(conta.status_cliente)"
                    >
                      {{ conta.status_cliente_display || statusLabel(conta.status_cliente) }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3 align-top text-sm text-gray-700">
                  {{ formatMarcas(conta) }}
                </td>
                <td class="px-4 py-3 align-top text-sm text-gray-700">
                  <p>{{ conta.telefone_principal || '-' }}</p>
                  <p class="text-xs text-gray-500">{{ conta.email || 'Sem e-mail' }}</p>
                </td>
                <td class="px-4 py-3 align-top text-sm text-gray-700">
                  <p>{{ conta.cidade || '-' }}<span v-if="conta.estado">/{{ conta.estado }}</span></p>
                  <p class="text-xs text-gray-500">{{ conta.setor || 'Setor não informado' }}</p>
                </td>
                <td class="px-4 py-3 align-top text-sm text-gray-700">
                  <p>{{ conta.canal_nome || '-' }}</p>
                  <p class="text-xs text-gray-500">{{ conta.proprietario_nome || '-' }}</p>
                </td>
                <td class="px-4 py-3 align-top">
                  <div class="flex items-center gap-2 text-xs font-black uppercase tracking-wide">
                    <span class="px-2 py-1 rounded-full bg-blue-50 text-blue-700">{{ conta.total_contatos || 0 }} contatos</span>
                    <span class="px-2 py-1 rounded-full bg-emerald-50 text-emerald-700">{{ conta.total_oportunidades || 0 }} oportunidades</span>
                  </div>
                </td>
                <td class="px-4 py-3 align-top text-sm text-gray-600">
                  {{ formatDate(conta.data_criacao) }}
                </td>
                <td class="px-4 py-3 align-top text-right">
                  <button class="btn btn-white" @click="viewConta(conta.id)">
                    Abrir
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Paginação -->
      <div v-if="totalPages > 1" class="flex items-center justify-between pt-2">
        <button
          class="btn btn-white text-sm"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          ← Anterior
        </button>

        <div class="flex items-center gap-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="min-w-[36px] h-9 rounded-lg text-sm font-semibold transition-colors"
            :class="page === currentPage
              ? 'bg-primary-600 text-white shadow-sm'
              : page === '...'
                ? 'cursor-default text-gray-400'
                : 'text-gray-600 hover:bg-gray-100'"
            :disabled="page === '...'"
            @click="page !== '...' && goToPage(page)"
          >
            {{ page }}
          </button>
        </div>

        <button
          class="btn btn-white text-sm"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Próxima →
        </button>
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

    <!-- Modal: Atualização em Lote de Endereços -->
    <CnpjBatchModal
      :show="showBatchModal"
      @close="showBatchModal = false"
      @saved="loadContas"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import ContaModal from '@/components/ContaModal.vue'
import CnpjBatchModal from '@/components/CnpjBatchModal.vue'

const router = useRouter()
const contas = ref([])
const canais = ref([])
const loading = ref(false)
const showModal = ref(false)
const showBatchModal = ref(false)
const selectedConta = ref(null)
const searchQuery = ref('')
const selectedCanal = ref(null)
const selectedVisaoComercial = ref('')

const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

let searchTimeout = null

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const pages = []
  pages.push(1)

  if (current > 3) pages.push('...')

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) pages.push(i)

  if (current < total - 2) pages.push('...')

  pages.push(total)
  return pages
})

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

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadContas()
  }, 300)
}

function resetAndLoad() {
  currentPage.value = 1
  loadContas()
}

async function loadContas() {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (selectedCanal.value) {
      params.canal = selectedCanal.value
    }
    if (selectedVisaoComercial.value === 'UPGRADE') {
      params.apenas_upgrade = true
    } else if (selectedVisaoComercial.value) {
      params.status_cliente = selectedVisaoComercial.value
    }
    const response = await api.get('/contas/', { params })
    contas.value = response.data.results || response.data
    totalCount.value = response.data.count ?? contas.value.length
  } catch (error) {
    console.error('Erro ao carregar contas:', error)
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadContas()
  window.scrollTo({ top: 0, behavior: 'smooth' })
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

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleDateString('pt-BR')
}

function formatMarcas(conta) {
  const marcas = conta.marcas_adicionais || []
  if (!marcas.length) return conta.marca || '-'
  const nomes = marcas.map((m) => m.nome).filter(Boolean)
  if (conta.marca) nomes.unshift(conta.marca)
  return [...new Set(nomes)].join(', ') || '-'
}

function statusLabel(status) {
  if (status === 'CLIENTE_ATIVO') return 'Cliente Ativo'
  if (status === 'INATIVO') return 'Ex-cliente'
  return 'Oportunidade'
}

function statusBadgeClass(status) {
  if (status === 'CLIENTE_ATIVO') return 'bg-emerald-100 text-emerald-700'
  if (status === 'INATIVO') return 'bg-gray-200 text-gray-700'
  return 'bg-blue-100 text-blue-700'
}
</script>
