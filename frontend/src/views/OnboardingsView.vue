<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Onboarding de Clientes</h1>
        <p class="text-gray-500 text-sm">Acompanhe o treinamento e implantação dos clientes.</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Novo Onboarding
      </button>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3">
      <select v-model="filtroStatus" @change="loadData" class="input w-auto">
        <option value="">Todos os Status</option>
        <option value="EM_ANDAMENTO">Em Andamento</option>
        <option value="CONCLUIDO">Concluído</option>
        <option value="PAUSADO">Pausado</option>
        <option value="CANCELADO">Cancelado</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Lista -->
    <div v-else class="space-y-4">
      <div
        v-for="ob in onboardings"
        :key="ob.id"
        @click="$router.push(`/onboarding/${ob.id}`)"
        class="card p-5 hover:shadow-xl transition-all duration-300 cursor-pointer border border-transparent hover:border-primary-100 group"
      >
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-bold text-gray-900 truncate">{{ ob.conta_nome }}</h3>
              <span
                class="text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wide"
                :class="statusClass(ob.status)"
              >{{ statusLabel(ob.status) }}</span>
            </div>
            <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500">
              <span v-if="ob.responsavel_nome" class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                {{ ob.responsavel_nome }}
              </span>
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                {{ formatDate(ob.data_inicio) }}
              </span>
              <span class="flex items-center gap-1 font-semibold text-gray-700">
                {{ ob.sessoes_concluidas }}/{{ ob.total_sessoes }} módulos
              </span>
            </div>
          </div>

          <!-- Barra de Progresso -->
          <div class="w-full md:w-48 flex flex-col items-end gap-1">
            <span class="text-sm font-bold" :class="ob.progresso === 100 ? 'text-emerald-600' : 'text-primary-600'">
              {{ ob.progresso }}%
            </span>
            <div class="w-full bg-gray-100 rounded-full h-2.5">
              <div
                class="h-2.5 rounded-full transition-all duration-500"
                :class="ob.progresso === 100 ? 'bg-emerald-500' : 'bg-primary-500'"
                :style="{ width: ob.progresso + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="onboardings.length === 0" class="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-100">
        <div class="inline-block p-4 bg-gray-50 rounded-full mb-4">
          <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900">Nenhum onboarding encontrado</h3>
        <p class="text-gray-500 max-w-xs mx-auto mt-2">Crie uma ficha de onboarding para acompanhar o treinamento de um cliente.</p>
        <button @click="showCreateModal = true" class="btn btn-primary mt-6">Criar Primeiro Onboarding</button>
      </div>
    </div>

    <!-- Modal Criar Onboarding -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="showCreateModal = false"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-gray-900">Novo Onboarding</h2>
            <button @click="showCreateModal = false" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>

          <form @submit.prevent="criarOnboarding" class="space-y-5">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Empresa *</label>
              <select v-model="createForm.conta" class="input" required>
                <option value="">Selecione uma empresa</option>
                <option v-for="c in contas" :key="c.id" :value="c.id">{{ c.nome_empresa }}</option>
              </select>
            </div>

            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Responsável</label>
              <select v-model="createForm.responsavel" class="input">
                <option value="">Eu mesmo</option>
                <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.first_name }} {{ u.last_name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Observações</label>
              <textarea v-model="createForm.observacoes" class="input" rows="2" placeholder="Observações gerais..."></textarea>
            </div>

            <div v-if="createError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{{ createError }}</div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
              <button type="button" @click="showCreateModal = false" class="btn btn-white">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="creating">
                {{ creating ? 'Criando...' : 'Criar Onboarding' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const onboardings = ref([])
const contas = ref([])
const usuarios = ref([])
const loading = ref(false)
const filtroStatus = ref('')
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const createForm = ref({ conta: '', responsavel: '', observacoes: '' })

onMounted(() => {
  loadData()
  loadContas()
  loadUsuarios()
})

async function loadData() {
  loading.value = true
  try {
    const params = {}
    if (filtroStatus.value) params.status = filtroStatus.value
    const res = await api.get('/onboardings/', { params })
    onboardings.value = res.data.results || res.data
  } catch (error) {
    console.error('Erro ao carregar onboardings:', error)
  } finally {
    loading.value = false
  }
}

async function loadContas() {
  try {
    const res = await api.get('/contas/', { params: { page_size: 500 } })
    contas.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

async function loadUsuarios() {
  try {
    const res = await api.get('/usuarios/')
    usuarios.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

async function criarOnboarding() {
  creating.value = true
  createError.value = ''
  try {
    const payload = { conta: createForm.value.conta }
    if (createForm.value.responsavel) payload.responsavel = createForm.value.responsavel
    if (createForm.value.observacoes) payload.observacoes = createForm.value.observacoes
    const res = await api.post('/onboardings/', payload)
    showCreateModal.value = false
    createForm.value = { conta: '', responsavel: '', observacoes: '' }
    router.push(`/onboarding/${res.data.id}`)
  } catch (err) {
    createError.value = err.response?.data?.detail || 'Erro ao criar onboarding.'
    console.error(err)
  } finally {
    creating.value = false
  }
}

function statusLabel(s) {
  const map = { EM_ANDAMENTO: 'Em Andamento', CONCLUIDO: 'Concluído', PAUSADO: 'Pausado', CANCELADO: 'Cancelado' }
  return map[s] || s
}

function statusClass(s) {
  const map = {
    EM_ANDAMENTO: 'bg-blue-50 text-blue-700 border border-blue-100',
    CONCLUIDO: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    PAUSADO: 'bg-amber-50 text-amber-700 border border-amber-100',
    CANCELADO: 'bg-gray-100 text-gray-500 border border-gray-200'
  }
  return map[s] || ''
}

function formatDate(d) {
  if (!d) return '-'
  const dt = new Date(d + 'T00:00:00')
  return dt.toLocaleDateString('pt-BR')
}
</script>
