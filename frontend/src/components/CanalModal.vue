<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Canal' : 'Novo Canal'"
    size="md"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome do Canal</label>
        <input v-model="form.nome" @input="generateSlug" type="text" required class="input" placeholder="Ex: Vendas Diretas, Parceiro X" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Slug (URL do Diagnóstico)
          <span class="text-gray-400 font-normal">- usado no link público</span>
        </label>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">/d/</span>
          <input 
            v-model="form.slug" 
            type="text" 
            class="input flex-1" 
            :placeholder="slugSugerido || 'ex: nome-do-canal'"
            pattern="[a-z0-9-]+"
          />
        </div>
        <p class="mt-1 text-xs text-gray-500 italic">
          Link: <code class="bg-gray-100 px-1 rounded">{{ baseUrl }}/d/{{ form.slug || slugSugerido || 'slug-do-canal' }}</code>
        </p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Responsável pelo Canal</label>
        <select v-model="form.responsavel" class="input">
          <option value="">Selecione um responsável...</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.first_name }} {{ user.last_name }} (@{{ user.username }})
          </option>
        </select>
        <p class="mt-1 text-xs text-gray-500 italic">O responsável terá acesso a todos os dados deste canal.</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Estado (UF)
          <span class="text-gray-400 font-normal">- para exibir no mapa</span>
        </label>
        <select v-model="form.estado" class="input">
          <option value="">Selecione o estado...</option>
          <option v-for="uf in ESTADOS" :key="uf.sigla" :value="uf.sigla">{{ uf.sigla }} - {{ uf.nome }}</option>
        </select>
      </div>

      <!-- Cor do canal no mapa -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Cor do Canal no Mapa
        </label>
        <div class="flex items-center gap-3">
          <input
            type="color"
            v-model="form.cor"
            class="w-12 h-10 rounded-lg border border-zinc-300 cursor-pointer p-0.5"
          />
          <span class="text-sm text-zinc-600 font-mono font-medium">{{ form.cor }}</span>
          <div class="w-6 h-6 rounded-full border-2 border-white shadow" :style="{ backgroundColor: form.cor }"></div>
        </div>
        <!-- Paleta rápida -->
        <div class="flex gap-2 mt-2 flex-wrap">
          <button
            v-for="c in PALETA_RAPIDA"
            :key="c"
            type="button"
            @click="form.cor = c"
            class="w-7 h-7 rounded-full border-2 transition-transform hover:scale-110"
            :style="{ backgroundColor: c, borderColor: form.cor === c ? '#111' : 'transparent' }"
            :title="c"
          />
        </div>
        <p class="mt-1 text-xs text-gray-400">Esta cor será usada nos pins do mapa para identificar clientes deste canal.</p>
      </div>

      <!-- Funil e Estágio Padrão -->
      <div class="border-t pt-4 mt-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Destino das Novas Oportunidades
        </h4>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Funil Padrão</label>
            <select v-model="form.funil_padrao" @change="onFunilChange" class="input">
              <option value="">Sistema decide</option>
              <option v-for="funil in funis" :key="funil.id" :value="funil.id">
                {{ funil.nome }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estágio Inicial</label>
            <select v-model="form.estagio_inicial" class="input" :disabled="!form.funil_padrao">
              <option value="">Primeiro do funil</option>
              <option v-for="estagio in estagiosDoFunil" :key="estagio.estagio_id" :value="estagio.estagio_id">
                {{ estagio.nome }}
              </option>
            </select>
          </div>
        </div>
        <p class="mt-2 text-xs text-gray-500 italic">
          Oportunidades via diagnóstico ou cadastro serão direcionadas para este funil/estágio.
        </p>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  canal: Object
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)
const users = ref([])
const funis = ref([])
const estagiosDoFunil = ref([])

