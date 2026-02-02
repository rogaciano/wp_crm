<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Funil' : 'Novo Funil'"
    size="xl"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Coluna da Esquerda: Dados Básicos -->
      <div class="lg:col-span-1 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nome do Funil <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nome"
            type="text"
            required
            class="input"
            placeholder="Ex: Funil SDR, Pipeline de Vendas"
          />
        </div>


        <div>
          <label class="flex items-center space-x-2 cursor-pointer">
            <input type="checkbox" v-model="form.is_active" class="rounded text-primary-600 focus:ring-primary-500" />
            <span class="text-sm font-medium text-gray-700">Funil Ativo</span>
          </label>
        </div>

        <div class="pt-4 border-t border-gray-100">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Usuários com Acesso
          </label>
          <div class="max-h-48 overflow-y-auto space-y-2 p-2 border border-gray-100 rounded-xl bg-gray-50/50">
            <div v-for="user in usuarios" :key="user.id" class="flex items-center space-x-2">
              <input 
                type="checkbox" 
                :id="'user-' + user.id"
                :value="user.id"
                v-model="form.usuarios"
                class="rounded text-primary-600 focus:ring-primary-500"
              />
              <label :for="'user-' + user.id" class="text-sm text-gray-600 cursor-pointer">
                {{ user.full_name || user.username }}
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Coluna da Direita: Estágios (Checkboxes) -->
      <div class="lg:col-span-2 space-y-4">
        <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wider">Configurar Estágios</h3>
        
        <div class="pt-4 border-t border-gray-100">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Estágios do Funil <span class="text-red-500">*</span>
            <span class="text-xs text-gray-400 font-normal ml-2">({{ estagiosSelecionados.length }} selecionado(s))</span>
          </label>
          <div class="max-h-96 overflow-y-auto space-y-2 p-2 border border-gray-100 rounded-xl bg-gray-50/50">
            <div v-if="loadingEstagios" class="flex items-center justify-center py-8">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
              <span class="ml-2 text-sm text-gray-500">Carregando estágios...</span>
            </div>
            
            <div v-else-if="estagiosDisponiveis.length === 0" class="text-center py-8">
              <p class="text-sm text-gray-400">Nenhum estágio disponível.</p>
              <button 
                @click="loadEstagiosDisponiveis()" 
                class="mt-2 text-sm text-primary-600 hover:text-primary-700 underline"
              >
                Tentar carregar novamente
              </button>
            </div>
            
            <div v-else v-for="estagio in estagiosDisponiveis" :key="estagio.id" class="flex items-center space-x-3 p-2 hover:bg-white rounded-lg transition-colors">
              <input 
                type="checkbox" 
                :id="'estagio-' + estagio.id"
                :value="estagio.id"
                v-model="estagiosSelecionados"
                @change="onEstagioChange(estagio.id, $event.target.checked)"
                class="rounded text-primary-600 focus:ring-primary-500"
              />
              <label :for="'estagio-' + estagio.id" class="flex items-center space-x-2 flex-1 cursor-pointer">
                <div class="w-4 h-4 rounded-full flex-shrink-0" :style="{ backgroundColor: estagio.cor || '#3B82F6' }"></div>
                <span class="text-sm text-gray-700 font-medium">{{ estagio.nome }}</span>
                <span class="text-xs text-gray-400 px-2 py-0.5 rounded" :class="{
                  'bg-blue-100 text-blue-700': estagio.tipo === 'ABERTO',
                  'bg-green-100 text-green-700': estagio.tipo === 'GANHO',
                  'bg-red-100 text-red-700': estagio.tipo === 'PERDIDO'
                }">
                  {{ estagio.tipo }}
                </span>
              </label>
              <button
                v-if="estagiosSelecionados.includes(estagio.id)"
                @click.stop="togglePadraoEstagio(estagio.id)"
                type="button"
                class="p-1 rounded hover:bg-gray-100"
                :title="estagiosNoFunil.find(e => e.id === estagio.id)?.is_padrao ? 'Estágio Padrão' : 'Definir como Padrão'"
              >
                <svg 
                  class="w-4 h-4" 
                  :class="estagiosNoFunil.find(e => e.id === estagio.id)?.is_padrao ? 'text-yellow-500 fill-current' : 'text-gray-300'"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </button>
            </div>
          </div>
          
          <div v-if="estagiosSelecionados.length > 0" class="mt-4 p-3 bg-primary-50 border border-primary-100 rounded-lg">
            <p class="text-xs font-bold text-primary-800 uppercase tracking-wider mb-2">Ordem dos Estágios</p>
            <div class="space-y-1">
              <div 
                v-for="(estagio, index) in sortedEstagiosNoFunil" 
                :key="estagio.id"
                class="flex items-center space-x-2 text-sm text-gray-700"
              >
                <span class="text-xs font-bold text-gray-400 w-6">{{ index + 1 }}.</span>
                <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: estagio.cor || '#3B82F6' }"></div>
                <span>{{ estagio.nome }}</span>
                <button
                  v-if="index > 0"
                  @click="moverEstagio(index, -1)"
                  type="button"
                  class="ml-auto text-gray-400 hover:text-primary-600"
                  title="Mover para cima"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path></svg>
                </button>
                <button
                  v-if="index < estagiosSelecionados.length - 1"
                  @click="moverEstagio(index, 1)"
                  type="button"
                  class="text-gray-400 hover:text-primary-600"
                  title="Mover para baixo"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  funil: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const loadingEstagios = ref(false)
