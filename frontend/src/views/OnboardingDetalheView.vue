<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <template v-else-if="onboarding">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button @click="$router.push('/onboardings')" class="text-sm text-gray-400 hover:text-gray-600 mb-2 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            Voltar
          </button>
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900">{{ onboarding.conta_nome }}</h1>
          <div class="flex flex-wrap items-center gap-3 mt-2">
            <span
              class="text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wide"
              :class="statusClass(onboarding.status)"
            >{{ statusLabel(onboarding.status) }}</span>
            <span v-if="onboarding.responsavel_nome" class="text-sm text-gray-500">
              Responsável: <strong>{{ onboarding.responsavel_nome }}</strong>
            </span>
            <span class="text-sm text-gray-500">
              Início: <strong>{{ formatDate(onboarding.data_inicio) }}</strong>
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <select v-model="onboarding.status" @change="updateStatus" class="input w-auto text-sm">
            <option value="EM_ANDAMENTO">Em Andamento</option>
            <option value="CONCLUIDO">Concluído</option>
            <option value="PAUSADO">Pausado</option>
            <option value="CANCELADO">Cancelado</option>
          </select>
        </div>
      </div>

      <!-- Progresso Geral -->
      <div class="card p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="font-bold text-gray-900">Progresso do Onboarding</h2>
          <span class="text-2xl font-black" :class="onboarding.progresso === 100 ? 'text-emerald-600' : 'text-primary-600'">
            {{ onboarding.progresso }}%
          </span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-4">
          <div
            class="h-4 rounded-full transition-all duration-700"
            :class="onboarding.progresso === 100 ? 'bg-emerald-500' : 'bg-primary-500'"
            :style="{ width: onboarding.progresso + '%' }"
          ></div>
        </div>
        <p class="text-sm text-gray-500 mt-2">
          {{ sessoesConcluidas }} de {{ onboarding.sessoes.length }} módulos concluídos
        </p>
      </div>

      <!-- Observações -->
      <div v-if="onboarding.observacoes" class="card p-5">
        <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Observações Gerais</h3>
        <p class="text-gray-700 text-sm whitespace-pre-line">{{ onboarding.observacoes }}</p>
      </div>

      <!-- Lista de Sessões (Checklist) -->
      <div class="space-y-3">
        <h2 class="text-lg font-bold text-gray-900">Sessões de Treinamento</h2>

        <div
          v-for="sessao in onboarding.sessoes"
          :key="sessao.id"
          class="card overflow-hidden transition-all duration-300"
          :class="sessao.status === 'CONCLUIDO' ? 'border-l-4 border-l-emerald-500' : sessao.status === 'CANCELADO' ? 'border-l-4 border-l-gray-300 opacity-60' : 'border-l-4 border-l-blue-400'"
        >
          <!-- Header da Sessão -->
          <div
            class="p-5 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
            @click="toggleSessao(sessao.id)"
          >
            <div class="flex items-center gap-4 flex-1 min-w-0">
              <!-- Checkbox visual -->
              <button
                @click.stop="toggleConcluido(sessao)"
                class="w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all flex-shrink-0"
                :class="sessao.status === 'CONCLUIDO'
                  ? 'bg-emerald-500 border-emerald-500 text-white'
                  : 'border-gray-300 hover:border-primary-400'"
              >
                <svg v-if="sessao.status === 'CONCLUIDO'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
              </button>

              <div class="min-w-0">
                <h3 class="font-bold text-gray-900" :class="{ 'line-through text-gray-400': sessao.status === 'CANCELADO' }">
                  {{ sessao.modulo_nome }}
                </h3>
                <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500 mt-1">
                  <span class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    {{ formatDuracao(sessao.modulo_carga_horaria) }}
                  </span>
                  <span v-if="sessao.data" class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    {{ formatDate(sessao.data) }}
                    <template v-if="sessao.hora_inicio"> · {{ sessao.hora_inicio?.substring(0,5) }}</template>
                    <template v-if="sessao.hora_fim"> - {{ sessao.hora_fim?.substring(0,5) }}</template>
                  </span>
                  <span v-if="sessao.treinador_nome" class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                    {{ sessao.treinador_nome }}
                  </span>
                  <span v-if="sessao.participantes_detalhe?.length" class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                    {{ sessao.participantes_detalhe.map(p => p.nome).join(', ') }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Chevron -->
            <svg
              class="w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ml-2"
              :class="{ 'rotate-180': expandedSessao === sessao.id }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            ><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </div>

          <!-- Detalhes expandidos -->
          <div v-if="expandedSessao === sessao.id" class="border-t border-gray-100 p-5 bg-gray-50/50">
            <form @submit.prevent="salvarSessao(sessao)" class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Data</label>
                  <input v-model="sessao.data" type="date" class="input" />
                </div>
                <div>
                  <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Hora Início</label>
                  <input v-model="sessao.hora_inicio" type="time" class="input" />
                </div>
                <div>
                  <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Hora Fim</label>
                  <input v-model="sessao.hora_fim" type="time" class="input" />
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Treinador</label>
                  <select v-model="sessao.treinador" class="input">
                    <option :value="null">Selecione...</option>
                    <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.first_name }} {{ u.last_name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Status</label>
                  <select v-model="sessao.status" class="input">
                    <option value="PENDENTE">Pendente</option>
                    <option value="CONCLUIDO">Concluído</option>
                    <option value="CANCELADO">Cancelado</option>
                  </select>
                </div>
              </div>

              <div>
                <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Participantes da Empresa</label>
                <div class="flex flex-wrap gap-2">
                  <label
                    v-for="contato in contatos"
                    :key="contato.id"
                    class="flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer transition-colors text-sm"
                    :class="sessao.participantes?.includes(contato.id) ? 'bg-primary-50 border-primary-300 text-primary-700' : 'bg-white border-gray-200 hover:border-gray-300'"
                  >
                    <input
                      type="checkbox"
                      :value="contato.id"
                      v-model="sessao.participantes"
                      class="sr-only"
                    />
                    <span class="w-2 h-2 rounded-full" :class="sessao.participantes?.includes(contato.id) ? 'bg-primary-500' : 'bg-gray-300'"></span>
                    {{ contato.nome }}
                  </label>
                  <span v-if="contatos.length === 0" class="text-gray-400 text-sm italic">Nenhum contato vinculado à empresa.</span>
                </div>
              </div>

              <div>
                <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Observação</label>
                <textarea v-model="sessao.observacao" class="input" rows="2" placeholder="Notas sobre esta sessão..."></textarea>
              </div>

              <!-- Assinatura -->
              <div>
                <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Assinatura</label>
                <div v-if="sessao.assinatura" class="mb-2">
                  <img :src="sessao.assinatura" class="max-h-24 border border-gray-200 rounded-lg bg-white" alt="Assinatura" />
                  <button type="button" @click="sessao.assinatura = null" class="text-xs text-red-500 mt-1 hover:underline">Limpar assinatura</button>
                </div>
                <div v-else>
                  <canvas
                    :ref="el => { if (el) signatureCanvases[sessao.id] = el }"
                    class="w-full h-24 border border-gray-200 rounded-lg bg-white cursor-crosshair"
                    @mousedown="startDrawing($event, sessao.id)"
                    @mousemove="draw($event, sessao.id)"
                    @mouseup="stopDrawing(sessao.id)"
                    @mouseleave="stopDrawing(sessao.id)"
                    @touchstart.prevent="startDrawingTouch($event, sessao.id)"
                    @touchmove.prevent="drawTouch($event, sessao.id)"
                    @touchend="stopDrawing(sessao.id)"
                  ></canvas>
                  <div class="flex gap-2 mt-1">
                    <button type="button" @click="clearSignature(sessao.id)" class="text-xs text-gray-500 hover:underline">Limpar</button>
                    <button type="button" @click="captureSignature(sessao)" class="text-xs text-primary-600 hover:underline">Capturar</button>
                  </div>
                </div>
              </div>

              <div class="flex justify-end gap-3 pt-3 border-t border-gray-100">
                <button type="submit" class="btn btn-primary text-sm" :disabled="saving">
                  {{ saving ? 'Salvando...' : 'Salvar Sessão' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Agendamentos -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">Próximos Agendamentos</h2>
          <button @click="showAgendaModal = true" class="btn btn-primary text-sm">+ Agendar Treinamento</button>
        </div>

        <div v-if="agendamentos.length === 0" class="card p-5 text-center text-gray-400 text-sm">
          Nenhum treinamento agendado. Clique em "+ Agendar Treinamento" para criar.
        </div>

        <div
          v-for="ag in agendamentos"
          :key="ag.id"
          class="card p-4 flex items-center justify-between gap-4 hover:shadow-md transition-all cursor-pointer"
          @click="editAgendamento(ag)"
        >
          <div class="flex items-center gap-4 flex-1 min-w-0">
            <div class="flex flex-col items-center justify-center w-14 h-14 rounded-xl flex-shrink-0"
              :class="ag.status === 'REALIZADO' ? 'bg-emerald-50 text-emerald-600' : ag.status === 'CANCELADO' ? 'bg-gray-100 text-gray-400' : 'bg-primary-50 text-primary-600'"
            >
              <span class="text-lg font-black leading-none">{{ formatDay(ag.data) }}</span>
              <span class="text-[10px] font-bold uppercase">{{ formatMonth(ag.data) }}</span>
            </div>
            <div class="min-w-0">
              <h4 class="font-bold text-gray-900 truncate">{{ ag.titulo }}</h4>
              <div class="flex items-center gap-3 text-xs text-gray-500 mt-0.5">
                <span v-if="ag.hora_inicio">{{ ag.hora_inicio?.substring(0,5) }}<template v-if="ag.hora_fim"> - {{ ag.hora_fim?.substring(0,5) }}</template></span>
                <span v-if="ag.modulo_nome">{{ ag.modulo_nome }}</span>
                <span v-if="ag.responsavel_nome">{{ ag.responsavel_nome }}</span>
              </div>
            </div>
          </div>
          <span
            class="text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-wide flex-shrink-0"
            :class="{
              'bg-blue-50 text-blue-700 border border-blue-100': ag.status === 'AGENDADO',
              'bg-emerald-50 text-emerald-700 border border-emerald-100': ag.status === 'REALIZADO',
              'bg-gray-100 text-gray-500 border border-gray-200': ag.status === 'CANCELADO',
              'bg-amber-50 text-amber-700 border border-amber-100': ag.status === 'REAGENDADO'
            }"
          >{{ agStatusLabel(ag.status) }}</span>
        </div>
      </div>

      <!-- Modal Agenda -->
      <AgendaTreinamentoModal
        :show="showAgendaModal"
        :agendamento="selectedAgendamento"
        :onboarding-id="onboarding?.id"
        @close="closeAgendaModal"
        @saved="loadAgendamentos"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import AgendaTreinamentoModal from '@/components/AgendaTreinamentoModal.vue'

const route = useRoute()
const authStore = useAuthStore()
const onboarding = ref(null)
const loading = ref(false)
const saving = ref(false)
const expandedSessao = ref(null)
const usuarios = ref([])
const contatos = ref([])

// Agenda
const agendamentos = ref([])
const showAgendaModal = ref(false)
const selectedAgendamento = ref(null)

// Signature
const signatureCanvases = ref({})
const isDrawing = ref(false)

const sessoesConcluidas = computed(() => {
  if (!onboarding.value?.sessoes) return 0
  return onboarding.value.sessoes.filter(s => s.status === 'CONCLUIDO').length
})

onMounted(() => {
  loadOnboarding()
  loadUsuarios()
  loadAgendamentos()
})

async function loadOnboarding() {
  loading.value = true
  try {
    const res = await api.get(`/onboardings/${route.params.id}/`)
    onboarding.value = res.data
    // Garantir que participantes é array de IDs
    onboarding.value.sessoes.forEach(s => {
      if (s.participantes_detalhe && !Array.isArray(s.participantes)) {
        s.participantes = s.participantes_detalhe.map(p => p.id)
      }
    })
    // Carregar contatos da empresa
    if (onboarding.value.conta) {
      loadContatos(onboarding.value.conta)
    }
  } catch (error) {
    console.error('Erro ao carregar onboarding:', error)
  } finally {
    loading.value = false
  }
}

async function loadContatos(contaId) {
  try {
    const res = await api.get('/contatos/', { params: { conta: contaId, page_size: 100 } })
    contatos.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

async function loadUsuarios() {
  try {
    const params = { is_active: true, funis_tipo: 'POS_VENDA' }
    if (authStore.user?.canal) {
      params.canal = authStore.user.canal
    }
    const res = await api.get('/usuarios/', { params })
    usuarios.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

async function updateStatus() {
  try {
    await api.patch(`/onboardings/${onboarding.value.id}/`, { status: onboarding.value.status })
  } catch (e) { console.error(e) }
}

function toggleSessao(id) {
  expandedSessao.value = expandedSessao.value === id ? null : id
  if (expandedSessao.value === id) {
    nextTick(() => initCanvas(id))
  }
}

async function toggleConcluido(sessao) {
  const newStatus = sessao.status === 'CONCLUIDO' ? 'PENDENTE' : 'CONCLUIDO'
  try {
    await api.patch(`/sessoes-treinamento/${sessao.id}/`, { status: newStatus })
    sessao.status = newStatus
    // Recalcular progresso
    recalcProgresso()
  } catch (e) { console.error(e) }
}

async function salvarSessao(sessao) {
  saving.value = true
  try {
    const payload = {
      status: sessao.status,
      data: sessao.data || null,
      hora_inicio: sessao.hora_inicio || null,
      hora_fim: sessao.hora_fim || null,
      observacao: sessao.observacao || '',
      treinador: sessao.treinador || null,
      participantes: sessao.participantes || [],
      assinatura: sessao.assinatura || null
    }
    const res = await api.patch(`/sessoes-treinamento/${sessao.id}/`, payload)
    // Atualizar dados locais
    sessao.treinador_nome = res.data.treinador_nome
    sessao.participantes_detalhe = res.data.participantes_detalhe
    recalcProgresso()
  } catch (e) {
    console.error('Erro ao salvar sessão:', e)
    alert('Erro ao salvar sessão.')
  } finally {
    saving.value = false
  }
}

function recalcProgresso() {
  if (!onboarding.value) return
  const total = onboarding.value.sessoes.length
  if (total === 0) { onboarding.value.progresso = 0; return }
  const done = onboarding.value.sessoes.filter(s => s.status === 'CONCLUIDO').length
  onboarding.value.progresso = Math.round((done / total) * 100)
}

// ===================== Signature Drawing =====================
function initCanvas(sessaoId) {
  const canvas = signatureCanvases.value[sessaoId]
  if (!canvas) return
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  const ctx = canvas.getContext('2d')
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.strokeStyle = '#1e293b'
}

function getPos(e, sessaoId) {
  const canvas = signatureCanvases.value[sessaoId]
  const rect = canvas.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function startDrawing(e, sessaoId) {
  isDrawing.value = true
  const canvas = signatureCanvases.value[sessaoId]
  const ctx = canvas.getContext('2d')
  const pos = getPos(e, sessaoId)
  ctx.beginPath()
  ctx.moveTo(pos.x, pos.y)
}

function draw(e, sessaoId) {
  if (!isDrawing.value) return
  const canvas = signatureCanvases.value[sessaoId]
  const ctx = canvas.getContext('2d')
  const pos = getPos(e, sessaoId)
  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
}

function stopDrawing() {
  isDrawing.value = false
}

function startDrawingTouch(e, sessaoId) {
  const touch = e.touches[0]
  startDrawing({ clientX: touch.clientX, clientY: touch.clientY }, sessaoId)
}

function drawTouch(e, sessaoId) {
  const touch = e.touches[0]
  draw({ clientX: touch.clientX, clientY: touch.clientY }, sessaoId)
}

function clearSignature(sessaoId) {
  const canvas = signatureCanvases.value[sessaoId]
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
}

function captureSignature(sessao) {
  const canvas = signatureCanvases.value[sessao.id]
  if (!canvas) return
  sessao.assinatura = canvas.toDataURL('image/png')
}

// ===================== Helpers =====================
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

function formatDuracao(minutos) {
  if (!minutos) return '-'
  if (minutos < 60) return `${minutos}min`
  const h = Math.floor(minutos / 60)
  const m = minutos % 60
  return m > 0 ? `${h}h ${m}min` : `${h}h`
}

// ===================== Agenda =====================
async function loadAgendamentos() {
  try {
    const res = await api.get('/agenda-treinamento/', { params: { onboarding: route.params.id, ordering: 'data' } })
    agendamentos.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

function editAgendamento(ag) {
  selectedAgendamento.value = ag
  showAgendaModal.value = true
}

function closeAgendaModal() {
  showAgendaModal.value = false
  selectedAgendamento.value = null
}

function formatDay(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').getDate().toString().padStart(2, '0')
}

function formatMonth(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR', { month: 'short' }).replace('.', '')
}

function agStatusLabel(s) {
  const map = { AGENDADO: 'Agendado', REALIZADO: 'Realizado', CANCELADO: 'Cancelado', REAGENDADO: 'Reagendado' }
  return map[s] || s
}
</script>
