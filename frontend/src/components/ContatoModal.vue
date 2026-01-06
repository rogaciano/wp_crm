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
        <div class="md:col-span-2">
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
    redes_sociais_input: []
  }
}

async function handleSubmit() {
  loading.value = true
  try {
    const data = { ...form.value }
    
    // Filtrar redes sociais vazias
    data.redes_sociais_input = (data.redes_sociais_input || []).filter(
      r => r.tipo && r.valor
    )
    
    // Remover campos vazios opcionais (exceto redes_sociais_input que pode ser array vazio)
    Object.keys(data).forEach(key => {
      if (key !== 'redes_sociais_input' && (data[key] === '' || data[key] === null || data[key] === undefined)) {
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
    
    // Remover campo de leitura que vem do backend
    delete data.redes_sociais
    
    if (isEdit.value) {
      await api.put(`/contatos/${form.value.id}/`, data)
    } else {
      await api.post('/contatos/', data)
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
