<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Contato' : 'Novo Contato'"
    size="lg"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        <!-- Foto do Contato -->
        <div class="md:col-span-2 flex items-center gap-4">
          <div class="relative">
            <img 
              v-if="fotoPreview || form.foto_url" 
              :src="fotoPreview || form.foto_url" 
              class="w-20 h-20 rounded-full object-cover ring-2 ring-primary-100 shadow-sm"
            />
            <div 
              v-else 
              class="w-20 h-20 rounded-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center text-white font-bold text-2xl shadow-sm ring-2 ring-gray-200"
            >
              {{ form.nome?.charAt(0)?.toUpperCase() || '?' }}
            </div>
            <label 
              class="absolute bottom-0 right-0 p-1.5 bg-primary-500 hover:bg-primary-600 text-white rounded-full cursor-pointer shadow-lg transition-colors"
              title="Alterar foto"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              <input 
                type="file" 
                accept="image/*" 
                class="hidden" 
                @change="handleFotoChange"
              />
            </label>
          </div>
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Nome Completo <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.nome"
              type="text"
              required
              class="input"
              placeholder="Ex: João da Silva"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Empresa (Conta)
          </label>
          <div class="flex gap-2">
            <select v-model="form.conta" class="input flex-1">
              <option value="">Selecione uma conta...</option>
              <option v-for="conta in contas" :key="conta.id" :value="conta.id">
                {{ conta.nome_empresa }}
              </option>
            </select>
            <button 
              type="button"
              @click="showNovaEmpresaModal = true"
              class="px-3 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors flex items-center gap-1"
              title="Criar nova empresa"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Cargo
          </label>
          <input
            v-model="form.cargo"
            type="text"
            class="input"
            placeholder="Ex: Gerente de Compras"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Departamento
          </label>
          <input
            v-model="form.departamento"
            type="text"
            class="input"
            placeholder="Ex: Comercial"
          />
        </div>
        <!-- Múltiplos Telefones -->
        <div class="md:col-span-2 pt-3 mt-2 border-t border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
              Telefones
            </p>
            <button 
              type="button"
              @click="adicionarTelefone"
              class="text-xs text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Adicionar
            </button>
          </div>
          
          <div class="space-y-2">
            <div 
              v-for="(tel, index) in form.telefones_input" 
              :key="'tel-' + index"
              class="flex items-center gap-2"
            >
              <select v-model="tel.tipo" class="input w-32 text-sm">
                <option value="CELULAR">Celular</option>
                <option value="COMERCIAL">Comercial</option>
                <option value="RESIDENCIAL">Residencial</option>
                <option value="WHATSAPP">WhatsApp</option>
                <option value="OUTRO">Outro</option>
              </select>
              <PhoneInput
                v-model="tel.numero"
                input-class="input flex-1 text-sm"
              />
              <label class="flex items-center gap-1 text-xs text-gray-500">
                <input type="checkbox" v-model="tel.principal" class="rounded" />
                Principal
              </label>
              <button 
                type="button"
                @click="removerTelefone(index)"
                class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            
            <p v-if="form.telefones_input.length === 0" class="text-sm text-gray-400 italic">
              Nenhum telefone adicionado
            </p>
          </div>
        </div>

        <!-- Múltiplos Emails -->
        <div class="md:col-span-2 pt-3 border-t border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              E-mails
            </p>
            <button 
              type="button"
              @click="adicionarEmail"
              class="text-xs text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Adicionar
            </button>
          </div>
          
          <div class="space-y-2">
            <div 
              v-for="(email, index) in form.emails_input" 
              :key="'email-' + index"
              class="flex items-center gap-2"
            >
              <select v-model="email.tipo" class="input w-32 text-sm">
                <option value="COMERCIAL">Comercial</option>
                <option value="PESSOAL">Pessoal</option>
                <option value="OUTRO">Outro</option>
              </select>
              <input
                v-model="email.email"
                type="email"
                class="input flex-1 text-sm"
                placeholder="email@exemplo.com"
              />
              <label class="flex items-center gap-1 text-xs text-gray-500">
                <input type="checkbox" v-model="email.principal" class="rounded" />
                Principal
              </label>
              <button 
                type="button"
                @click="removerEmail(index)"
                class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            
            <p v-if="form.emails_input.length === 0" class="text-sm text-gray-400 italic">
              Nenhum e-mail adicionado
            </p>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Chave PIX
          </label>
          <input
            v-model="form.chave_pix"
            type="text"
            class="input"
            placeholder="Ex: email@exemplo.com, CPF, telefone ou chave aleatória"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Tipo de Contato
          </label>
          <select v-model="form.tipo_contato" class="input">
            <option :value="null">Nenhum...</option>
            <option v-for="tipo in tiposContato" :key="tipo.id" :value="tipo.id">
              {{ tipo.nome }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Canal Associado
          </label>
          <select 
            v-model="form.canal" 
            class="input"
            :disabled="!authStore.isAdmin"
          >
            <option :value="null">Sem Canal...</option>
            <option v-for="canal in canais" :key="canal.id" :value="canal.id">
              {{ canal.nome }}
            </option>
          </select>
        </div>

        <!-- Tags -->
        <div class="md:col-span-2 pt-3 mt-2 border-t border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
              </svg>
              Tags
            </p>
          </div>
          
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tag in tagsDisponiveis"
              :key="tag.id"
              type="button"
              @click="toggleTag(tag.id)"
              class="px-3 py-1 text-xs font-medium rounded-full transition-all"
              :class="form.tags.includes(tag.id) 
                ? 'ring-2 ring-offset-1 opacity-100' 
                : 'opacity-50 hover:opacity-75'"
              :style="{ 
                backgroundColor: form.tags.includes(tag.id) ? tag.cor : tag.cor + '40',
                color: form.tags.includes(tag.id) ? '#fff' : tag.cor,
                ringColor: tag.cor
              }"
            >
              {{ tag.nome }}
            </button>
            
            <p v-if="tagsDisponiveis.length === 0" class="text-sm text-gray-400 italic">
              Nenhuma tag disponível
            </p>
          </div>
        </div>

        <!-- Redes Sociais -->
        <div class="md:col-span-2 pt-3 mt-2 border-t border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <svg class="w-4 h-4 text-primary-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
              Redes Sociais
            </p>
            <button 
              type="button"
              @click="adicionarRedeSocial"
              class="text-xs text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Adicionar
            </button>
          </div>
          
          <!-- Lista de redes sociais -->
          <div class="space-y-3">
            <div 
              v-for="(rede, index) in form.redes_sociais_input" 
              :key="index"
              class="flex items-center gap-2"
            >
              <select 
                v-model="rede.tipo" 
                class="input w-40 text-sm"
              >
                <option :value="null">Selecione...</option>
                <option 
                  v-for="tipo in tiposRedeSocial" 
                  :key="tipo.id" 
                  :value="tipo.id"
                >
                  {{ tipo.nome }}
                </option>
              </select>
              <input
                v-model="rede.valor"
                type="text"
                class="input flex-1 text-sm"
                :placeholder="getPlaceholder(rede.tipo)"
              />
              <button 
                type="button"
                @click="removerRedeSocial(index)"
                class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            
            <p v-if="form.redes_sociais_input.length === 0" class="text-sm text-gray-400 italic">
              Nenhuma rede social adicionada
            </p>
          </div>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Notas
          </label>
          <textarea
            v-model="form.notas"
            rows="2"
            class="input"
            placeholder="Observações..."
          ></textarea>
        </div>

        <!-- Informações de Auditoria (apenas em edição) -->
        <div v-if="isEdit" class="md:col-span-2 pt-3 mt-2 border-t border-gray-100">
          <p class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Informações de Registro
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="font-medium text-gray-600 mb-1">Criado</p>
              <p v-if="form.criado_por_nome" class="text-gray-900 font-semibold">{{ form.criado_por_nome }}</p>
              <p v-else class="text-gray-400 italic">Usuário não registrado</p>
              <p class="text-gray-500 mt-1">{{ formatDateTime(form.data_criacao) }}</p>
            </div>

            <div class="bg-gray-50 rounded-lg p-3">
              <p class="font-medium text-gray-600 mb-1">Última atualização</p>
              <p v-if="form.atualizado_por_nome" class="text-gray-900 font-semibold">{{ form.atualizado_por_nome }}</p>
              <p v-else class="text-gray-400 italic">Usuário não registrado</p>
              <p class="text-gray-500 mt-1">{{ formatDateTime(form.data_atualizacao) }}</p>
            </div>
          </div>
        </div>
      </div>
    </form>
  </BaseModal>
  
  <!-- Modal para criar nova empresa -->
  <ContaModal
    :show="showNovaEmpresaModal"
    @close="showNovaEmpresaModal = false"
    @saved="handleNovaEmpresaSaved"
  />
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import PhoneInput from './PhoneInput.vue'
import ContaModal from './ContaModal.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const props = defineProps({
  show: Boolean,
  contato: Object,
  fixedContaId: [Number, String] // Permite fixar uma conta (quando vindo do detalhe da conta)
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)
const contas = ref([])
const tiposContato = ref([])
const canais = ref([])
const tiposRedeSocial = ref([])
const tagsDisponiveis = ref([])
const showNovaEmpresaModal = ref(false)

