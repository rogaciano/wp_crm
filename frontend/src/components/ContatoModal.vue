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
          <PhoneInput
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

        <div class="md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Notas
          </label>
          <textarea
            v-model="form.notas"
            rows="1"
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
  notas: ''
})

watch(() => props.show, async (newVal) => {
  if (newVal) {
    // Carregar opções de forma independente para evitar bloqueios
    await loadContas()
    await loadTiposContato()
    await loadCanais()
    
    if (props.fixedContaId) {
      form.value.conta = props.fixedContaId
    }
  }
})

watch(() => props.contato, (newContato) => {
  if (newContato) {
    isEdit.value = true
    form.value = { ...newContato }
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
