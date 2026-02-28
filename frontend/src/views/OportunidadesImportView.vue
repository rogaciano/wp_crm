<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Importar Oportunidades</h1>
        <p class="text-sm text-gray-500 mt-1">Upload de planilha XLSX para criar Empresa, Contato e Oportunidade.</p>
      </div>
      <button class="btn btn-white" @click="router.push('/oportunidades')">
        Voltar para Oportunidades
      </button>
    </div>

    <div class="flex items-center gap-2">
      <button
        class="tab-btn"
        :class="{ 'tab-btn-active': activeTab === 'importar' }"
        @click="activeTab = 'importar'"
      >
        Importar
      </button>
      <button
        class="tab-btn"
        :class="{ 'tab-btn-active': activeTab === 'lotes' }"
        @click="activeTab = 'lotes'"
      >
        Lotes importados
      </button>
    </div>

    <div v-if="activeTab === 'importar'" class="card space-y-5">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">Arquivo (.xlsx)</label>
          <input
            ref="fileInput"
            type="file"
            accept=".xlsx"
            class="input"
            @change="onFileChange"
          />
          <p v-if="selectedFile" class="text-xs text-gray-500 mt-1">
            {{ selectedFile.name }}
          </p>
        </div>

        <div>
          <label class="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">Canal</label>
          <select v-model="selectedCanal" class="input">
            <option value="">Selecionar canal...</option>
            <option v-for="canal in canais" :key="canal.id" :value="String(canal.id)">
              {{ canal.nome }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">Tipo de importação</label>
          <select v-model="modoImportacao" class="input">
            <option value="VENDAS">Funil de Vendas</option>
            <option v-if="authStore.isAdmin" value="CLIENTE_LEGADO">Clientes legados (Pós-Venda + Suporte)</option>
          </select>
          <p v-if="modoImportacao === 'CLIENTE_LEGADO'" class="text-[11px] text-gray-500 mt-1">
            Cria oportunidades diretamente em Pós-Venda e Suporte, sem venda retroativa.
          </p>
        </div>
      </div>

      <div class="flex flex-col md:flex-row md:items-center gap-3 justify-between border-t border-gray-100 pt-4">
        <label class="inline-flex items-center gap-2 text-sm text-gray-700">
          <input v-model="dryRun" type="checkbox" class="rounded border-gray-300" />
          Simulação (dry-run, não grava no banco)
        </label>

        <div class="flex gap-2">
          <button class="btn btn-white" :disabled="importLoading" @click="clearForm">
            Limpar
          </button>
          <button class="btn btn-primary" :disabled="importLoading || !selectedFile" @click="importar">
            {{ importLoading ? 'Importando...' : 'Importar Planilha' }}
          </button>
        </div>
      </div>

      <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
        {{ errorMessage }}
      </div>

      <div v-if="result" class="space-y-4">
        <div class="rounded-xl bg-gray-50 border border-gray-100 p-4">
          <div class="flex flex-wrap items-center gap-2 mb-3">
            <span class="text-[10px] font-black uppercase tracking-widest text-gray-500">Modo:</span>
            <span
              class="px-2 py-1 rounded-full text-[10px] font-black uppercase"
              :class="result.modo_importacao === 'CLIENTE_LEGADO' ? 'bg-indigo-100 text-indigo-700' : 'bg-blue-100 text-blue-700'"
            >
              {{ result.modo_importacao === 'CLIENTE_LEGADO' ? 'Clientes legados' : 'Vendas' }}
            </span>

            <template v-if="result.destinos && result.destinos.length">
              <span class="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-2">Destinos:</span>
              <span
                v-for="destino in result.destinos"
                :key="destino.tipo || destino.funil?.id"
                class="px-2 py-1 rounded-full text-[10px] font-black uppercase bg-emerald-100 text-emerald-700"
              >
                {{ destino.funil?.nome || destino.tipo }}
              </span>
            </template>
          </div>

          <p class="text-xs font-black uppercase tracking-widest text-gray-500 mb-3">Resumo</p>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
            <div class="bg-white rounded-lg border border-gray-100 p-3">
              <p class="text-gray-500 text-xs uppercase">Processadas</p>
              <p class="font-black text-gray-900">{{ result.summary.processadas }}</p>
            </div>
            <div class="bg-white rounded-lg border border-gray-100 p-3">
              <p class="text-gray-500 text-xs uppercase">Criadas</p>
              <p class="font-black text-emerald-600">{{ result.summary.criadas }}</p>
            </div>
            <div class="bg-white rounded-lg border border-gray-100 p-3">
              <p class="text-gray-500 text-xs uppercase">Atualizadas</p>
              <p class="font-black text-blue-600">{{ result.summary.atualizadas }}</p>
            </div>
            <div class="bg-white rounded-lg border border-gray-100 p-3">
              <p class="text-gray-500 text-xs uppercase">Erros</p>
              <p class="font-black text-red-600">{{ result.summary.erros }}</p>
            </div>
            <div class="bg-white rounded-lg border border-gray-100 p-3">
              <p class="text-gray-500 text-xs uppercase">Origens novas</p>
              <p class="font-black text-indigo-600">{{ result.summary.origens_criadas }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-xl border border-gray-100 overflow-hidden">
          <div class="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
            <p class="text-xs font-black uppercase tracking-widest text-gray-500">Detalhes por linha</p>
            <p class="text-xs text-gray-500">Mostrando até 200 linhas</p>
          </div>
          <div class="max-h-[420px] overflow-auto">
            <table class="table min-w-full">
              <thead>
                <tr>
                  <th class="table-header">Linha</th>
                  <th class="table-header">Status</th>
                  <th class="table-header">Mensagem</th>
                  <th class="table-header">Oportunidade</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in result.rows" :key="`${item.linha}-${item.status}-${item.oportunidade_nome || ''}`">
                  <td class="table-cell text-gray-600">{{ item.linha }}</td>
                  <td class="table-cell">
                    <span
                      class="px-2 py-1 rounded-full text-[10px] font-black uppercase"
                      :class="statusClass(item.status)"
                    >
                      {{ item.status }}
                    </span>
                  </td>
                  <td class="table-cell text-gray-700">{{ item.mensagem }}</td>
                  <td class="table-cell text-gray-600">{{ item.oportunidade_nome || '-' }}</td>
                </tr>
                <tr v-if="!result.rows || result.rows.length === 0">
                  <td class="table-cell text-center text-gray-400" colspan="4">Sem linhas para exibir.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card space-y-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-2">
        <div>
          <p class="text-xs font-black uppercase tracking-widest text-gray-500">Histórico</p>
          <h2 class="text-lg font-black text-gray-900">Lotes importados</h2>
        </div>
        <button class="btn btn-white" :disabled="lotesLoading" @click="loadLotes">
          {{ lotesLoading ? 'Atualizando...' : 'Atualizar lista' }}
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">Buscar arquivo</label>
          <input
            v-model="loteSearch"
            type="text"
            class="input"
            placeholder="Ex: mailing-fevereiro.xlsx"
          />
        </div>
        <div>
          <label class="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">Status</label>
          <select v-model="loteStatusFilter" class="input">
            <option value="todos">Todos</option>
            <option value="ativos">Ativos</option>
            <option value="revertidos">Revertidos</option>
          </select>
        </div>
      </div>

      <div v-if="lotesError" class="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
        {{ lotesError }}
      </div>

      <div v-if="successMessage" class="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-700">
        {{ successMessage }}
      </div>

      <div class="rounded-xl border border-gray-100 overflow-hidden">
        <div class="max-h-[520px] overflow-auto">
          <table class="table min-w-full">
            <thead>
              <tr>
                <th class="table-header">Lote</th>
                <th class="table-header">Arquivo</th>
                <th class="table-header">Resumo</th>
                <th class="table-header">Criado em</th>
                <th class="table-header">Status</th>
                <th class="table-header">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lote in filteredLotes" :key="lote.lote_id">
                <td class="table-cell text-gray-700 font-bold">#{{ lote.lote_id }}</td>
                <td class="table-cell text-gray-700">{{ lote.arquivo || '-' }}</td>
                <td class="table-cell text-xs text-gray-600">
                  <div class="space-y-1">
                    <p>Oportunidades: <span class="font-black">{{ lote.created_counts?.oportunidades || 0 }}</span></p>
                    <p>Contas: <span class="font-black">{{ lote.created_counts?.contas || 0 }}</span> · Contatos: <span class="font-black">{{ lote.created_counts?.contatos || 0 }}</span></p>
                  </div>
                </td>
                <td class="table-cell text-gray-600">{{ formatDate(lote.criado_em) }}</td>
                <td class="table-cell">
                  <span
                    class="px-2 py-1 rounded-full text-[10px] font-black uppercase"
                    :class="lote.revertido ? 'bg-gray-200 text-gray-700' : 'bg-emerald-100 text-emerald-700'"
                  >
                    {{ lote.revertido ? 'revertido' : 'ativo' }}
                  </span>
                </td>
                <td class="table-cell">
                  <button
                    class="btn btn-danger"
                    :disabled="lote.revertido || revertLoading"
                    @click="openReverterModal(lote)"
                  >
                    Reverter lote
                  </button>
                </td>
              </tr>
              <tr v-if="!filteredLotes.length && !lotesLoading">
                <td class="table-cell text-center text-gray-400" colspan="6">{{ emptyLotesMessage }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showReverterModal" class="modal-overlay">
      <div class="modal-content space-y-4">
        <div>
          <p class="text-xs font-black uppercase tracking-widest text-gray-500">Confirmação</p>
          <h3 class="text-lg font-black text-gray-900">Reverter lote #{{ loteSelecionado?.lote_id }}</h3>
          <p class="text-sm text-gray-600 mt-1">Essa ação remove os registros criados nesta importação, quando não tiverem vínculos ativos.</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-gray-50 p-3 text-sm text-gray-700 space-y-1">
          <p>Arquivo: <span class="font-black">{{ loteSelecionado?.arquivo || '-' }}</span></p>
          <p>Oportunidades criadas: <span class="font-black">{{ loteSelecionado?.created_counts?.oportunidades || 0 }}</span></p>
          <p>Contatos criados: <span class="font-black">{{ loteSelecionado?.created_counts?.contatos || 0 }}</span></p>
          <p>Contas criadas: <span class="font-black">{{ loteSelecionado?.created_counts?.contas || 0 }}</span></p>
          <p>Origens criadas: <span class="font-black">{{ loteSelecionado?.created_counts?.origens || 0 }}</span></p>
        </div>

        <div class="flex justify-end gap-2">
          <button class="btn btn-white" :disabled="revertLoading" @click="closeReverterModal">Cancelar</button>
          <button class="btn btn-danger" :disabled="revertLoading" @click="reverterLoteSelecionado">
            {{ revertLoading ? 'Revertendo...' : 'Confirmar reversão' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const fileInput = ref(null)
const selectedFile = ref(null)
const selectedCanal = ref('')
const modoImportacao = ref('VENDAS')
const canais = ref([])
const dryRun = ref(true)
const importLoading = ref(false)
const errorMessage = ref('')
const result = ref(null)
const activeTab = ref('importar')
const lotes = ref([])
const lotesLoading = ref(false)
const lotesError = ref('')
const loteSearch = ref('')
const loteStatusFilter = ref('todos')
const showReverterModal = ref(false)
const loteSelecionado = ref(null)
const revertLoading = ref(false)
const successMessage = ref('')

const filteredLotes = computed(() => {
  const searchValue = loteSearch.value.trim().toLowerCase()

  return lotes.value.filter((lote) => {
    const matchesStatus =
      loteStatusFilter.value === 'todos' ||
      (loteStatusFilter.value === 'ativos' && !lote.revertido) ||
      (loteStatusFilter.value === 'revertidos' && lote.revertido)

    const arquivo = (lote.arquivo || '').toLowerCase()
    const matchesSearch = !searchValue || arquivo.includes(searchValue)

    return matchesStatus && matchesSearch
  })
})

const emptyLotesMessage = computed(() => {
  if (loteSearch.value.trim() || loteStatusFilter.value !== 'todos') {
    return 'Nenhum lote encontrado para os filtros aplicados.'
  }
  return 'Nenhum lote de importação encontrado.'
})

onMounted(() => {
  loadCanais()
  loadLotes()
})

async function loadCanais() {
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data

    if (!authStore.isAdmin && authStore.user?.canal) {
      selectedCanal.value = String(authStore.user.canal)
    }
  } catch (error) {
    console.error('Erro ao carregar canais:', error)
  }
}

function onFileChange(event) {
  const file = event.target.files?.[0]
  selectedFile.value = file || null
}

function clearForm() {
  selectedFile.value = null
  result.value = null
  errorMessage.value = ''
  successMessage.value = ''
  dryRun.value = true
  modoImportacao.value = 'VENDAS'
  if (fileInput.value) fileInput.value.value = ''
}

async function importar() {
  errorMessage.value = ''
  successMessage.value = ''
  result.value = null

  if (!selectedFile.value) {
    errorMessage.value = 'Selecione um arquivo .xlsx para importar.'
    return
  }

  if (!selectedCanal.value) {
    errorMessage.value = 'Selecione um canal para a importação.'
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('canal_id', selectedCanal.value)
  formData.append('dry_run', dryRun.value ? 'true' : 'false')
  formData.append('modo_importacao', modoImportacao.value)

  importLoading.value = true
  try {
    const response = await api.post('/oportunidades/importar_xlsx/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = response.data
    if (!dryRun.value && response.data?.lote_importacao?.id) {
      successMessage.value = `Importação concluída. Lote #${response.data.lote_importacao.id} criado.`
      await loadLotes()
    }
  } catch (error) {
    console.error('Erro na importação:', error)
    errorMessage.value = error.response?.data?.error || 'Erro ao importar planilha.'
  } finally {
    importLoading.value = false
  }
}

async function loadLotes() {
  lotesLoading.value = true
  lotesError.value = ''
  try {
    const response = await api.get('/oportunidades/importacao_lotes/')
    lotes.value = response.data?.results || []
  } catch (error) {
    console.error('Erro ao carregar lotes:', error)
    lotesError.value = error.response?.data?.error || 'Erro ao carregar lotes de importação.'
  } finally {
    lotesLoading.value = false
  }
}

function openReverterModal(lote) {
  successMessage.value = ''
  lotesError.value = ''
  loteSelecionado.value = lote
  showReverterModal.value = true
}

function closeReverterModal() {
  showReverterModal.value = false
  loteSelecionado.value = null
}

async function reverterLoteSelecionado() {
  if (!loteSelecionado.value?.lote_id) return

  revertLoading.value = true
  lotesError.value = ''
  successMessage.value = ''

  try {
    const response = await api.post('/oportunidades/reverter_importacao/', {
      lote_id: loteSelecionado.value.lote_id
    })
    const resumo = response.data?.rollback_summary || {}
    successMessage.value = `Lote #${loteSelecionado.value.lote_id} revertido. Oportunidades removidas: ${resumo.oportunidades_excluidas || 0}.`
    closeReverterModal()
    await loadLotes()
  } catch (error) {
    console.error('Erro ao reverter lote:', error)
    lotesError.value = error.response?.data?.error || 'Erro ao reverter lote.'
  } finally {
    revertLoading.value = false
  }
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleString('pt-BR')
}

function statusClass(status) {
  if (status === 'ok') return 'bg-emerald-100 text-emerald-700'
  if (status === 'preview') return 'bg-blue-100 text-blue-700'
  if (status === 'erro') return 'bg-red-100 text-red-700'
  return 'bg-gray-100 text-gray-600'
}
</script>

<style scoped>
.btn { @apply px-4 py-2.5 rounded-xl font-black text-xs uppercase tracking-widest transition-all active:scale-95 shadow-sm disabled:opacity-60 disabled:cursor-not-allowed; }
.btn-primary { @apply bg-primary-600 text-white hover:bg-primary-700; }
.btn-white { @apply bg-white border border-gray-200 text-gray-700 hover:bg-gray-50; }
.btn-danger { @apply bg-red-600 text-white hover:bg-red-700; }
.input { @apply w-full px-4 py-2.5 rounded-xl border border-gray-100 bg-gray-50/50 focus:bg-white focus:border-primary-500 focus:ring-4 focus:ring-primary-50 transition-all outline-none text-sm font-bold; }
.table { @apply min-w-full divide-y divide-gray-100; }
.table-header { @apply px-4 py-3 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest bg-gray-50; }
.table-cell { @apply px-4 py-3 text-sm border-t border-gray-50; }
.card { @apply bg-white rounded-2xl border border-gray-100 p-5 shadow-sm; }
.tab-btn { @apply px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 transition-all; }
.tab-btn-active { @apply bg-primary-600 text-white border-primary-600 hover:bg-primary-700; }
.modal-overlay { @apply fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4; }
.modal-content { @apply w-full max-w-xl bg-white rounded-2xl border border-gray-100 shadow-xl p-5; }
</style>
