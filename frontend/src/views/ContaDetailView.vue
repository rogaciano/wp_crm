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
          
          <!-- Marcas -->
          <div class="col-span-2 bg-gray-50 p-3 rounded-lg border border-gray-100" v-if="conta.marca || conta.marcas_adicionais?.length">
            <p class="text-xs text-gray-400 font-bold uppercase mb-2 flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>
              Marcas
            </p>
            <div class="flex flex-wrap gap-2">
              <span v-if="conta.marca" class="px-2.5 py-1 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 shadow-sm">
                {{ conta.marca }} (Principal)
              </span>
              <span 
                v-for="m in conta.marcas_adicionais" 
                :key="m.id"
                class="px-2.5 py-1 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 shadow-sm"
              >
                {{ m.nome }}
              </span>
            </div>
          </div>

          <!-- Etiquetas (Tags) -->
          <div class="col-span-2">
            <p class="text-xs text-gray-400 font-bold uppercase mb-2 flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>
              Etiquetas
            </p>
            <TagInput
              v-model="contaTagsIds"
              v-model:tagsDetail="contaTagsDetail"
              placeholder="Adicionar etiqueta..."
              @update:modelValue="saveTagsConta"
            />
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
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-gray-800 flex items-center gap-2">
            <svg class="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            Contatos da Empresa
          </h3>
          <button @click="openContactModal()" class="btn btn-primary shadow-sm flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Novo Contato
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="contato in contatos"
            :key="contato.id"
            class="group p-5 bg-white border border-gray-100 rounded-xl hover:border-primary-200 hover:shadow-md transition-all duration-300 relative overflow-hidden"
          >
            <!-- Background Accent -->
            <div class="absolute top-0 right-0 w-24 h-24 bg-primary-50 rounded-full -mr-12 -mt-12 opacity-0 group-hover:opacity-40 transition-opacity duration-500"></div>

            <div class="flex items-start gap-4">
              <!-- Avatar placeholder -->
              <div 
                @click="viewContato(contato.id)"
                class="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-lg shadow-sm flex-shrink-0 cursor-pointer"
              >
                {{ contato.nome?.charAt(0)?.toUpperCase() || '?' }}
              </div>

              <div class="flex-1 min-w-0">
                <h4 
                  @click="viewContato(contato.id)"
                  class="font-bold text-gray-900 truncate hover:text-primary-600 cursor-pointer text-lg"
                >
                  {{ contato.nome }}
                </h4>
                <p class="text-sm text-gray-500 font-medium truncate">{{ contato.cargo || 'Responsável' }}</p>
                
                <div class="mt-3 space-y-1.5">
                  <div v-if="contato.email" class="flex items-center gap-2 text-sm text-gray-600">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    <span class="truncate">{{ contato.email }}</span>
                  </div>
                  <!-- Telefone principal (legado ou primeiro da lista) -->
                  <div v-if="getContatoPhone(contato)" class="flex items-center gap-2 text-sm text-gray-600">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                    </svg>
                    <span class="font-medium">{{ getContatoPhoneFormatted(contato) }}</span>
                    <!-- WhatsApp inline link -->
                    <button 
                      @click.stop="openWhatsapp(contato)"
                      class="ml-1 text-emerald-500 hover:text-emerald-600 transition-colors"
                      title="Abrir WhatsApp"
                    >
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                      </svg>
                    </button>
                  </div>
                  <!-- Telefones adicionais da lista -->
                  <template v-if="getAdditionalPhones(contato).length > 0">
                    <div 
                      v-for="tel in getAdditionalPhones(contato)" 
                      :key="tel.id" 
                      class="flex items-center gap-2 text-sm text-gray-500"
                    >
                      <svg class="w-3.5 h-3.5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                      </svg>
                      <span>{{ tel.numero }}</span>
                      <span class="text-xs text-gray-400">({{ tel.tipo }})</span>
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <div class="mt-4 pt-4 border-t border-gray-50 flex justify-end gap-3">
              <button @click="openContactModal(contato)" class="p-2 text-gray-400 hover:text-primary-600 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                </svg>
              </button>
              <button @click="deleteContato(contato.id)" class="p-2 text-gray-400 hover:text-red-600 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
          
          <div v-if="contatos.length === 0" class="md:col-span-2 card bg-gray-50 border-dashed border-2 py-12 flex flex-col items-center justify-center opacity-60">
            <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <p class="text-xl font-medium text-gray-500">Nenhum contato cadastrado</p>
            <p class="text-sm text-gray-400 mt-2">Clique em "+ Novo Contato" para começar</p>
          </div>
        </div>
      </div>

      <!-- Oportunidades Tab -->
      <div v-if="activeTab === 'oportunidades'">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-gray-800 flex items-center gap-2">
            <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Oportunidades de Negócio
          </h3>
          <button @click="openOportunidadeModal()" class="btn btn-primary shadow-sm flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Nova Oportunidade
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="oportunidade in oportunidades"
            :key="oportunidade.id"
            class="p-5 bg-white border border-gray-100 rounded-xl hover:border-green-200 hover:shadow-md transition-all duration-300 flex flex-col justify-between"
          >
            <div>
              <div class="flex justify-between items-start mb-3">
                <span 
                  class="px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
                  :class="{
                    'bg-blue-100 text-blue-700': opport_is_early(oportunidade.estagio_nome),
                    'bg-amber-100 text-amber-700': opport_is_mid(oportunidade.estagio_nome),
                    'bg-green-100 text-green-700': opport_is_late(oportunidade.estagio_nome)
                  }"
                >
                  {{ oportunidade.estagio_nome }}
                </span>
                <span class="text-2xl">💰</span>
              </div>
              
              <h4 class="font-bold text-gray-900 text-lg mb-1 leading-tight">{{ oportunidade.nome }}</h4>
              <p class="text-sm text-gray-500 mb-4">Atualizado em: {{ formatShortDate(oportunidade.data_atualizacao) }}</p>
            </div>

            <div class="flex items-end justify-between pt-4 border-t border-gray-50">
              <div>
                <p class="text-xs text-gray-400 font-bold uppercase">Valor Estimado</p>
                <p class="text-xl font-black text-green-600">
                  R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </p>
              </div>
              <div class="flex gap-2">
                <button @click="openOportunidadeModal(oportunidade)" class="p-2 text-gray-400 hover:text-primary-600 transition-colors bg-gray-50 rounded-lg">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div v-if="oportunidades.length === 0" class="md:col-span-2 card bg-gray-50 border-dashed border-2 py-12 flex flex-col items-center justify-center opacity-60">
            <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
            </svg>
            <p class="text-xl font-medium text-gray-500">Nenhuma oportunidade ativa</p>
            <p class="text-sm text-gray-400 mt-2">Clique em "+ Nova Oportunidade" para prospectar</p>
          </div>
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
    :fixed-contato-principal-id="defaultContatoPrincipalId"
    :fixed-contatos-ids="contextContatosNovaOportunidade"
    :fixed-empresas-ids="contextEmpresasNovaOportunidade"
    :fixed-canal-id="conta?.canal || null"
    @close="showOportunidadeModal = false"
    @saved="refreshOportunidades"
  />

  <ContaModal
    :show="showEditContaModal"
    :conta="conta"
    @close="showEditContaModal = false"
    @saved="loadContaData"
  />

  <WhatsappChat
    :show="showWhatsapp"
    :number="whatsappData.number"
    :title="whatsappData.title"
    :oportunidade="whatsappData.oportunidade"
    @close="showWhatsapp = false"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import ContatoModal from '@/components/ContatoModal.vue'
