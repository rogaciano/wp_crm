<template>
  <div v-if="conta">
    <div class="mb-6 flex justify-between items-start">
      <div>
        <button @click="$router.back()" class="text-primary-600 hover:text-primary-700 mb-4 flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          Voltar
        </button>
        <h1 class="text-3xl font-bold text-gray-900">{{ conta.nome_empresa }}</h1>
        <p v-if="conta.cnpj" class="text-gray-600 mt-1">CNPJ: {{ conta.cnpj }}</p>
      </div>
      <button @click="openEditContaModal" class="btn btn-secondary flex items-center mt-8">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
        Editar Conta
      </button>
    </div>

    <!-- Informações Gerais -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div class="lg:col-span-2 card">
        <h2 class="text-xl font-semibold mb-4">Informações</h2>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500">Telefone</p>
            <p class="font-medium">{{ conta.telefone_principal || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Email</p>
            <p class="font-medium">{{ conta.email || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Website</p>
            <p class="font-medium">
              <a v-if="conta.website" :href="conta.website" target="_blank" class="text-primary-600 hover:underline">
                {{ conta.website }}
              </a>
              <span v-else>N/A</span>
            </p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Setor</p>
            <p class="font-medium">{{ conta.setor || 'N/A' }}</p>
          </div>
          <div class="col-span-2">
            <p class="text-sm text-gray-500">Endereço</p>
            <p class="font-medium">
              {{ conta.endereco || 'N/A' }}
              <span v-if="conta.cidade">, {{ conta.cidade }} - {{ conta.estado }}</span>
            </p>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="text-xl font-semibold mb-4">Resumo</h2>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-gray-600">Contatos</span>
            <span class="text-2xl font-bold text-primary-600">{{ contatos.length }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-600">Oportunidades</span>
            <span class="text-2xl font-bold text-green-600">{{ oportunidades.length }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-600">Valor Total</span>
            <span class="text-lg font-bold text-green-600">
              R$ {{ valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="card">
      <div class="border-b mb-6">
        <nav class="-mb-px flex space-x-8">
          <button
            @click="activeTab = 'contatos'"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'contatos'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Contatos ({{ contatos.length }})
          </button>
          <button
            @click="activeTab = 'oportunidades'"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'oportunidades'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Oportunidades ({{ oportunidades.length }})
          </button>
        </nav>
      </div>

      <!-- Contatos Tab -->
      <div v-if="activeTab === 'contatos'">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">Lista de Contatos</h3>
          <button @click="openContactModal()" class="btn btn-primary text-xs">+ Adicionar Contato</button>
        </div>
        <div class="space-y-4">
          <div
            v-for="contato in contatos"
            :key="contato.id"
            class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
          >
            <div>
              <h3 class="font-medium text-gray-900">{{ contato.nome }}</h3>
              <p class="text-sm text-gray-500">{{ contato.cargo || 'N/A' }}</p>
              <div class="mt-1 text-sm text-gray-600">
                <span v-if="contato.email">{{ contato.email }}</span>
                <span v-if="contato.telefone" class="ml-4">{{ contato.telefone }}</span>
              </div>
            </div>
            <div class="flex space-x-2">
              <button @click="openContactModal(contato)" class="text-primary-600 hover:text-primary-900 text-sm">Editar</button>
              <button @click="deleteContato(contato.id)" class="text-red-600 hover:text-red-900 text-sm">Excluir</button>
            </div>
          </div>
          <p v-if="contatos.length === 0" class="text-center text-gray-500 py-8">
            Nenhum contato cadastrado
          </p>
        </div>
      </div>

      <!-- Oportunidades Tab -->
      <div v-if="activeTab === 'oportunidades'">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">Lista de Oportunidades</h3>
          <button @click="openOportunidadeModal()" class="btn btn-primary text-xs">+ Adicionar Oportunidade</button>
        </div>
        <div class="space-y-4">
          <div
            v-for="oportunidade in oportunidades"
            :key="oportunidade.id"
            class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
          >
            <div>
              <h3 class="font-medium text-gray-900">{{ oportunidade.nome }}</h3>
              <p class="text-sm text-gray-500">{{ oportunidade.estagio_nome }}</p>
            </div>
            <div class="flex items-center space-x-4">
              <div class="text-right">
                <p class="font-semibold text-green-600">
                  R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </p>
                <p v-if="oportunidade.probabilidade" class="text-sm text-gray-500">
                  {{ oportunidade.probabilidade }}% prob.
                </p>
              </div>
              <button @click="openOportunidadeModal(oportunidade)" class="text-primary-600 hover:text-primary-900 text-sm">Editar</button>
            </div>
          </div>
          <p v-if="oportunidades.length === 0" class="text-center text-gray-500 py-8">
            Nenhuma oportunidade cadastrada
          </p>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="text-center py-12">
    <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
  </div>

  <ContatoModal
    :show="showContactModal"
    :contato="selectedContato"
    :fixed-conta-id="conta?.id"
    @close="showContactModal = false"
    @saved="refreshContacts"
  />

  <OportunidadeModal
    :show="showOportunidadeModal"
    :oportunidade="selectedOportunidade"
    :fixed-conta-id="conta?.id"
    @close="showOportunidadeModal = false"
    @saved="refreshOportunidades"
  />

  <ContaModal
    :show="showEditContaModal"
    :conta="conta"
    @close="showEditContaModal = false"
    @saved="loadContaData"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import ContatoModal from '@/components/ContatoModal.vue'
import OportunidadeModal from '@/components/OportunidadeModal.vue'
import ContaModal from '@/components/ContaModal.vue'

const route = useRoute()
const conta = ref(null)
const contatos = ref([])
const oportunidades = ref([])
const loading = ref(false)
const activeTab = ref('contatos')

const showEditContaModal = ref(false)
const showContactModal = ref(false)
const selectedContato = ref(null)

const showOportunidadeModal = ref(false)
const selectedOportunidade = ref(null)

function openContactModal(contato = null) {
  selectedContato.value = contato
  showContactModal.value = true
}

async function refreshContacts() {
  const contaId = route.params.id
  try {
    const res = await api.get(`/contas/${contaId}/contatos/`)
    contatos.value = res.data
  } catch (error) {
    console.error('Erro ao atualizar contatos:', error)
  }
}

function openOportunidadeModal(oportunidade = null) {
  selectedOportunidade.value = oportunidade
  showOportunidadeModal.value = true
}

function openEditContaModal() {
  showEditContaModal.value = true
}

async function loadContaData() {
  loading.value = true
  try {
    const contaId = route.params.id
    
    const [contaRes, contatosRes, oportunidadesRes] = await Promise.all([
      api.get(`/contas/${contaId}/`),
      api.get(`/contas/${contaId}/contatos/`),
      api.get(`/contas/${contaId}/oportunidades/`)
    ])
    
    conta.value = contaRes.data
    contatos.value = contatosRes.data
    oportunidades.value = oportunidadesRes.data
  } catch (error) {
    console.error('Erro ao carregar conta:', error)
  } finally {
    loading.value = false
  }
}

async function refreshOportunidades() {
  const contaId = route.params.id
  try {
    const res = await api.get(`/contas/${contaId}/oportunidades/`)
    oportunidades.value = res.data
  } catch (error) {
    console.error('Erro ao atualizar oportunidades:', error)
  }
}

async function deleteContato(id) {
  if (!confirm('Tem certeza que deseja excluir este contato?')) return
  try {
    await api.delete(`/contatos/${id}/`)
    refreshContacts()
  } catch (error) {
    console.error('Erro ao excluir contato:', error)
    alert('Erro ao excluir contato')
  }
}

const valorTotal = computed(() => {
  return oportunidades.value.reduce((sum, opp) => {
    return sum + Number(opp.valor_estimado || 0)
  }, 0)
})

onMounted(async () => {
  await loadContaData()
})
</script>
