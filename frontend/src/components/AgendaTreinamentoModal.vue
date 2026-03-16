<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
    <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-gray-900">
            {{ isEditing ? 'Editar Agendamento' : 'Novo Agendamento' }}
          </h2>
          <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div>
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Título *</label>
            <input v-model="form.titulo" type="text" class="input" placeholder="Ex: Treinamento Módulo Financeiro" required />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Data *</label>
              <input v-model="form.data" type="date" class="input" required />
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Hora Início</label>
              <input v-model="form.hora_inicio" type="time" class="input" />
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Hora Fim</label>
              <input v-model="form.hora_fim" type="time" class="input" />
            </div>
          </div>

          <div v-if="!fixedOnboarding">
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Onboarding *</label>
            <select v-model="form.onboarding" class="input" required>
              <option value="">Selecione...</option>
              <option v-for="ob in onboardings" :key="ob.id" :value="ob.id">{{ ob.conta_nome }}</option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Módulo (opcional)</label>
            <select v-model="form.modulo" class="input">
              <option :value="null">Nenhum módulo específico</option>
              <option v-for="m in modulos" :key="m.id" :value="m.id">{{ m.nome }}</option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Responsável</label>
            <select v-model="form.responsavel" class="input">
              <option :value="null">Eu mesmo</option>
              <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.first_name }} {{ u.last_name }}</option>
            </select>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Modalidade</label>
              <select v-model="form.modalidade" class="input">
                <option value="ONLINE">Online</option>
                <option value="PRESENCIAL">Presencial</option>
              </select>
            </div>
            <div v-if="isEditing">
              <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Status</label>
              <select v-model="form.status" class="input">
                <option value="AGENDADO">Agendado</option>
                <option value="REALIZADO">Realizado</option>
                <option value="CANCELADO">Cancelado</option>
                <option value="REAGENDADO">Reagendado</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Observação</label>
            <textarea v-model="form.observacao" class="input" rows="2" placeholder="Observações..."></textarea>
          </div>

          <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{{ error }}</div>

          <div class="flex justify-between pt-4 border-t border-gray-100">
            <div>
              <button
                v-if="isEditing"
                type="button"
                @click="deleteAgendamento"
                class="btn text-red-600 hover:bg-red-50 text-sm"
              >Excluir</button>
            </div>
            <div class="flex gap-3">
              <button type="button" @click="$emit('close')" class="btn btn-white">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                {{ saving ? 'Salvando...' : (isEditing ? 'Salvar' : 'Agendar') }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  agendamento: Object,
  onboardingId: Number,
})

const emit = defineEmits(['close', 'saved'])

const isEditing = computed(() => !!props.agendamento?.id)
const fixedOnboarding = computed(() => !!props.onboardingId)

const form = ref(getEmptyForm())
const saving = ref(false)
const error = ref('')
const modulos = ref([])
const usuarios = ref([])
const onboardings = ref([])

function getEmptyForm() {
  return {
    titulo: '',
    data: '',
    hora_inicio: null,
    hora_fim: null,
    onboarding: props.onboardingId || '',
    modulo: null,
    responsavel: null,
    observacao: '',
    modalidade: 'ONLINE',
    status: 'AGENDADO'
  }
}

watch(() => props.show, async (val) => {
  if (val) {
    error.value = ''
    if (props.agendamento) {
      form.value = {
        titulo: props.agendamento.titulo || '',
        data: props.agendamento.data || '',
        hora_inicio: props.agendamento.hora_inicio?.substring(0, 5) || null,
        hora_fim: props.agendamento.hora_fim?.substring(0, 5) || null,
        onboarding: props.agendamento.onboarding || '',
        modulo: props.agendamento.modulo || null,
        responsavel: props.agendamento.responsavel || null,
        observacao: props.agendamento.observacao || '',
        modalidade: props.agendamento.modalidade || 'ONLINE',
        status: props.agendamento.status || 'AGENDADO'
      }
    } else {
      form.value = getEmptyForm()
      if (props.onboardingId) form.value.onboarding = props.onboardingId
    }
    await loadDeps()
  }
})

async function loadDeps() {
  try {
    const [mRes, uRes] = await Promise.all([
      api.get('/modulos-treinamento/'),
      api.get('/usuarios/')
    ])
    modulos.value = mRes.data.results || mRes.data
    usuarios.value = uRes.data.results || uRes.data
    if (!fixedOnboarding.value) {
      const obRes = await api.get('/onboardings/', { params: { status: 'EM_ANDAMENTO' } })
      onboardings.value = obRes.data.results || obRes.data
    }
  } catch (e) { console.error(e) }
}

async function handleSubmit() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.hora_inicio) payload.hora_inicio = null
    if (!payload.hora_fim) payload.hora_fim = null
    if (!payload.modulo) payload.modulo = null
    if (!payload.responsavel) payload.responsavel = null

    if (isEditing.value) {
      await api.patch(`/agenda-treinamento/${props.agendamento.id}/`, payload)
    } else {
      await api.post('/agenda-treinamento/', payload)
    }
    emit('saved')
    emit('close')
  } catch (err) {
    console.error('Erro ao salvar agendamento:', err)
    error.value = err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Erro ao salvar agendamento.'
  } finally {
    saving.value = false
  }
}

async function deleteAgendamento() {
  if (!confirm('Excluir este agendamento?')) return
  try {
    await api.delete(`/agenda-treinamento/${props.agendamento.id}/`)
    emit('saved')
    emit('close')
  } catch (e) {
    console.error(e)
    alert('Erro ao excluir agendamento.')
  }
}
</script>