import OportunidadeModal from '@/components/OportunidadeModal.vue'
import ContaModal from '@/components/ContaModal.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'
import TagInput from '@/components/TagInput.vue'

const route = useRoute()
const router = useRouter()
const conta = ref(null)
const contatos = ref([])
const oportunidades = ref([])
const loading = ref(false)
const activeTab = ref('contatos')
const contaTagsIds = ref([])
const contaTagsDetail = ref([])

const showEditContaModal = ref(false)
const showContactModal = ref(false)
const selectedContato = ref(null)

const showOportunidadeModal = ref(false)
const selectedOportunidade = ref(null)

const showWhatsapp = ref(false)
const whatsappData = ref({ number: '', title: '', oportunidade: null })

function openContactModal(contato = null) {
  selectedContato.value = contato
  showContactModal.value = true
}

function viewContato(id) {
  router.push(`/contatos/${id}`)
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
  if (oportunidade && oportunidade.id) {
    router.push({ name: 'oportunidade-detail', params: { id: oportunidade.id } })
  } else {
    selectedOportunidade.value = null
    showOportunidadeModal.value = true
  }
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
    contaTagsIds.value = contaRes.data.tags || []
    contaTagsDetail.value = contaRes.data.tags_detail || []
  } catch (error) {
    console.error('Erro ao carregar conta:', error)
  } finally {
    loading.value = false
  }
}

