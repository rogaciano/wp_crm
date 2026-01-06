<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Contatos</h1>
      <button @click="openModal()" class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Contato</button>
    </div>

    <!-- Cards de Estatísticas/Filtros por Tipo -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
      <!-- Card Total -->
      <div
        @click="filterByTipo(undefined)"
        :class="['card cursor-pointer transition-all duration-200 hover:shadow-lg border-2', selectedTipo === undefined && selectedCanal === undefined ? 'border-primary-500 bg-primary-50' : 'border-transparent hover:border-gray-300']"
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
        :class="['card cursor-pointer transition-all duration-200 hover:shadow-lg border-2', selectedTipo === tipo.id ? 'border-teal-500 bg-teal-50' : 'border-transparent hover:border-gray-300']"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">{{ tipo.nome }}</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">{{ tipo.total }}</p>
          </div>
          <div
            :class="['h-12 w-12 rounded-lg flex items-center justify-center text-3xl', getTipoColor(index)]"
          >
            {{ tipo.emoji || '👤' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Cards de Estatísticas/Filtros por Canal -->
    <div v-if="stats.por_canal && stats.por_canal.length > 0" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-3">
      <div
        v-for="(canal, index) in stats.por_canal"
        :key="canal.id || 'sem-canal'"
        @click="filterByCanal(canal.id)"
        :class="['card cursor-pointer transition-all duration-200 hover:shadow-lg border-2 py-3', selectedCanal === canal.id ? 'border-amber-500 bg-amber-50' : 'border-transparent hover:border-gray-300']"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <p class="text-xs font-medium text-gray-500 truncate">{{ canal.nome }}</p>
            <p class="text-2xl font-bold text-gray-900 mt-0.5">{{ canal.total }}</p>
          </div>
          <div :class="['h-10 w-10 rounded-lg flex items-center justify-center text-xl', getCanalColor(index)]">
            🏢
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros Ativos -->
    <div v-if="selectedTipo !== undefined || selectedCanal !== undefined" class="flex items-center gap-2 flex-wrap">
      <span class="text-sm text-gray-500">Filtros:</span>
      <span v-if="selectedTipo !== undefined" class="inline-flex items-center gap-1 px-2 py-1 bg-teal-100 text-teal-700 rounded-full text-sm">
        {{ getSelectedTipoName() }}
        <button @click="filterByTipo(undefined)" class="ml-1 hover:text-teal-900">&times;</button>
      </span>
      <span v-if="selectedCanal !== undefined" class="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-sm">
        🏢 {{ getSelectedCanalName() }}
        <button @click="filterByCanal(undefined)" class="ml-1 hover:text-amber-900">&times;</button>
      </span>
      <button 
        v-if="selectedTipo !== undefined || selectedCanal !== undefined"
        @click="clearFilters()"
        class="text-xs text-gray-500 hover:text-gray-700 underline"
      >
        Limpar filtros
      </button>
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
        <div class="hidden md:block">
          <table class="table table-fixed w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header w-36">Nome</th>
                <th class="table-header w-44">Email</th>
                <th class="table-header w-28">Telefone</th>
                <th class="table-header w-32">Cargo</th>
                <th class="table-header w-28">Tipo</th>
                <th class="table-header w-28">Canal</th>
                <th class="table-header w-40">Empresa</th>
                <th class="table-header text-right w-24">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="contato in contatos" :key="contato.id" class="hover:bg-gray-50">
                <td class="table-cell">
                  <div class="font-medium text-gray-900 break-words">{{ contato.nome }}</div>
                  <div v-if="contato.criado_por_nome" class="text-xs text-gray-500 mt-1">
                    {{ contato.criado_por_nome }} • {{ formatShortDate(contato.data_criacao) }}
                  </div>
                </td>
                <td class="table-cell text-gray-500">
                  <a
                    v-if="contato.email"
                    :href="`mailto:${contato.email}`"
                    :title="contato.email"
                    class="text-primary-600 hover:text-primary-700 hover:underline block truncate max-w-full"
                  >
                    {{ contato.email }}
                  </a>
                  <span v-else class="text-gray-400 text-xs">Sem email</span>
                </td>
                <td class="table-cell text-gray-500 whitespace-nowrap">{{ contato.telefone_formatado || contato.telefone }}</td>
                <td class="table-cell text-gray-500 break-words">{{ contato.cargo }}</td>
                <td class="table-cell text-gray-500">
                  <span v-if="contato.tipo_contato_nome" class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 break-words">
                    <span class="flex-shrink-0">{{ contato.tipo_contato_emoji || '👤' }}</span>
                    <span class="break-words">{{ contato.tipo_contato_nome }}</span>
                  </span>
                  <span v-else class="text-gray-400 text-xs inline-flex items-center gap-1">
                    <span>👤</span>
                    Sem tipo
                  </span>
                </td>
                <td class="table-cell text-gray-500 break-words">
                  <span v-if="contato.canal_nome" class="text-sm">
                    {{ contato.canal_nome }}
                  </span>
                  <span v-else class="text-gray-400 text-xs">Sem canal</span>
                </td>
                <td class="table-cell text-gray-500 font-medium break-words">
                  <span v-if="contato.conta_nome">
                    {{ contato.conta_nome }}
                  </span>
                  <span v-else class="text-gray-400 text-xs">Sem empresa</span>
                </td>
                <td class="table-cell text-right whitespace-nowrap">
                  <div class="flex justify-end space-x-3">
                    <button @click="openModal(contato)" class="text-primary-600 hover:text-primary-700 font-medium" title="Editar">
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button @click="deleteContato(contato.id)" class="text-red-600 hover:text-red-700 font-medium" title="Excluir">
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
          <div v-for="contato in contatos" :key="contato.id" class="p-4 active:bg-gray-50 transition-colors">
            <div class="mb-3">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900">{{ contato.nome }}</h3>
                  <p v-if="contato.criado_por_nome" class="text-xs text-gray-500 mt-1">
                    {{ contato.criado_por_nome }} • {{ formatShortDate(contato.data_criacao) }}
                  </p>
                </div>
                <span v-if="contato.tipo_contato_nome" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                  <span>{{ contato.tipo_contato_emoji || '👤' }}</span>
                  {{ contato.tipo_contato_nome }}
                </span>
              </div>
              <p class="text-sm text-primary-600 font-medium mt-1">{{ contato.cargo || 'Contato' }}</p>
              <div class="flex items-center gap-2 mt-1">
                <p class="text-xs text-gray-500">Empresa: {{ contato.conta_nome || 'N/A' }}</p>
                <span v-if="contato.canal_nome" class="text-xs text-gray-400">• Canal: {{ contato.canal_nome }}</span>
              </div>
            </div>

            <div class="space-y-1.5 mb-4">
              <div v-if="contato.email" class="flex items-center text-xs">
                <svg class="w-3.5 h-3.5 mr-1.5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                <a
                  :href="`mailto:${contato.email}`"
                  :title="contato.email"
                  class="text-primary-600 hover:text-primary-700 hover:underline truncate"
                >
                  {{ contato.email }}
                </a>
              </div>
              <div v-if="contato.telefone || contato.telefone_formatado" class="flex items-center text-xs text-gray-500">
                <svg class="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                {{ contato.telefone_formatado || contato.telefone }}
              </div>
              <div v-if="contato.celular || contato.celular_formatado" class="flex items-center text-xs text-gray-500">
                <svg class="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                {{ contato.celular_formatado || contato.celular }}
              </div>
            </div>

            <div class="flex justify-end space-x-6 border-t pt-3 mt-2">
              <button @click="openModal(contato)" class="text-xs font-bold text-primary-600 uppercase tracking-widest flex items-center">
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                 Editar
              </button>
              <button @click="deleteContato(contato.id)" class="text-xs font-bold text-red-600 uppercase tracking-widest flex items-center">
                 <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                 Excluir
              </button>
            </div>
          </div>
        </div>

        <div v-if="contatos.length === 0" class="text-center py-12 text-gray-500">
          Nenhum contato encontrado.
        </div>
      </div>

      <!-- Paginação -->
      <div v-if="pagination.count > 0" class="border-t border-gray-200 px-4 py-3 sm:px-6">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <!-- Informações da página -->
          <div class="text-sm text-gray-700">
            Mostrando <span class="font-medium">{{ (pagination.currentPage - 1) * pagination.pageSize + 1 }}</span>
            a <span class="font-medium">{{ Math.min(pagination.currentPage * pagination.pageSize, pagination.count) }}</span>
            de <span class="font-medium">{{ pagination.count }}</span> contatos
          </div>

          <!-- Controles de navegação -->
          <div class="flex items-center space-x-2">
            <!-- Botão Primeira Página -->
            <button
              @click="goToPage(1)"
              :disabled="pagination.currentPage === 1"
              :class="['px-3 py-2 rounded-md text-sm font-medium transition-colors',
                       pagination.currentPage === 1
                         ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                         : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>

            <!-- Botão Página Anterior -->
            <button
              @click="goToPage(pagination.currentPage - 1)"
              :disabled="!pagination.previous"
              :class="['px-3 py-2 rounded-md text-sm font-medium transition-colors',
                       !pagination.previous
                         ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                         : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <!-- Números das páginas -->
            <div class="hidden sm:flex space-x-1">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="['px-3 py-2 rounded-md text-sm font-medium transition-colors',
                         page === pagination.currentPage
                           ? 'bg-primary-600 text-white'
                           : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300']"
              >
                {{ page }}
              </button>
            </div>

            <!-- Indicador de página atual (mobile) -->
            <div class="sm:hidden px-3 py-2 text-sm font-medium text-gray-700">
              {{ pagination.currentPage }} / {{ pagination.totalPages }}
            </div>

            <!-- Botão Próxima Página -->
            <button
              @click="goToPage(pagination.currentPage + 1)"
              :disabled="!pagination.next"
              :class="['px-3 py-2 rounded-md text-sm font-medium transition-colors',
                       !pagination.next
                         ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                         : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <!-- Botão Última Página -->
            <button
              @click="goToPage(pagination.totalPages)"
              :disabled="pagination.currentPage === pagination.totalPages"
              :class="['px-3 py-2 rounded-md text-sm font-medium transition-colors',
                       pagination.currentPage === pagination.totalPages
                         ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                         : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <ContatoModal
      :show="showModal"
      :contato="selectedContato"
      @close="showModal = false"
      @saved="handleContatoSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import ContatoModal from '@/components/ContatoModal.vue'

const contatos = ref([])
const searchQuery = ref('')
const showModal = ref(false)
const selectedContato = ref(null)
const loading = ref(false)
const stats = ref({ total: 0, por_tipo: [], por_canal: [] })
const selectedTipo = ref(undefined) // undefined = sem filtro, null = sem tipo, número = tipo específico
const selectedCanal = ref(undefined) // undefined = sem filtro, null = sem canal, número = canal específico

// Estado de paginação
const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 10,
  totalPages: 0
})

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

