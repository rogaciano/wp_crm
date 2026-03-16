<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Agenda de Treinamentos</h1>
        <p class="text-gray-500 text-sm">Próximos treinamentos agendados para os clientes.</p>
      </div>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3">
      <select v-model="filtroStatus" @change="loadData" class="input w-auto">
        <option value="">Todos os Status</option>
        <option value="AGENDADO">Agendado</option>
        <option value="REALIZADO">Realizado</option>
        <option value="CANCELADO">Cancelado</option>
        <option value="REAGENDADO">Reagendado</option>
      </select>
      <select v-model="filtroPeriodo" @change="loadData" class="input w-auto">
        <option value="proximos">Próximos</option>
        <option value="semana">Esta Semana</option>
        <option value="mes">Este Mês</option>
        <option value="todos">Todos</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Agendamentos agrupados por data -->
    <div v-else class="space-y-6">
      <div v-for="(items, data) in agendamentosPorData" :key="data">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex items-center gap-2">
            <div
              class="w-3 h-3 rounded-full"
              :class="isToday(data) ? 'bg-primary-500 animate-pulse' : isPassado(data) ? 'bg-gray-300' : 'bg-emerald-400'"
            ></div>
            <h3 class="text-sm font-black uppercase tracking-widest" :class="isToday(data) ? 'text-primary-600' : 'text-gray-400'">
              {{ formatDateLabel(data) }}
            </h3>
          </div>
          <div class="flex-1 border-t border-gray-100"></div>
        </div>

        <div class="space-y-3 ml-1.5 pl-5 border-l-2" :class="isToday(data) ? 'border-primary-200' : 'border-gray-100'">
          <div
            v-for="ag in items"
            :key="ag.id"
            class="card p-4 hover:shadow-lg transition-all duration-300 cursor-pointer group"
            @click="openEditModal(ag)"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <h4 class="font-bold text-gray-900">{{ ag.titulo }}</h4>
                  <span
                    class="text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-wide"
                    :class="agStatusClass(ag.status)"
                  >{{ agStatusLabel(ag.status) }}</span>
                </div>
                <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                  <span class="flex items-center gap-1 font-semibold text-gray-700">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5" /></svg>
                    {{ ag.onboarding_conta_nome }}
                  </span>
                  <span v-if="ag.modulo_nome" class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
                    {{ ag.modulo_nome }}
                  </span>
                  <span v-if="ag.hora_inicio" class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    {{ ag.hora_inicio?.substring(0,5) }}
                    <template v-if="ag.hora_fim"> - {{ ag.hora_fim?.substring(0,5) }}</template>
                  </span>
                  <span v-if="ag.modalidade" class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded font-bold"
                    :class="ag.modalidade === 'ONLINE' ? 'bg-sky-50 text-sky-600' : 'bg-orange-50 text-orange-600'"
                  >{{ ag.modalidade === 'ONLINE' ? '🖥 Online' : '🏢 Presencial' }}</span>
                  <span v-if="ag.responsavel_nome" class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                    {{ ag.responsavel_nome }}
                  </span>
                </div>
                <p v-if="ag.observacao" class="text-xs text-gray-400 mt-1 truncate">{{ ag.observacao }}</p>
              </div>

              <!-- Ações rápidas -->
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  v-if="ag.status === 'AGENDADO'"
                  @click.stop="marcarRealizado(ag)"
                  class="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                  title="Marcar como realizado"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                </button>
                <button
                  v-if="ag.status === 'AGENDADO'"
                  @click.stop="cancelarAgendamento(ag)"
                  class="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="Cancelar"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="agendamentos.length === 0" class="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-100">
        <div class="inline-block p-4 bg-gray-50 rounded-full mb-4">
          <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900">Nenhum agendamento encontrado</h3>
        <p class="text-gray-500 max-w-xs mx-auto mt-2">Os agendamentos são criados a partir da ficha de onboarding de cada cliente.</p>
      </div>
    </div>

    <!-- Modal Editar Agendamento -->
    <AgendaTreinamentoModal
      :show="showModal"
      :agendamento="selectedAgendamento"
      @close="closeModal"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import AgendaTreinamentoModal from '@/components/AgendaTreinamentoModal.vue'

const agendamentos = ref([])
const loading = ref(false)
const filtroStatus = ref('')
const filtroPeriodo = ref('proximos')
const showModal = ref(false)
const selectedAgendamento = ref(null)

const agendamentosPorData = computed(() => {
  const grouped = {}
  for (const ag of agendamentos.value) {
    const data = ag.data
    if (!grouped[data]) grouped[data] = []
    grouped[data].push(ag)
  }
  return grouped
})

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const params = { ordering: 'data' }
    if (filtroStatus.value) params.status = filtroStatus.value
    if (filtroPeriodo.value === 'proximos') {
      params.proximos = '1'
    } else if (filtroPeriodo.value === 'semana') {
      const today = new Date()
      const end = new Date(today)
      end.setDate(end.getDate() + 7)
      params.data_inicio = formatISO(today)
      params.data_fim = formatISO(end)
    } else if (filtroPeriodo.value === 'mes') {
      const today = new Date()
      const end = new Date(today)
      end.setDate(end.getDate() + 30)
      params.data_inicio = formatISO(today)
      params.data_fim = formatISO(end)
    }
    const res = await api.get('/agenda-treinamento/', { params })
    agendamentos.value = res.data.results || res.data
  } catch (error) {
    console.error('Erro ao carregar agenda:', error)
  } finally {
    loading.value = false
  }
}

function openEditModal(ag) {
  selectedAgendamento.value = ag
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedAgendamento.value = null
}

async function marcarRealizado(ag) {
  try {
    await api.patch(`/agenda-treinamento/${ag.id}/`, { status: 'REALIZADO' })
    ag.status = 'REALIZADO'
  } catch (e) { console.error(e) }
}

async function cancelarAgendamento(ag) {
  if (!confirm('Cancelar este agendamento?')) return
  try {
    await api.patch(`/agenda-treinamento/${ag.id}/`, { status: 'CANCELADO' })
    ag.status = 'CANCELADO'
  } catch (e) { console.error(e) }
}

function isToday(dateStr) {
  return dateStr === formatISO(new Date())
}

function isPassado(dateStr) {
  return dateStr < formatISO(new Date())
}

function formatISO(d) {
  return d.toISOString().split('T')[0]
}

function formatDateLabel(dateStr) {
  const today = formatISO(new Date())
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  if (dateStr === today) return 'Hoje'
  if (dateStr === formatISO(tomorrow)) return 'Amanhã'
  const dt = new Date(dateStr + 'T00:00:00')
  const dia = dt.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' })
  return dia
}

function agStatusLabel(s) {
  const map = { AGENDADO: 'Agendado', REALIZADO: 'Realizado', CANCELADO: 'Cancelado', REAGENDADO: 'Reagendado' }
  return map[s] || s
}

function agStatusClass(s) {
  const map = {
    AGENDADO: 'bg-blue-50 text-blue-700 border border-blue-100',
    REALIZADO: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    CANCELADO: 'bg-gray-100 text-gray-500 border border-gray-200',
    REAGENDADO: 'bg-amber-50 text-amber-700 border border-amber-100'
  }
  return map[s] || ''
}
</script>