async function saveTagsConta() {
  if (!conta.value) return
  try {
    await api.patch(`/contas/${conta.value.id}/`, { tags_ids: JSON.stringify(contaTagsIds.value) })
  } catch (err) {
    console.error('Erro ao salvar tags da conta:', err)
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

const defaultContatoPrincipalId = computed(() => {
  if (!contatos.value.length) return null

  const contatoComFlagPrincipal = contatos.value.find(c => c.principal === true)
  if (contatoComFlagPrincipal?.id) return contatoComFlagPrincipal.id

  if (contatos.value.length === 1) return contatos.value[0].id

  return null
})

const contextContatosNovaOportunidade = computed(() => {
  return contatos.value.map(c => c.id).filter(Boolean)
})

const contextEmpresasNovaOportunidade = computed(() => {
  return conta.value?.id ? [conta.value.id] : []
})

onMounted(async () => {
  await loadContaData()
})

// Funções auxiliares de contato
function getContatoPhone(contato) {
  if (contato.celular) return contato.celular
  if (contato.telefone) return contato.telefone
  if (contato.telefones && contato.telefones.length > 0) {
    const principal = contato.telefones.find(t => t.principal)
    return (principal || contato.telefones[0]).numero
  }
  return null
}

function getContatoPhoneFormatted(contato) {
  if (contato.celular_formatado) return contato.celular_formatado
  if (contato.telefone_formatado) return contato.telefone_formatado
  return getContatoPhone(contato) || ''
}

function normalizePhone(value) {
  return (value || '').replace(/\D/g, '')
}

function getAdditionalPhones(contato) {
  const telefones = contato?.telefones || []
  if (!telefones.length) return []

  const primaryNormalized = normalizePhone(getContatoPhone(contato))
  const seen = new Set()

  return telefones.filter((tel) => {
    const normalized = normalizePhone(tel.numero)
    if (!normalized) return false
    if (normalized === primaryNormalized) return false
    if (seen.has(normalized)) return false
    seen.add(normalized)
    return true
  })
}

function openWhatsapp(contato) {
  const phone = getContatoPhone(contato)
  if (!phone) {
    alert('Contato sem telefone cadastrado.')
    return
  }
  let cleanNumber = phone.replace(/\D/g, '')
  if (!cleanNumber.startsWith('55') && cleanNumber.length <= 11) {
    cleanNumber = '55' + cleanNumber
  }
  whatsappData.value = { number: cleanNumber, title: contato.nome, oportunidade: null }
  showWhatsapp.value = true
}

// Funções auxiliares de UI
function formatShortDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

function opport_is_early(estagio) {
  const early = ['Prospecção', 'Qualificação', 'Diagnóstico']
  return early.includes(estagio)
}

function opport_is_mid(estagio) {
  const mid = ['Proposta', 'Negociação']
  return mid.includes(estagio)
}

function opport_is_late(estagio) {
  const late = ['Fechamento', 'Ganho', 'Perdido']
  return late.includes(estagio)
}
</script>
