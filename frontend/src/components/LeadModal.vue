<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Lead' : 'Novo Lead'"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nome <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nome"
            type="text"
            required
            class="input"
            placeholder="Nome completo"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            v-model="form.email"
            type="email"
            class="input"
            placeholder="email@exemplo.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Telefone
          </label>
          <input
            v-model="form.telefone"
            type="text"
            class="input"
            placeholder="(00) 0000-0000"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Empresa
          </label>
          <input
            v-model="form.empresa"
            type="text"
            class="input"
            placeholder="Nome da empresa"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Cargo
          </label>
          <input
            v-model="form.cargo"
            type="text"
            class="input"
            placeholder="Cargo do contato"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Fonte
          </label>
          <select v-model="form.fonte" class="input">
            <option value="">Selecione...</option>
            <option value="Site">Site</option>
            <option value="Evento">Evento</option>
            <option value="Indicação">Indicação</option>
            <option value="LinkedIn">LinkedIn</option>
            <option value="Cold Call">Cold Call</option>
            <option value="Outro">Outro</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Status do Lead
          </label>
          <select v-model="form.status" class="input">
            <option value="Novo">Novo</option>
            <option value="Contatado">Contatado</option>
            <option value="Qualificado">Qualificado</option>
            <option value="Descartado">Descartado</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Funil <span class="text-red-500">*</span>
          </label>
          <select v-model="form.funil" required class="input">
            <option :value="null">Selecione o funil...</option>
            <option v-for="f in funis" :key="f.id" :value="f.id">{{ f.nome }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Estágio <span class="text-red-500">*</span>
          </label>
          <select v-model="form.estagio" required class="input" :disabled="!form.funil">
            <option :value="null">{{ form.funil ? 'Selecione o estágio...' : 'Selecione um funil primeiro' }}</option>
            <option v-for="e in estagios" :key="e.id" :value="e.id">{{ e.nome }}</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Observações
        </label>
        <textarea
          v-model="form.notas"
          rows="3"
          class="input"
          placeholder="Informações adicionais sobre o lead..."
        ></textarea>
      </div>

      <!-- Seção de Diagnóstico -->
      <div v-if="form.diagnosticos && form.diagnosticos.length > 0" class="mt-8 pt-6 border-t border-gray-100">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900 flex items-center">
            <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            Histórico de Diagnósticos
          </h3>
          <button 
            v-if="selectedDiagnosticos.length === 2"
            type="button"
            @click="handleCompare"
            class="px-3 py-1.5 bg-primary-600 text-white text-xs font-bold rounded-lg hover:bg-primary-700 transition-colors flex items-center shadow-sm"
          >
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            Comparar Selecionados (2)
          </button>
          <span v-else-if="form.diagnosticos.length > 1" class="text-xs text-gray-400 font-medium">Selecione 2 para comparar</span>
        </div>
        
        <div v-for="diag in form.diagnosticos" :key="diag.id" class="bg-gray-50 rounded-xl p-4 mb-4 border border-transparent transition-all" :class="{'border-primary-200 ring-2 ring-primary-50 bg-white': selectedDiagnosticos.includes(diag.id)}">
          <div class="flex justify-between items-center mb-4">
            <div class="flex items-center">
              <input 
                type="checkbox" 
                :id="'diag-' + diag.id"
                :value="diag.id"
                v-model="selectedDiagnosticos"
                :disabled="selectedDiagnosticos.length >= 2 && !selectedDiagnosticos.includes(diag.id)"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mr-3"
              />
              <label :for="'diag-' + diag.id" class="text-xs font-bold text-gray-500 cursor-pointer uppercase tracking-wider">
                Realizado em {{ new Date(diag.data_conclusao).toLocaleDateString('pt-BR') }}
              </label>
            </div>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div v-for="(data, pilar) in diag.pontuacao_por_pilar" :key="pilar" class="text-center p-2 bg-white rounded-lg shadow-sm border border-gray-100">
              <div class="text-xs text-gray-500 mb-1 truncate" :title="pilar">{{ pilar }}</div>
              <div class="text-xl font-black" :style="{ color: data.cor }">{{ data.score }}</div>
              <div class="w-full h-1 bg-gray-100 rounded-full mt-1">
                <div class="h-full rounded-full" :style="{ width: `${data.score * 10}%`, backgroundColor: data.cor }"></div>
              </div>
            </div>
          </div>

          <!-- Análise da IA -->
          <div v-if="diag.analise_ia" class="mt-4 p-3 bg-indigo-50 rounded-lg border border-indigo-100">
            <div class="flex items-center text-xs font-bold text-indigo-700 mb-2">
              <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              ANÁLISE ESTRATÉGICA (IA)
            </div>
            <div class="text-xs text-indigo-900 leading-relaxed whitespace-pre-wrap">
              {{ diag.analise_ia }}
            </div>
          </div>

          <!-- Respostas Detalhadas -->
          <details class="mt-4">
            <summary class="text-xs font-semibold text-primary-600 cursor-pointer hover:text-primary-700 outline-none">
              Ver respostas detalhadas
            </summary>
            <div class="mt-3 space-y-3">
              <div v-for="(resp, idx) in diag.respostas_detalhadas" :key="idx" class="text-sm border-l-2 border-primary-200 pl-3 py-1">
                <div class="font-bold text-gray-700">{{ resp.pergunta }}</div>
                <div class="text-gray-600 mt-1">
                  <span class="font-medium text-primary-700">{{ resp.resposta }}</span>
                  <span class="text-xs text-gray-400 ml-2">({{ resp.pontos }} pts)</span>
                </div>
                <div v-if="resp.feedback" class="text-xs text-amber-600 mt-1 italic">
                  {{ resp.feedback }}
                </div>
              </div>
            </div>
          </details>
        </div>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const router = useRouter()

const props = defineProps({
  show: Boolean,
  lead: Object,
  initialFunilId: Number,
  initialEstagioId: Number
})

const emit = defineEmits(['close', 'saved'])

const form = ref({
  nome: '',
  email: '',
  telefone: '',
  empresa: '',
  cargo: '',
  fonte: '',
  status: 'Novo',
  funil: null,
  estagio: null,
  notas: ''
})

const loading = ref(false)
const isEdit = ref(false)
const selectedDiagnosticos = ref([])
const funis = ref([])
const estagios = ref([])

onMounted(async () => {
  await loadFunis()
})

async function loadFunis() {
  try {
    const response = await api.get('/funis/')
    funis.value = (response.data.results || response.data).filter(f => f.tipo === 'LEAD')
  } catch (error) {
    console.error('Erro ao carregar funis:', error)
  }
}

watch(() => form.value.funil, async (newFunil) => {
  if (newFunil) {
    try {
      const response = await api.get(`/funis/${newFunil}/estagios/`)
      // Normalizar os dados vindos do FunilEstagioSerializer para o select
      const raw = response.data.results || response.data
      estagios.value = raw.map(v => ({
        id: v.estagio_id,
        nome: v.nome
      }))
    } catch (error) {
      console.error('Erro ao carregar estágios:', error)
      estagios.value = []
    }
  } else {
    estagios.value = []
  }
})

function handleCompare() {
  if (selectedDiagnosticos.value.length !== 2) return

  const diag1 = form.value.diagnosticos.find(d => d.id === selectedDiagnosticos.value[0])
  const diag2 = form.value.diagnosticos.find(d => d.id === selectedDiagnosticos.value[1])

  // Ordenar por data (mais antigo em comparison, mais recente em last)
  const sorted = [diag1, diag2].sort((a, b) => new Date(a.data_conclusao) - new Date(b.data_conclusao))
  
  localStorage.setItem('comparison_diagnosis_result', JSON.stringify(sorted[0]))
  localStorage.setItem('last_diagnosis_result', JSON.stringify(sorted[1]))

  // Abrir em nova aba
  const url = router.resolve({ name: 'diagnostico-resultado' }).href
  window.open(url, '_blank')
}


watch(() => props.lead, (newLead) => {
  if (newLead) {
    isEdit.value = true
    form.value = { ...newLead }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    nome: '',
    email: '',
    telefone: '',
    empresa: '',
    cargo: '',
    fonte: '',
    status: 'Novo',
    funil: props.initialFunilId || null,
    estagio: props.initialEstagioId || null,
    notas: ''
  }
}

async function handleSubmit() {
  loading.value = true
  try {
    const data = { ...form.value }
    
    // Remover campos vazios opcionais
    Object.keys(data).forEach(key => {
      if (data[key] === '' || data[key] === null || data[key] === undefined) {
        delete data[key]
      }
    })
    
    // Remover campos que não devem ser enviados na criação
    if (!isEdit.value) {
      delete data.id
      delete data.proprietario
      delete data.proprietario_nome
      delete data.data_criacao
      delete data.data_atualizacao
    }
    
    if (isEdit.value) {
      await api.put(`/leads/${form.value.id}/`, data)
    } else {
      await api.post('/leads/', data)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar lead:', error)
    const errorMsg = error.response?.data?.detail || 
                     JSON.stringify(error.response?.data) || 
                     error.message
    alert('Erro ao salvar lead: ' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>