const ESTADOS = [
  { sigla: 'AC', nome: 'Acre' }, { sigla: 'AL', nome: 'Alagoas' }, { sigla: 'AP', nome: 'Amapá' },
  { sigla: 'AM', nome: 'Amazonas' }, { sigla: 'BA', nome: 'Bahia' }, { sigla: 'CE', nome: 'Ceará' },
  { sigla: 'DF', nome: 'Distrito Federal' }, { sigla: 'ES', nome: 'Espírito Santo' }, { sigla: 'GO', nome: 'Goiás' },
  { sigla: 'MA', nome: 'Maranhão' }, { sigla: 'MT', nome: 'Mato Grosso' }, { sigla: 'MS', nome: 'Mato Grosso do Sul' },
  { sigla: 'MG', nome: 'Minas Gerais' }, { sigla: 'PA', nome: 'Pará' }, { sigla: 'PB', nome: 'Paraíba' },
  { sigla: 'PR', nome: 'Paraná' }, { sigla: 'PE', nome: 'Pernambuco' }, { sigla: 'PI', nome: 'Piauí' },
  { sigla: 'RJ', nome: 'Rio de Janeiro' }, { sigla: 'RN', nome: 'Rio Grande do Norte' },
  { sigla: 'RS', nome: 'Rio Grande do Sul' }, { sigla: 'RO', nome: 'Rondônia' }, { sigla: 'RR', nome: 'Roraima' },
  { sigla: 'SC', nome: 'Santa Catarina' }, { sigla: 'SP', nome: 'São Paulo' }, { sigla: 'SE', nome: 'Sergipe' },
  { sigla: 'TO', nome: 'Tocantins' },
]

const PALETA_RAPIDA = [
  '#F97316', '#10B981', '#3B82F6', '#8B5CF6',
  '#EF4444', '#EAB308', '#EC4899', '#06B6D4',
  '#0F172A', '#14B8A6', '#6366F1', '#84CC16',
]

const form = ref({
  nome: '',
  slug: '',
  estado: '',
  cor: '#F97316',
  responsavel: '',
  funil_padrao: '',
  estagio_inicial: ''
})

// URL base para mostrar no preview
const baseUrl = computed(() => {
  return window.location.origin
})

// Slug sugerido baseado no nome (para placeholder e preview)
const slugSugerido = computed(() => {
  if (!form.value.nome) return ''
  return form.value.nome
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
})

onMounted(() => {
  loadUsers()
  loadFunis()
})

async function loadUsers() {
  try {
    const response = await api.get('/usuarios/')
    users.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar usuários:', error)
  }
}

async function loadFunis() {
  try {
    const response = await api.get('/funis/')
    funis.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar funis:', error)
  }
}

async function onFunilChange() {
  form.value.estagio_inicial = ''
  estagiosDoFunil.value = []
  
  if (form.value.funil_padrao) {
    try {
      const response = await api.get(`/funis/${form.value.funil_padrao}/`)
      estagiosDoFunil.value = response.data.estagios_detalhe || []
    } catch (error) {
      console.error('Erro ao carregar estágios:', error)
    }
  }
}

// Gera slug automaticamente a partir do nome (apenas se ainda não tem slug)
function generateSlug() {
  if (!isEdit.value || !form.value.slug) {
    form.value.slug = form.value.nome
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove acentos
      .replace(/[^a-z0-9]+/g, '-')     // Substitui não alfanuméricos por -
      .replace(/^-+|-+$/g, '')          // Remove - do início/fim
  }
}

watch(() => props.canal, async (newCanal) => {
  if (newCanal) {
    isEdit.value = true
    form.value = { 
      ...newCanal,
      slug: newCanal.slug || '',
      cor: newCanal.cor || '#F97316',
      funil_padrao: newCanal.funil_padrao || '',
      estagio_inicial: newCanal.estagio_inicial || ''
    }
    // Carrega estágios se tem funil
    if (newCanal.funil_padrao) {
      await onFunilChange()
      // Redefine o estágio após carregar
      form.value.estagio_inicial = newCanal.estagio_inicial || ''
    }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.value = {
    nome: '',
    slug: '',
    estado: '',
    cor: '#F97316',
    responsavel: '',
    funil_padrao: '',
    estagio_inicial: ''
  }
  estagiosDoFunil.value = []
}

async function handleSubmit() {
  if (!form.value.nome) return
  
  loading.value = true
  try {
    const data = { 
      ...form.value,
      slug: form.value.slug || null,
      funil_padrao: form.value.funil_padrao || null,
      estagio_inicial: form.value.estagio_inicial || null
    }
    if (!data.responsavel) data.responsavel = null

    if (isEdit.value) {
      await api.put(`/canais/${form.value.id}/`, data)
    } else {
      await api.post('/canais/', data)
    }
    
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar canal:', error)
    alert('Erro ao salvar canal')
  } finally {
    loading.value = false
  }
}
</script>
