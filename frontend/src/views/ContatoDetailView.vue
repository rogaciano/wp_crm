<template>
  <div class="space-y-6">
    <!-- Header com nome e ações -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div class="flex flex-col md:flex-row md:items-center gap-6">
        <!-- Foto/Avatar -->
        <div class="flex-shrink-0">
          <img 
            v-if="contato?.foto_url" 
            :src="contato.foto_url" 
            class="w-24 h-24 rounded-full object-cover ring-4 ring-primary-100 shadow-lg"
          />
          <div 
            v-else 
            class="w-24 h-24 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-3xl shadow-lg"
          >
            {{ contato?.nome?.charAt(0)?.toUpperCase() || '?' }}
          </div>
        </div>
        
        <!-- Info principal -->
        <div class="flex-1">
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900">{{ contato?.nome }}</h1>
          <p v-if="contato?.cargo" class="text-gray-500 mt-1">{{ contato.cargo }}</p>
          
          <!-- Tags -->
          <div v-if="contato?.tags_detail?.length" class="flex flex-wrap gap-2 mt-3">
            <span 
              v-for="tag in contato.tags_detail" 
              :key="tag.id"
              class="px-3 py-1 text-xs font-medium rounded-full text-white"
              :style="{ backgroundColor: tag.cor }"
            >
              {{ tag.nome }}
            </span>
          </div>
        </div>
        
        <!-- Ações -->
        <div class="flex gap-2">
          <button 
            @click="editarContato"
            class="btn btn-primary flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
            </svg>
            Editar
          </button>
          <button 
            v-if="telefonePrincipal"
            @click="abrirWhatsapp"
            class="btn bg-emerald-500 hover:bg-emerald-600 text-white flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751z"/>
            </svg>
            WhatsApp
          </button>
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Coluna esquerda: Informações -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Dados de contato -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            Dados de Contato
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Telefones -->
            <div v-if="contato?.telefones?.length">
              <p class="text-sm font-medium text-gray-500 mb-2">Telefones</p>
              <div class="space-y-2">
                <div v-for="tel in contato.telefones" :key="tel.id" class="flex items-center gap-2">
                  <span class="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">{{ tel.tipo_display }}</span>
                  <span class="text-gray-900">{{ tel.numero }}</span>
                  <span v-if="tel.principal" class="text-xs text-primary-500 font-medium">Principal</span>
                </div>
              </div>
            </div>
            
            <!-- Emails -->
            <div v-if="contato?.emails?.length">
              <p class="text-sm font-medium text-gray-500 mb-2">E-mails</p>
              <div class="space-y-2">
                <div v-for="email in contato.emails" :key="email.id" class="flex items-center gap-2">
                  <span class="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">{{ email.tipo_display }}</span>
                  <a :href="'mailto:' + email.email" class="text-primary-600 hover:underline">{{ email.email }}</a>
                  <span v-if="email.principal" class="text-xs text-primary-500 font-medium">Principal</span>
                </div>
              </div>
            </div>
            
            <!-- Cargo/Departamento -->
            <div v-if="contato?.cargo || contato?.departamento">
              <p class="text-sm font-medium text-gray-500 mb-2">Cargo / Departamento</p>
              <p class="text-gray-900">{{ contato.cargo || '-' }} / {{ contato.departamento || '-' }}</p>
            </div>
            
            <!-- Chave PIX -->
            <div v-if="contato?.chave_pix">
              <p class="text-sm font-medium text-gray-500 mb-2">Chave PIX</p>
              <p class="text-gray-900 font-mono text-sm">{{ contato.chave_pix }}</p>
            </div>
          </div>
        </div>
        
        <!-- Oportunidades vinculadas -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
              <svg class="w-6 h-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              Oportunidades
            </h2>
            <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-bold">
              {{ contato?.oportunidades?.length || 0 }}
            </span>
          </div>
          
          <div v-if="contato?.oportunidades?.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="opp in contato.oportunidades" 
              :key="opp.id"
              class="group p-4 bg-gray-50 rounded-xl hover:bg-white border border-transparent hover:border-emerald-200 hover:shadow-lg transition-all cursor-pointer"
              @click="irParaOportunidade(opp.id)"
            >
              <div class="flex justify-between items-start mb-2">
                <span 
                  class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider"
                  :style="{ backgroundColor: opp.estagio_cor + '20', color: opp.estagio_cor }"
                >
                  {{ opp.estagio_nome }}
                </span>
                <span class="text-xs font-bold text-gray-400">{{ formatDate(opp.data_atualizacao) }}</span>
              </div>
              
              <h4 class="font-bold text-gray-900 mb-2 truncate group-hover:text-emerald-600">{{ opp.nome }}</h4>
              
              <div class="flex justify-between items-end">
                <p class="text-lg font-black text-emerald-600">
                  R$ {{ Number(opp.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </p>
                <div class="p-1 rounded bg-white shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                  <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 bg-gray-50 rounded-xl border border-dashed border-gray-200">
             <p class="text-gray-400 text-sm italic">Nenhuma oportunidade vinculada a este contato.</p>
          </div>
        </div>
        
        <!-- Timeline Unificada (Notas, Tarefas, WhatsApp, Logs) -->
        <div v-if="contato" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden min-h-[500px] flex flex-col">
          <TimelineFeed 
            model="contato" 
            :id="contato.id" 
            @action="handleTimelineAction" 
          />
        </div>
      </div>
      
      <!-- Coluna direita: Empresa e Redes Sociais -->
      <div class="space-y-6">
        <!-- Empresa -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
            Empresa
          </h2>
          
          <div 
            v-if="contato?.conta"
            @click="irParaEmpresa"
            class="p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg hover:from-indigo-100 hover:to-purple-100 cursor-pointer transition-colors"
          >
            <h3 class="font-semibold text-gray-900">{{ contato.conta_nome }}</h3>
            <p v-if="contato.conta_cnpj" class="text-sm text-gray-500 mt-1">CNPJ: {{ contato.conta_cnpj }}</p>
          </div>
        </div>
        
        <!-- Redes Sociais -->
        <div v-if="contato?.redes_sociais?.length" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-pink-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            Redes Sociais
          </h2>
          
          <div class="space-y-3">
            <a 
              v-for="rede in contato.redes_sociais" 
              :key="rede.id"
              :href="rede.url_completa"
              target="_blank"
              class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <span class="text-2xl" v-html="sanitizeHtml(rede.tipo_icone)"></span>
              <span class="text-gray-700">{{ rede.valor }}</span>
            </a>
          </div>
        </div>
        
        <!-- Responsável -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Responsável
          </h2>
          
          <p class="text-gray-900 font-medium">{{ contato?.proprietario_nome || 'Não definido' }}</p>
          <p v-if="contato?.canal_nome" class="text-sm text-gray-500 mt-1">Canal: {{ contato.canal_nome }}</p>
        </div>
        
        <!-- Auditoria -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-sm font-semibold text-gray-500 mb-3">Informações do Registro</h2>
          
          <div class="space-y-2 text-xs text-gray-500">
            <p>Criado em: {{ formatDateTime(contato?.data_criacao) }}</p>
            <p v-if="contato?.criado_por_nome">Por: {{ contato.criado_por_nome }}</p>
            <p class="mt-2">Atualizado em: {{ formatDateTime(contato?.data_atualizacao) }}</p>
            <p v-if="contato?.atualizado_por_nome">Por: {{ contato.atualizado_por_nome }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal de edição -->
    <ContatoModal
      :show="showEditModal"
      :contato="contato"
      @close="showEditModal = false"
      @saved="handleSaved"
    />

    <WhatsappChat
      :show="showWhatsapp"
      :number="whatsappData.number"
      :title="whatsappData.title"
      :oportunidade="whatsappData.oportunidade"
      @close="showWhatsapp = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import ContatoModal from '@/components/ContatoModal.vue'
import TimelineFeed from '@/components/TimelineFeed.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'
import { sanitizeHtml } from '@/utils/sanitize'

const route = useRoute()
const router = useRouter()

const contato = ref(null)
const loading = ref(false)
const showEditModal = ref(false)
const showWhatsapp = ref(false)
const whatsappData = ref({ number: '', title: '', oportunidade: null })

const telefonePrincipal = computed(() => {
  if (!contato.value?.telefones?.length) return null
  const principal = contato.value.telefones.find(t => t.principal)
  return principal?.numero || contato.value.telefones[0]?.numero
})

onMounted(() => {
  loadContato()
})

async function loadContato() {
  loading.value = true
  try {
    const id = route.params.id
    const response = await api.get(`/contatos/${id}/`)
    contato.value = response.data
  } catch (error) {
    console.error('Erro ao carregar contato:', error)
  } finally {
    loading.value = false
  }
}

function editarContato() {
  showEditModal.value = true
}

async function handleSaved() {
  showEditModal.value = false
  await loadContato()
}

function irParaEmpresa() {
  if (contato.value?.conta) {
    router.push(`/contas/${contato.value.conta}`)
  }
}

function abrirWhatsapp() {
  if (!telefonePrincipal.value) return
  
  let cleanNumber = telefonePrincipal.value.replace(/\D/g, '')
  if (!cleanNumber.startsWith('55') && cleanNumber.length <= 11) {
    cleanNumber = '55' + cleanNumber
  }
  
  whatsappData.value = { number: cleanNumber, title: contato.value?.nome || '', oportunidade: null }
  showWhatsapp.value = true
}

function handleTimelineAction(action) {
  if (action === 'whatsapp') {
    abrirWhatsapp()
    return
  }
}

function irParaOportunidade(id) {
  router.push(`/kanban`) // Por enquanto volta pro kanban, ou se tiver rota de detalhe de oportunidade...
  // TODO: Se houver OportunidadeDetailView, navegar para lá.
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR')
}

function formatDateTime(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
