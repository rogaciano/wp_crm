<template>
  <div class="p-6">
    <!-- Cabeçalho -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Logs de Auditoria</h1>
      <p class="text-sm text-gray-600 mt-1">Histórico de ações realizadas no sistema</p>
    </div>

    <!-- Filtros -->
    <div class="bg-white rounded-lg shadow-sm p-4 mb-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ação</label>
          <select v-model="filtros.acao" @change="aplicarFiltros" class="input">
            <option value="">Todas as ações</option>
            <option value="CREATE">Criação</option>
            <option value="UPDATE">Atualização</option>
            <option value="DELETE">Exclusão</option>
            <option value="VIEW">Visualização</option>
            <option value="LOGIN">Login</option>
            <option value="LOGOUT">Logout</option>
            <option value="EXPORT">Exportação</option>
            <option value="IMPORT">Importação</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Modelo</label>
          <select v-model="filtros.modelo" @change="aplicarFiltros" class="input">
            <option value="">Todos os modelos</option>
            <option value="Lead">Lead</option>
            <option value="Conta">Conta</option>
            <option value="Contato">Contato</option>
            <option value="Oportunidade">Oportunidade</option>
            <option value="Atividade">Atividade</option>
            <option value="User">Usuário</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input
            v-model="filtros.search"
            @input="debounceSearch"
            type="text"
            placeholder="Buscar em logs..."
            class="input"
          />
        </div>

        <div class="flex items-end">
          <button @click="limparFiltros" class="btn-secondary w-full">
            Limpar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Tabela de Logs -->
    <div v-else class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="table-header w-40">Data/Hora</th>
              <th class="table-header w-32">Usuário</th>
              <th class="table-header w-24">Ação</th>
              <th class="table-header w-28">Modelo</th>
              <th class="table-header w-48">Objeto</th>
              <th class="table-header w-32">IP</th>
              <th class="table-header text-right w-24">Detalhes</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="logs.length === 0">
              <td colspan="7" class="text-center py-8 text-gray-500">
                Nenhum log encontrado
              </td>
            </tr>
            <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
              <td class="table-cell">
                <div class="text-sm text-gray-900">{{ formatDate(log.timestamp) }}</div>
                <div class="text-xs text-gray-500">{{ formatTime(log.timestamp) }}</div>
              </td>
              <td class="table-cell">
                <span class="text-sm text-gray-900">{{ log.usuario_nome || 'Sistema' }}</span>
              </td>
              <td class="table-cell">
                <span :class="getAcaoBadgeClass(log.acao)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ log.acao_display }}
                </span>
              </td>
              <td class="table-cell">
                <span class="text-sm text-gray-700 font-medium">{{ log.modelo }}</span>
              </td>
              <td class="table-cell">
                <div class="text-sm text-gray-900 truncate max-w-xs">
                  <span v-if="log.objeto_id" class="text-gray-500 text-xs">#{{ log.objeto_id }}</span>
                  {{ log.objeto_repr }}
                </div>
              </td>
              <td class="table-cell">
                <span class="text-xs text-gray-600">{{ log.ip_address || '-' }}</span>
              </td>
              <td class="table-cell text-right">
                <button
                  @click="verDetalhes(log)"
                  class="text-blue-600 hover:text-blue-900 text-sm font-medium"
                >
                  Ver
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginação -->
      <div v-if="totalPages > 1" class="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="paginaAnterior"
            :disabled="paginaAtual === 1"
            class="btn-secondary"
          >
            Anterior
          </button>
          <button
            @click="proximaPagina"
            :disabled="paginaAtual === totalPages"
            class="btn-secondary ml-3"
          >
            Próxima
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Mostrando <span class="font-medium">{{ (paginaAtual - 1) * 20 + 1 }}</span> até
              <span class="font-medium">{{ Math.min(paginaAtual * 20, total) }}</span> de
              <span class="font-medium">{{ total }}</span> registros
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
              <button
                @click="paginaAnterior"
                :disabled="paginaAtual === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                @click="proximaPagina"
                :disabled="paginaAtual === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                Próxima
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Detalhes -->
    <div v-if="showModal" @click.self="fecharModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 class="text-lg font-semibold text-gray-900">Detalhes do Log</h3>
          <button @click="fecharModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="px-6 py-4 overflow-y-auto max-h-[calc(90vh-8rem)]">
          <div v-if="logSelecionado" class="space-y-4">
            <!-- Informações Básicas -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Data/Hora</label>
                <p class="text-sm text-gray-900">{{ formatDateTime(logSelecionado.timestamp) }}</p>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Usuário</label>
                <p class="text-sm text-gray-900">{{ logSelecionado.usuario_nome || 'Sistema' }}</p>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Ação</label>
                <p class="text-sm text-gray-900">{{ logSelecionado.acao_display }}</p>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Modelo</label>
                <p class="text-sm text-gray-900">{{ logSelecionado.modelo }}</p>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">Objeto ID</label>
                <p class="text-sm text-gray-900">#{{ logSelecionado.objeto_id || 'N/A' }}</p>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 mb-1">IP</label>
                <p class="text-sm text-gray-900">{{ logSelecionado.ip_address || '-' }}</p>
              </div>
            </div>

            <!-- Objeto -->
            <div v-if="logSelecionado.objeto_repr">
              <label class="block text-xs font-medium text-gray-500 mb-1">Objeto</label>
              <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded">{{ logSelecionado.objeto_repr }}</p>
            </div>

            <!-- Alterações -->
            <div v-if="logSelecionado.alteracoes && Object.keys(logSelecionado.alteracoes).length > 0">
              <label class="block text-xs font-medium text-gray-500 mb-2">Alterações</label>
              <div class="bg-gray-50 p-3 rounded space-y-2">
                <div v-for="(alteracao, campo) in logSelecionado.alteracoes" :key="campo" class="border-b border-gray-200 pb-2 last:border-0">
                  <p class="text-xs font-semibold text-gray-700 mb-1">{{ campo }}</p>
                  <div class="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span class="text-gray-500">Antes:</span>
                      <span class="text-red-600 ml-1">{{ alteracao.antes || '(vazio)' }}</span>
                    </div>
                    <div>
                      <span class="text-gray-500">Depois:</span>
                      <span class="text-green-600 ml-1">{{ alteracao.depois || '(vazio)' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Observação -->
            <div v-if="logSelecionado.observacao">
              <label class="block text-xs font-medium text-gray-500 mb-1">Observação</label>
              <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded">{{ logSelecionado.observacao }}</p>
            </div>

            <!-- User Agent -->
            <div v-if="logSelecionado.user_agent">
              <label class="block text-xs font-medium text-gray-500 mb-1">Navegador/Dispositivo</label>
              <p class="text-xs text-gray-600 bg-gray-50 p-3 rounded break-all">{{ logSelecionado.user_agent }}</p>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button @click="fecharModal" class="btn-secondary">Fechar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const logs = ref([])
const loading = ref(false)
const paginaAtual = ref(1)
const totalPages = ref(1)
const total = ref(0)
const showModal = ref(false)
const logSelecionado = ref(null)

const filtros = ref({
  acao: '',
  modelo: '',
  search: ''
})

let searchTimeout = null

onMounted(() => {
  carregarLogs()
})

async function carregarLogs() {
  loading.value = true
  try {
    const params = {
      page: paginaAtual.value
    }

    if (filtros.value.acao) params.acao = filtros.value.acao
    if (filtros.value.modelo) params.modelo = filtros.value.modelo
    if (filtros.value.search) params.search = filtros.value.search

    const response = await api.get('/api/crm/logs/', { params })
    logs.value = response.data.results
    total.value = response.data.count
    totalPages.value = Math.ceil(response.data.count / 20)
  } catch (error) {
    console.error('Erro ao carregar logs:', error)
  } finally {
    loading.value = false
  }
}

function aplicarFiltros() {
  paginaAtual.value = 1
  carregarLogs()
}

function debounceSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    aplicarFiltros()
  }, 500)
}