const isEdit = ref(false)
const usuarios = ref([])
const estagiosDisponiveis = ref([])
const estagiosSelecionados = ref([]) // IDs dos estágios selecionados
const estagiosNoFunil = ref([]) // Estágios com metadados (ordem, is_padrao)

const sortedEstagiosNoFunil = computed(() => {
  return [...estagiosNoFunil.value].sort((a, b) => (a.ordem || 0) - (b.ordem || 0))
})

const form = ref({
  nome: '',
  tipo: 'OPORTUNIDADE',
  is_active: true,
  usuarios: []
})

onMounted(() => {
  console.log('🔍 FunilModal montado')
  if (props.show) {
    loadInitialData()
  }
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    console.log('🔍 Modal aberto, carregando dados...')
    loadInitialData()
  } else {
    console.log('🔍 Modal fechado')
  }
})

watch(() => props.funil, (newFunil) => {
  if (newFunil) {
    isEdit.value = true
    form.value = { 
      ...newFunil,
      usuarios: [...(newFunil.usuarios || [])]
    }
    loadEstagiosFunil(newFunil.id)
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

async function loadInitialData() {
  loadingEstagios.value = true
  try {
    await Promise.all([
      loadUsuarios(),
      loadEstagiosDisponiveis()
    ])
  } finally {
    loadingEstagios.value = false
  }
}

async function loadUsuarios() {
  try {
    const response = await api.get('/usuarios/')
    usuarios.value = (response.data.results || response.data).map(u => ({
      ...u,
      full_name: `${u.first_name} ${u.last_name}`.trim()
    }))
  } catch (error) {
    console.error('Erro ao carregar usuários:', error)
  }
}

async function loadEstagiosDisponiveis() {
  estagiosDisponiveis.value = [] // Limpar antes de carregar
  try {
    console.log('📋 [FunilModal] Carregando estágios disponíveis...')
    console.log('📋 [FunilModal] Token:', localStorage.getItem('access_token') ? 'Presente' : 'Ausente')
    
    // Buscar todos os estágios (sem paginação)
    const response = await api.get('/estagios-funil/', { 
      params: { 
        page_size: 1000  // Garantir que pegue todos
      } 
    })
    
    console.log('📋 [FunilModal] Resposta completa da API:', response)
    console.log('📋 [FunilModal] response.data:', response.data)
    console.log('📋 [FunilModal] Tipo de response.data:', typeof response.data)
    console.log('📋 [FunilModal] É array?', Array.isArray(response.data))
    
    // Tratar paginação ou resposta direta
    let raw = []
    if (response.data.results) {
      // Resposta paginada
      console.log('📋 [FunilModal] Resposta paginada detectada')
      raw = response.data.results
      console.log('📋 [FunilModal] Primeira página:', raw.length, 'itens')
      // Se houver mais páginas, buscar todas
      if (response.data.next) {
        console.log('📋 [FunilModal] Buscando páginas adicionais...')
        let nextUrl = response.data.next
        let pageCount = 1
        while (nextUrl && pageCount < 10) { // Limite de segurança
          // Removemos o .replace('/api', '') que causava o erro 404
          const nextResponse = await api.get(nextUrl)
          raw = [...raw, ...(nextResponse.data.results || [])]
          nextUrl = nextResponse.data.next
          pageCount++
        }
        console.log('📋 [FunilModal] Total após buscar todas as páginas:', raw.length)
      }
    } else if (Array.isArray(response.data)) {
      // Resposta direta como array
      console.log('📋 [FunilModal] Resposta direta como array')
      raw = response.data
    } else {
      console.warn('⚠️ [FunilModal] Formato de resposta inesperado:', response.data)
      raw = []
    }
    
    console.log('📋 [FunilModal] Dados brutos processados:', raw)
    console.log('📋 [FunilModal] Total de estágios encontrados:', raw.length)
    
    if (raw.length > 0) {
      console.log('📋 [FunilModal] Primeiro estágio exemplo:', raw[0])
    }
    
    // Garantir que seja um array e mapear corretamente
    estagiosDisponiveis.value = Array.isArray(raw) ? raw.map((e, index) => {
      const estagio = {
        id: e.id,
        nome: e.nome || `Estágio ${index + 1}`,
        tipo: e.tipo || 'ABERTO',
        cor: e.cor || '#3B82F6'
      }
      console.log(`📋 [FunilModal] Mapeando estágio ${index + 1}:`, estagio)
      return estagio
    }) : []
    
    console.log('✅ [FunilModal] Estágios disponíveis carregados:', estagiosDisponiveis.value.length)
    console.log('✅ [FunilModal] Lista completa de estágios:', estagiosDisponiveis.value)
    console.log('✅ [FunilModal] estagiosDisponiveis.value é reativo?', estagiosDisponiveis.value)
    
    if (estagiosDisponiveis.value.length === 0) {
      console.warn('⚠️ [FunilModal] Nenhum estágio encontrado no banco de dados.')
      console.warn('⚠️ [FunilModal] Execute: python manage.py shell < backend/setup_database.py')
    }
  } catch (error) {
    console.error('❌ [FunilModal] Erro ao carregar estágios disponíveis:', error)
    console.error('❌ [FunilModal] Status:', error.response?.status)
    console.error('❌ [FunilModal] Status Text:', error.response?.statusText)
    console.error('❌ [FunilModal] Headers:', error.response?.headers)
    console.error('❌ [FunilModal] Detalhes:', error.response?.data || error.message)
    console.error('❌ [FunilModal] URL:', error.config?.url)
    console.error('❌ [FunilModal] Stack:', error.stack)
    estagiosDisponiveis.value = []
  }
}

async function loadEstagiosFunil(funilId) {
  loadingEstagios.value = true
  try {
    // Usamos a nova ação 'estagios' que criamos no FunilViewSet
    const response = await api.get(`/funis/${funilId}/estagios/`)
    const raw = response.data.results || response.data
    
    // Mapear estágios do funil
    estagiosNoFunil.value = raw.map(item => ({
      id: item.estagio_id,
      estagio_id: item.estagio_id,
      nome: item.nome,
      cor: item.cor,
      tipo: item.tipo,
      ordem: item.ordem || 0,
      is_padrao: item.is_padrao || false
    }))
    
    // Ordenar por ordem e atualizar lista de selecionados
    estagiosNoFunil.value.sort((a, b) => a.ordem - b.ordem)
    estagiosSelecionados.value = estagiosNoFunil.value.map(e => e.id)
    
    console.log('✅ Estágios do funil carregados:', estagiosNoFunil.value.length)
  } catch (error) {
    console.error('Erro ao carregar estágios do funil:', error)
  } finally {
    loadingEstagios.value = false
  }
}

function resetForm() {
  form.value = {
    nome: '',
    tipo: 'OPORTUNIDADE',
    is_active: true,
    usuarios: []
  }
  estagiosSelecionados.value = []
  estagiosNoFunil.value = []
}

function getEstagioById(id) {
  return estagiosDisponiveis.value.find(e => e.id === id)
}

function onEstagioChange(estagioId, checked) {
  if (checked) {
    // Adicionar ao funil
    const estagio = getEstagioById(estagioId)
    if (estagio) {
      const index = estagiosSelecionados.value.indexOf(estagioId)
      if (index === -1) {
        estagiosSelecionados.value.push(estagioId)
      }
      
      // Adicionar aos estágios do funil se não existir
      if (!estagiosNoFunil.value.find(e => e.id === estagioId)) {
        estagiosNoFunil.value.push({
          id: estagioId,
          estagio_id: estagioId,
          nome: estagio.nome,
          cor: estagio.cor,
          tipo: estagio.tipo,
          is_padrao: estagiosNoFunil.value.length === 0 // Primeiro é padrão
        })
      }
    }
  } else {
    // Remover do funil
    estagiosSelecionados.value = estagiosSelecionados.value.filter(id => id !== estagioId)
    estagiosNoFunil.value = estagiosNoFunil.value.filter(e => e.id !== estagioId)
  }
  
  // Garantir que pelo menos um estágio seja padrão
  if (estagiosNoFunil.value.length > 0 && !estagiosNoFunil.value.some(e => e.is_padrao)) {
    estagiosNoFunil.value[0].is_padrao = true
  }
}

function moverEstagio(index, direction) {
  const newIndex = index + direction
  if (newIndex >= 0 && newIndex < estagiosSelecionados.value.length) {
    // Mover no array de IDs
    const [removed] = estagiosSelecionados.value.splice(index, 1)
    estagiosSelecionados.value.splice(newIndex, 0, removed)
    
    // Atualizar ordem nos estágios do funil
    atualizarOrdemEstagios()
  }
}

function atualizarOrdemEstagios() {
  estagiosSelecionados.value.forEach((estagioId, index) => {
    const estagioNoFunil = estagiosNoFunil.value.find(e => e.id === estagioId)
    if (estagioNoFunil) {
      estagioNoFunil.ordem = index + 1
    }
  })
  // Forçar atualização do computed reselcionando ou ordenando o array base
  estagiosNoFunil.value.sort((a, b) => a.ordem - b.ordem)
}

function togglePadraoEstagio(estagioId) {
  // Apenas um estágio pode ser padrão
  estagiosNoFunil.value.forEach(e => {
    e.is_padrao = (e.id === estagioId)
  })
}

async function handleSubmit() {
  if (estagiosSelecionados.value.length === 0) {
    alert('Selecione ao menos um estágio para o funil.')
    return
  }

  loading.value = true
  try {
    let funilId = form.value.id
    
    // 1. Salva o Funil
    if (isEdit.value) {
      await api.put(`/funis/${funilId}/`, form.value)
    } else {
      const response = await api.post('/funis/', form.value)
      funilId = response.data.id
    }

    // 2. Atualizar ordem baseada na ordem de seleção
    atualizarOrdemEstagios()

    // 3. Salva os vínculos de estágios na ordem correta
    const estagiosPayload = estagiosSelecionados.value.map((estagioId, index) => {
      const estagioNoFunil = estagiosNoFunil.value.find(e => e.id === estagioId)
      return {
        estagio_id: estagioId,
        ordem: index + 1,
        is_padrao: estagioNoFunil?.is_padrao || false
      }
    })

    await api.post(`/funis/${funilId}/atualizar_estagios/`, {
      estagios: estagiosPayload
    })

    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar funil:', error)
    alert('Erro ao salvar funil: ' + (error.response?.data?.error || error.response?.data?.detail || 'Erro desconhecido'))
  } finally {
    loading.value = false
  }
}
</script>