// Cores para os cards de canais (gradientes âmbar)
const canalColors = [
  'bg-gradient-to-br from-amber-400 to-amber-500',
  'bg-gradient-to-br from-orange-400 to-orange-500',
  'bg-gradient-to-br from-yellow-400 to-yellow-500',
  'bg-gradient-to-br from-lime-400 to-lime-500',
  'bg-gradient-to-br from-emerald-400 to-emerald-500',
  'bg-gradient-to-br from-cyan-400 to-cyan-500',
]

// Computed para páginas visíveis (mostra até 5 páginas por vez)
const visiblePages = computed(() => {
  const total = pagination.value.totalPages
  const current = pagination.value.currentPage
  const pages = []

  if (total <= 5) {
    // Se tem 5 ou menos páginas, mostra todas
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Mostra 5 páginas centradas na atual
    let start = Math.max(1, current - 2)
    let end = Math.min(total, start + 4)

    // Ajusta se chegou no final
    if (end === total) {
      start = Math.max(1, end - 4)
    }

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }

  return pages
})

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

async function loadContatos(page = 1) {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      page: page,
      page_size: pagination.value.pageSize
    }

    // Adiciona filtro por tipo se selecionado
    // Se selectedTipo for undefined, não filtra (mostra todos)
    // Se for 'null' (string), filtra por contatos sem tipo
    // Se for um número, filtra por aquele tipo específico
    if (selectedTipo.value !== undefined) {
      params.tipo_contato = selectedTipo.value === 'null' ? '' : selectedTipo.value
    }

    // Adiciona filtro por canal se selecionado
    if (selectedCanal.value !== undefined) {
      params.canal = selectedCanal.value === 'null' ? '' : selectedCanal.value
    }

    const response = await api.get('/contatos/', { params })

    // Se a resposta tem paginação (results, count, next, previous)
    if (response.data.results) {
      contatos.value = response.data.results
      pagination.value.count = response.data.count
      pagination.value.next = response.data.next
      pagination.value.previous = response.data.previous
      pagination.value.currentPage = page
      pagination.value.totalPages = Math.ceil(response.data.count / pagination.value.pageSize)
    } else {
      // Fallback se não houver paginação
      contatos.value = response.data
      pagination.value.count = response.data.length
      pagination.value.totalPages = 1
      pagination.value.currentPage = 1
    }
  } catch (error) {
    console.error('Erro ao carregar contatos:', error)
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= pagination.value.totalPages) {
    loadContatos(page)
    // Scroll suave para o topo da lista
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function getTipoColor(index) {
  return tipoColors[index % tipoColors.length]
}

function formatShortDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const options = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }
  return date.toLocaleDateString('pt-BR', options)
}