// Foto do contato
const fotoPreview = ref(null)
const fotoFile = ref(null)

const form = ref({
  nome: '',
  email: '',
  telefone: '',
  celular: '',
  cargo: '',
  departamento: '',
  chave_pix: '',
  conta: '',
  tipo_contato: null,
  canal: null,
  tipo: 'PADRAO',
  notas: '',
  foto_url: null,
  redes_sociais_input: [],
  telefones_input: [],
  emails_input: [],
  tags: []
})

watch(() => props.show, async (newVal) => {
  if (newVal) {
    // Carregar opções de forma independente para evitar bloqueios
    await loadContas()
    await loadTiposContato()
    await loadCanais()
    await loadTiposRedeSocial()
    await loadTags()
    
    if (props.fixedContaId) {
      form.value.conta = props.fixedContaId
    }
  } else {
    // Limpar preview da foto quando fechar modal
    fotoPreview.value = null
    fotoFile.value = null
  }
})

watch(() => props.contato, (newContato) => {
  if (newContato) {
    isEdit.value = true
    form.value = { 
      ...newContato,
      // Converter redes_sociais do formato de leitura para o formato de escrita
      redes_sociais_input: (newContato.redes_sociais || []).map(r => ({
        tipo: r.tipo,
        valor: r.valor
      })),
      // Converter telefones do formato de leitura para o formato de escrita
      telefones_input: (newContato.telefones || []).map(t => ({
        numero: t.numero,
        tipo: t.tipo,
        principal: t.principal
      })),
      // Converter emails do formato de leitura para o formato de escrita
      emails_input: (newContato.emails || []).map(e => ({
        email: e.email,
        tipo: e.tipo,
        principal: e.principal
      })),
      // Tags (array de IDs)
      tags: (newContato.tags || [])
    }
    fotoPreview.value = null
    fotoFile.value = null
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

async function loadContas() {
  try {
    const response = await api.get('/contas/')
    contas.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar contas:', error)
  }
}

async function handleNovaEmpresaSaved() {
  // Recarrega a lista de contas
  await loadContas()
  
  // Seleciona a última conta criada (a mais recente)
  if (contas.value.length > 0) {
    // Ordena por data de criação (desc) e pega a primeira
    const contasOrdenadas = [...contas.value].sort((a, b) => 
      new Date(b.data_criacao) - new Date(a.data_criacao)
    )
    form.value.conta = contasOrdenadas[0].id
  }
  
  showNovaEmpresaModal.value = false
}

async function loadTiposContato() {
  try {
    const response = await api.get('/tipos-contato/')
    tiposContato.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar tipos de contato:', error)
  }
}

async function loadCanais() {
  try {
    const response = await api.get('/canais/')
    canais.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar canais:', error)
  }
}

async function loadTiposRedeSocial() {
  try {
    const response = await api.get('/tipos-rede-social/')
    tiposRedeSocial.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar tipos de redes sociais:', error)
  }
}

async function loadTags() {
  try {
    const response = await api.get('/tags/')
    tagsDisponiveis.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar tags:', error)
  }
}

function toggleTag(tagId) {
  const index = form.value.tags.indexOf(tagId)
  if (index === -1) {
    form.value.tags.push(tagId)
  } else {
    form.value.tags.splice(index, 1)
  }
}

function getPlaceholder(tipoId) {
  const tipo = tiposRedeSocial.value.find(t => t.id === tipoId)
  return tipo?.placeholder || 'Informe o usuário ou URL'
}

function adicionarRedeSocial() {
  form.value.redes_sociais_input.push({ tipo: null, valor: '' })
}

function removerRedeSocial(index) {
  form.value.redes_sociais_input.splice(index, 1)
}

function adicionarTelefone() {
  const isFirst = form.value.telefones_input.length === 0
  form.value.telefones_input.push({ numero: '', tipo: 'CELULAR', principal: isFirst })
}

function removerTelefone(index) {
  const wasPrincipal = form.value.telefones_input[index].principal
  form.value.telefones_input.splice(index, 1)
  
  // Se removeu o principal e ainda tem telefones, define o primeiro como principal
  if (wasPrincipal && form.value.telefones_input.length > 0) {
    form.value.telefones_input[0].principal = true
  }
}

function adicionarEmail() {
  form.value.emails_input.push({ email: '', tipo: 'COMERCIAL', principal: false })
}

function removerEmail(index) {
  form.value.emails_input.splice(index, 1)
}

function handleFotoChange(event) {
  const file = event.target.files[0]
  if (file) {
    fotoFile.value = file
    // Criar preview
    const reader = new FileReader()
    reader.onload = (e) => {
      fotoPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

function formatDateTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const options = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }
  return date.toLocaleString('pt-BR', options)
}

function resetForm() {
  form.value = {
    nome: '',
    email: '',
    telefone: '',
    celular: '',
    cargo: '',
    departamento: '',
    chave_pix: '',
    conta: props.fixedContaId || '',
    tipo_contato: null,
    canal: authStore.isAdmin ? null : (authStore.user?.canal || null),
    tipo: 'PADRAO',
    notas: '',
    foto_url: null,
    redes_sociais_input: [],
    telefones_input: [],
    emails_input: [],
    tags: []
  }
  fotoPreview.value = null
  fotoFile.value = null
}

async function handleSubmit() {
  loading.value = true
  try {
    // Validação: Pelo menos um telefone deve existir
    const hasPhone = form.value.telefones_input.some(t => t.numero && t.numero.trim() !== '')
    if (!hasPhone) {
      alert('É obrigatório cadastrar pelo menos um telefone.')
      loading.value = false
      return
    }

    // Usar FormData para suportar upload de arquivo
    const formData = new FormData()
    
    // Adicionar campos do formulário
    formData.append('nome', form.value.nome)
    if (form.value.email) formData.append('email', form.value.email)
    if (form.value.telefone) formData.append('telefone', form.value.telefone)
    if (form.value.celular) formData.append('celular', form.value.celular)
    if (form.value.cargo) formData.append('cargo', form.value.cargo)
    if (form.value.departamento) formData.append('departamento', form.value.departamento)
    if (form.value.chave_pix) formData.append('chave_pix', form.value.chave_pix)
    
    // Envia o valor de conta (mesmo que vazio, para permitir remover)
    formData.append('conta', form.value.conta || '')
    
    if (form.value.tipo_contato) formData.append('tipo_contato', form.value.tipo_contato)
    if (form.value.canal) formData.append('canal', form.value.canal)
    formData.append('tipo', form.value.tipo || 'PADRAO')
    if (form.value.notas) formData.append('notas', form.value.notas)
    
    // Adicionar foto se houver nova
    if (fotoFile.value) {
      formData.append('foto', fotoFile.value)
    }
    
    // Adicionar redes sociais como JSON
    const redesSociais = (form.value.redes_sociais_input || []).filter(r => r.tipo && r.valor)
    formData.append('redes_sociais_input', JSON.stringify(redesSociais))
    
    // Adicionar telefones como JSON
    const telefones = (form.value.telefones_input || []).filter(t => t.numero)
    formData.append('telefones_input', JSON.stringify(telefones))
    
    // Adicionar emails como JSON
    const emails = (form.value.emails_input || []).filter(e => e.email)
    formData.append('emails_input', JSON.stringify(emails))
    
    // Adicionar tags como JSON (array de IDs)
    formData.append('tags_input', JSON.stringify(form.value.tags || []))
    
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
    
    if (isEdit.value) {
      await api.put(`/contatos/${form.value.id}/`, formData, config)
    } else {
      await api.post('/contatos/', formData, config)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar contato:', error)
    const errorMsg = error.response?.data?.detail || 
                     JSON.stringify(error.response?.data) || 
                     error.message
    alert('Erro ao salvar contato: ' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>