function limparFiltros() {
  filtros.value = {
    acao: '',
    modelo: '',
    search: ''
  }
  paginaAtual.value = 1
  carregarLogs()
}

function paginaAnterior() {
  if (paginaAtual.value > 1) {
    paginaAtual.value--
    carregarLogs()
  }
}

function proximaPagina() {
  if (paginaAtual.value < totalPages.value) {
    paginaAtual.value++
    carregarLogs()
  }
}

function verDetalhes(log) {
  logSelecionado.value = log
  showModal.value = true
}

function fecharModal() {
  showModal.value = false
  logSelecionado.value = null
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR')
}

function formatTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

function formatDateTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getAcaoBadgeClass(acao) {
  const classes = {
    'CREATE': 'bg-green-100 text-green-800',
    'UPDATE': 'bg-blue-100 text-blue-800',
    'DELETE': 'bg-red-100 text-red-800',
    'VIEW': 'bg-gray-100 text-gray-800',
    'LOGIN': 'bg-purple-100 text-purple-800',
    'LOGOUT': 'bg-gray-100 text-gray-800',
    'EXPORT': 'bg-yellow-100 text-yellow-800',
    'IMPORT': 'bg-indigo-100 text-indigo-800'
  }
  return classes[acao] || 'bg-gray-100 text-gray-800'
}
</script>
