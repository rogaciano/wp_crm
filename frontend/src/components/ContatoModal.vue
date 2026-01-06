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
            Email
          </label>
          <input
            v-model="form.email"
            type="email"
            class="input"
            placeholder="joao@exemplo.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Empresa (Conta) <span class="text-red-500">*</span>
          </label>
          <select v-model="form.conta" required class="input">
            <option value="">Selecione uma conta...</option>
            <option v-for="conta in contas" :key="conta.id" :value="conta.id">
              {{ conta.nome_empresa }}
            </option>
          </select>
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

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Telefone
          </label>
          <LandlineInput
            v-model="form.telefone"
            input-class="input"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Celular
          </label>
          <PhoneInput
            v-model="form.celular"
            input-class="input"
          />
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
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import PhoneInput from './PhoneInput.vue'
import LandlineInput from './LandlineInput.vue'
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
  redes_sociais_input: []
})

watch(() => props.show, async (newVal) => {
  if (newVal) {
    // Carregar opções de forma independente para evitar bloqueios
    await loadContas()
    await loadTiposContato()
    await loadCanais()
    await loadTiposRedeSocial()
    
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
      }))
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
    redes_sociais_input: []
  }
  fotoPreview.value = null
  fotoFile.value = null
}

async function handleSubmit() {
  loading.value = true
  try {
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
    if (form.value.conta) formData.append('conta', form.value.conta)
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