function filterByTipo(tipoId) {
  selectedTipo.value = tipoId
  pagination.value.currentPage = 1 // Resetar para página 1 ao filtrar
  loadContatos(1)
}

function filterByCanal(canalId) {
  selectedCanal.value = canalId
  pagination.value.currentPage = 1 // Resetar para página 1 ao filtrar
  loadContatos(1)
}

function clearFilters() {
  selectedTipo.value = undefined
  selectedCanal.value = undefined
  pagination.value.currentPage = 1
  loadContatos(1)
}

function getCanalColor(index) {
  return canalColors[index % canalColors.length]
}

function getSelectedTipoName() {
  if (selectedTipo.value === undefined) return ''
  if (selectedTipo.value === 'null') return '👤 Sem Tipo'
  const tipo = stats.value.por_tipo.find(t => t.id === selectedTipo.value)
  return tipo ? `${tipo.emoji || '👤'} ${tipo.nome}` : ''
}

function getSelectedCanalName() {
  if (selectedCanal.value === undefined) return ''
  if (selectedCanal.value === 'null') return 'Sem Canal'
  const canal = stats.value.por_canal.find(c => c.id === selectedCanal.value)
  return canal ? canal.nome : ''
}

function openModal(contato = null) {
  selectedContato.value = contato
  showModal.value = true
}

function handleContatoSaved() {
  // Recarrega a página atual e as estatísticas
  loadContatos(pagination.value.currentPage)
  loadEstatisticas()
}

async function deleteContato(id) {
  if (!confirm('Tem certeza que deseja excluir este contato?')) return

  try {
    await api.delete(`/contatos/${id}/`)

    // Se era o último item da página e não é a primeira página, volta uma página
    if (contatos.value.length === 1 && pagination.value.currentPage > 1) {
      loadContatos(pagination.value.currentPage - 1)
    } else {
      loadContatos(pagination.value.currentPage)
    }

    loadEstatisticas()
  } catch (error) {
    console.error('Erro ao excluir contato:', error)
    alert('Erro ao excluir contato')
  }
}
</script>
