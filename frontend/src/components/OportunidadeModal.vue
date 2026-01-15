<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Oportunidade' : 'Nova Oportunidade'"
    size="xl"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Coluna Principal (Formulário) -->
      <form @submit.prevent="handleSubmit" class="lg:col-span-2 space-y-8">
        <!-- Informações Básicas -->
        <section class="bg-gray-50/50 p-6 rounded-2xl border border-gray-100">
          <h3 class="text-xs font-black text-primary-600 uppercase tracking-[0.2em] mb-6 flex items-center">
            <span class="w-8 h-px bg-primary-200 mr-3"></span>
            Informações Básicas
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2">
              <label class="block text-sm font-bold text-gray-700 mb-1.5">
                Nome da Oportunidade <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.nome"
                type="text"
                required
                class="input focus:ring-primary-500"
                placeholder="Ex: Venda de Sistema - Empresa XYZ"
              />
            </div>

            <div class="relative">
              <label class="block text-sm font-bold text-gray-700 mb-1.5 flex justify-between">
                <span>Empresa Principal <span class="text-red-500">*</span></span>
                <button type="button" @click="showNovaEmpresaModal = true" class="text-primary-600 hover:text-primary-700 text-[10px] font-black uppercase tracking-wider">+ Nova Empresa</button>
              </label>
              
              <div class="relative group">
                <input 
                  v-model="searchContaPrincipal" 
                  type="text" 
                  class="input pl-10 pr-10" 
                  placeholder="Buscar empresa..."
                  @focus="showContasPrincipalDropdown = true"
                >
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <button v-if="form.conta" @click="form.conta = null; searchContaPrincipal = ''" type="button" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg class="h-4 w-4 text-gray-400 hover:text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <div v-if="showContasPrincipalDropdown && filteredContasPrincipal.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-60 overflow-y-auto custom-scrollbar">
                  <div 
                    v-for="c in filteredContasPrincipal" :key="c.id"
                    @click="selectContaPrincipal(c)"
                    class="p-3 hover:bg-primary-50 cursor-pointer border-b border-gray-50 last:border-0 transition-colors"
                  >
                    <div class="font-bold text-gray-900 text-sm">{{ c.nome_empresa }}</div>
                    <div class="text-[10px] text-gray-500">{{ c.cnpj || 'Sem CNPJ' }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="relative">
              <label class="block text-sm font-bold text-gray-700 mb-1.5 flex justify-between">
                <span>Contato Principal</span>
                <button type="button" @click="showNovoContatoModal = true" class="text-primary-600 hover:text-primary-700 text-[10px] font-black uppercase tracking-wider">+ Novo Contato</button>
              </label>
              
              <div class="relative group">
                <input 
                  v-model="searchContatoPrincipal" 
                  type="text" 
                  class="input pl-10 pr-10 disabled:bg-gray-50" 
                  :placeholder="form.conta ? 'Buscar contato...' : 'Selecione uma empresa primeiro'"
                  :disabled="!form.conta"
                  @focus="showContatosPrincipalDropdown = true"
                >
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <button v-if="form.contato_principal" @click="form.contato_principal = null; searchContatoPrincipal = ''" type="button" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg class="h-4 w-4 text-gray-400 hover:text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <div v-if="showContatosPrincipalDropdown && filteredContatosPrincipal.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-60 overflow-y-auto custom-scrollbar">
                  <div 
                    v-for="c in filteredContatosPrincipal" :key="c.id"
                    @click="selectContatoPrincipal(c)"
                    class="p-3 hover:bg-primary-50 cursor-pointer border-b border-gray-50 last:border-0 transition-colors"
                  >
                    <div class="font-bold text-gray-900 text-sm">{{ c.nome }}</div>
                    <div class="text-[10px] text-gray-500">{{ c.email || 'Sem e-mail' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Funções e Estágios -->
        <section class="bg-gray-50/50 p-6 rounded-2xl border border-gray-100">
          <h3 class="text-xs font-black text-indigo-600 uppercase tracking-[0.2em] mb-6 flex items-center">
            <span class="w-8 h-px bg-indigo-200 mr-3"></span>
            Funil e Estágio
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Funil</label>
              <select v-model="form.funil" required class="input">
                <option :value="null">Selecione o funil...</option>
                <option v-for="f in funis" :key="f.id" :value="f.id">{{ f.nome }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Estágio</label>
              <select v-model="form.estagio" required class="input" :disabled="!form.funil">
                <option v-for="e in estagios" :key="e.id" :value="e.id">{{ e.nome }}</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Valores e Datas -->
        <section class="bg-gray-50/50 p-6 rounded-2xl border border-gray-100">
          <h3 class="text-xs font-black text-emerald-600 uppercase tracking-[0.2em] mb-6 flex items-center">
            <span class="w-8 h-px bg-emerald-200 mr-3"></span>
            Valores e Previsão
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Valor Estimado (R$)</label>
              <input v-model.number="form.valor_estimado" type="number" step="0.01" class="input" placeholder="0,00" />
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Probabilidade (%)</label>
              <input v-model.number="form.probabilidade" type="number" min="0" max="100" class="input" />
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Fechamento Esperado</label>
              <input v-model="form.data_fechamento_esperada" type="date" class="input" />
            </div>
          </div>
        </section>

        <!-- Relações Adicionais (M2M) -->
        <section class="bg-gray-50/50 p-6 rounded-2xl border border-gray-100">
          <h3 class="text-xs font-black text-amber-600 uppercase tracking-[0.2em] mb-6 flex items-center">
            <span class="w-8 h-px bg-amber-200 mr-3"></span>
            Pessoas e Empresas Envolvidas
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- M2M Contatos -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-3">Contatos Extras</label>
              <div class="relative mb-4">
                <input 
                  v-model="searchM2MContato" 
                  type="text" 
                  class="input text-xs" 
                  placeholder="Buscar contato para vincular..."
                  @focus="showM2MContatosDropdown = true"
                >
                <div v-if="showM2MContatosDropdown && filteredM2MContatos.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-48 overflow-y-auto">
                  <div 
                    v-for="c in filteredM2MContatos" :key="c.id"
                    @click="addContatoM2M(c)"
                    class="p-2 hover:bg-primary-50 cursor-pointer border-b border-gray-50 text-xs"
                  >
                    {{ c.nome }} <span class="text-gray-400">({{ c.conta_nome || 'S/ Empresa' }})</span>
                  </div>
                </div>
              </div>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="cId in form.contatos" :key="cId"
                  class="inline-flex items-center px-2.5 py-1.5 rounded-lg bg-white border border-gray-100 text-xs font-bold text-gray-700 shadow-sm"
                >
                  {{ getContatoNome(cId) }}
                  <button type="button" @click="removeContatoM2M(cId)" class="ml-2 text-gray-400 hover:text-red-500">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </span>
              </div>
            </div>

            <!-- M2M Empresas -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-3">Empresas Extras</label>
              <div class="relative mb-4">
                <input 
                  v-model="searchM2MEmpresa" 
                  type="text" 
                  class="input text-xs" 
                  placeholder="Buscar empresa para vincular..."
                  @focus="showM2MEmpresasDropdown = true"
                >
                <div v-if="showM2MEmpresasDropdown && filteredM2MEmpresas.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-48 overflow-y-auto">
                  <div 
                    v-for="c in filteredM2MEmpresas" :key="c.id"
                    @click="addEmpresaM2M(c)"
                    class="p-2 hover:bg-primary-50 cursor-pointer border-b border-gray-50 text-xs"
                  >
                    {{ c.nome_empresa }}
                  </div>
                </div>
              </div>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="eId in form.empresas" :key="eId"
                  class="inline-flex items-center px-2.5 py-1.5 rounded-lg bg-white border border-gray-100 text-xs font-bold text-gray-700 shadow-sm"
                >
                  {{ getEmpresaNome(eId) }}
                  <button type="button" @click="removeEmpresaM2M(eId)" class="ml-2 text-gray-400 hover:text-red-500">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Observações -->
        <section>
          <label class="block text-sm font-bold text-gray-700 mb-1.5">Detalhamento / Contexto</label>
          <textarea v-model="form.descricao" rows="4" class="input" placeholder="Anote aqui informações importantes da negociação..."></textarea>
        </section>
      </form>

      <!-- Coluna Lateral (Informações Rápidas, Anexos e Diagnósticos) -->
      <aside class="space-y-6">
        <!-- Status Card -->
        <div v-if="isEdit" class="bg-primary-600 rounded-2xl p-6 text-white shadow-xl shadow-primary-100">
          <div class="text-[10px] font-black uppercase tracking-[0.2em] opacity-80 mb-2">Responsável</div>
          <div class="flex items-center gap-3">
             <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center font-bold">{{ props.oportunidade?.proprietario_nome?.charAt(0) }}</div>
             <div>
               <div class="font-bold">{{ props.oportunidade?.proprietario_nome }}</div>
               <div class="text-[10px] opacity-70">{{ props.oportunidade?.canal_nome }}</div>
             </div>
          </div>
        </div>

        <!-- Seção de Anexos -->
        <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h4 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-4 flex justify-between items-center">
            Anexos
            <label class="cursor-pointer text-primary-600 hover:text-primary-700 font-black tracking-normal">
              <input type="file" class="hidden" @change="handleFileUpload" multiple>
              + Adicionar
            </label>
          </h4>
          
          <div v-if="anexos.length > 0" class="space-y-3">
            <div v-for="anexo in anexos" :key="anexo.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-xl group hover:bg-white border border-transparent hover:border-gray-100 transition-all">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-8 h-8 rounded-lg bg-white flex items-center justify-center shadow-sm">
                  <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                </div>
                <div class="min-w-0">
                  <div class="text-xs font-bold text-gray-700 truncate" :title="anexo.nome">{{ anexo.nome }}</div>
                  <div class="text-[9px] text-gray-400">{{ formatDateShort(anexo.data_upload) }}</div>
                </div>
              </div>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <a :href="anexo.arquivo" target="_blank" class="p-1.5 text-gray-400 hover:text-primary-600"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg></a>
                <button type="button" @click="deleteAnexo(anexo.id)" class="p-1.5 text-gray-400 hover:text-red-500"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-6 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
             <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-loose">Sem arquivos</p>
          </div>
        </div>

        <!-- Diagnósticos de Maturidade -->
        <div v-if="diagnosticos.length > 0" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h4 class="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4">Maturidade (Diagnóstico)</h4>
          <div class="space-y-4">
            <div v-for="diag in diagnosticos" :key="diag.id" class="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 relative group overflow-hidden">
               <div class="flex justify-between items-center mb-3">
                 <span class="text-[10px] font-black text-indigo-600 uppercase">{{ formatDateShort(diag.data_conclusao) }}</span>
                 <button @click="verDiagnostico(diag)" class="text-[10px] font-black text-indigo-500 hover:underline">Ver Detalhes</button>
               </div>
               <div class="grid grid-cols-2 gap-2">
                 <div v-for="(pilar, nome) in diag.pontuacao_por_pilar" :key="nome" class="text-center">
                    <div class="text-[8px] font-black text-gray-400 uppercase truncate" :title="nome">{{ nome }}</div>
                    <div class="text-sm font-black text-indigo-600">{{ pilar.score }}</div>
                 </div>
               </div>
            </div>
          </div>
        </div>

        <!-- Histórico de Estágios -->
        <div v-if="isEdit && historico.length > 0" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
           <h4 class="text-xs font-black text-amber-400 uppercase tracking-widest mb-4">Track de Evolução</h4>
           <div class="space-y-4 relative">
             <div v-for="(item, idx) in historico.slice(0, 5)" :key="item.id" class="flex gap-3 relative">
                <div class="flex flex-col items-center">
                  <div class="w-2 h-2 rounded-full bg-amber-400"></div>
                  <div v-if="idx !== 0" class="w-px flex-1 bg-amber-100"></div>
                </div>
                <div class="pb-4 border-b border-gray-50 last:border-0 w-full">
                   <div class="text-[10px] font-black text-gray-800 tracking-tight">{{ item.nome_estagio_novo }}</div>
                   <div class="text-[8px] text-gray-400 mt-0.5">{{ formatDateShort(item.data_mudanca) }} • {{ item.usuario_nome }}</div>
                </div>
             </div>
           </div>
        </div>
      </aside>
    </div>

    <!-- Modais Auxiliares -->
    <ContaModal
      :show="showNovaEmpresaModal"
      @close="showNovaEmpresaModal = false"
      @saved="handleNovaEmpresaSaved"
    />
    <ContatoModal
      :show="showNovoContatoModal"
      :fixed-conta-id="form.conta"
      @close="showNovoContatoModal = false"
      @saved="handleNovoContatoSaved"
    />
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'
import { useOportunidadesStore } from '@/stores/oportunidades'
import { useAuthStore } from '@/stores/auth'
import ContaModal from './ContaModal.vue'
import ContatoModal from './ContatoModal.vue'

const authStore = useAuthStore()

const props = defineProps({
  show: Boolean,
  oportunidade: Object,
  fixedContaId: [Number, String],
  fixedFunilId: [Number, String],
  fixedEstagioId: [Number, String]
})

const emit = defineEmits(['close', 'saved'])

const form = ref({
  id: null,
  nome: '',
  conta: null,
  contato_principal: null,
  funil: null,
  estagio: null,
  valor_estimado: 0,
  data_fechamento_esperada: '',
  probabilidade: 0,
  descricao: '',
  canal: null,
  indicador_comissao: null,
  fonte: '',
  contatos: [],
  empresas: []
})

const loading = ref(false)
const isEdit = ref(false)
const contas = ref([])
const contatos = ref([])
const estagios = ref([])
const canais = ref([])
const funis = ref([])
const historico = ref([])
const anexos = ref([])
const diagnosticos = ref([])

const showNovaEmpresaModal = ref(false)
const showNovoContatoModal = ref(false)

// Autocomplete Logic
const searchContaPrincipal = ref('')
const showContasPrincipalDropdown = ref(false)
const filteredContasPrincipal = computed(() => {
  if (!searchContaPrincipal.value) return contas.value.slice(0, 10)
  return contas.value.filter(c => 
    c.nome_empresa.toLowerCase().includes(searchContaPrincipal.value.toLowerCase())
  ).slice(0, 10)
})

const searchContatoPrincipal = ref('')
const showContatosPrincipalDropdown = ref(false)
const filteredContatosPrincipal = computed(() => {
  const base = form.value.conta ? contatos.value.filter(c => c.conta === form.value.conta) : contatos.value
  if (!searchContatoPrincipal.value) return base.slice(0, 10)
  return base.filter(c => 
    c.nome.toLowerCase().includes(searchContatoPrincipal.value.toLowerCase())
  ).slice(0, 10)
})

// M2M Search Logic
const searchM2MContato = ref('')
const showM2MContatosDropdown = ref(false)
const filteredM2MContatos = computed(() => {
  if (!searchM2MContato.value) return contatos.value.slice(0, 10)
  return contatos.value.filter(c => 
    c.nome.toLowerCase().includes(searchM2MContato.value.toLowerCase()) &&
    !form.value.contatos.includes(c.id)
  ).slice(0, 10)
})

const searchM2MEmpresa = ref('')
const showM2MEmpresasDropdown = ref(false)
const filteredM2MEmpresas = computed(() => {
  if (!searchM2MEmpresa.value) return contas.value.slice(0, 10)
  return contas.value.filter(c => 
    c.nome_empresa.toLowerCase().includes(searchM2MEmpresa.value.toLowerCase()) &&
    !form.value.empresas.includes(c.id)
  ).slice(0, 10)
})

function selectContaPrincipal(c) {
  form.value.conta = c.id
  searchContaPrincipal.value = c.nome_empresa
  showContasPrincipalDropdown.value = false
}

function selectContatoPrincipal(c) {
  form.value.contato_principal = c.id
  searchContatoPrincipal.value = c.nome
  showContatosPrincipalDropdown.value = false
}

function addContatoM2M(c) {
  if (!form.value.contatos.includes(c.id)) {
    form.value.contatos.push(c.id)
  }
  searchM2MContato.value = ''
  showM2MContatosDropdown.value = false
}

function removeContatoM2M(id) {
  form.value.contatos = form.value.contatos.filter(c => c !== id)
}

function addEmpresaM2M(c) {
  if (!form.value.empresas.includes(c.id)) {
    form.value.empresas.push(c.id)
  }
  searchM2MEmpresa.value = ''
  showM2MEmpresasDropdown.value = false
}

function removeEmpresaM2M(id) {
  form.value.empresas = form.value.empresas.filter(e => e !== id)
}

function getContatoNome(id) {
  return contatos.value.find(c => c.id === id)?.nome || '...'
}

function getEmpresaNome(id) {
  return contas.value.find(c => c.id === id)?.nome_empresa || '...'
}

// Watchers
watch(() => props.show, async (newVal) => {
  if (newVal) {
    await loadOptions()
    if (!isEdit.value) {
      if (props.fixedContaId) {
        form.value.conta = parseInt(props.fixedContaId)
        const c = contas.value.find(x => x.id === form.value.conta)
        if (c) searchContaPrincipal.value = c.nome_empresa
      }
      if (props.fixedFunilId) form.value.funil = parseInt(props.fixedFunilId)
      if (props.fixedEstagioId) form.value.estagio = parseInt(props.fixedEstagioId)
    }
  }
})

watch(() => form.value.funil, async (newFunil) => {
  if (newFunil) {
    try {
      const response = await api.get(`/funis/${newFunil}/estagios/`)
      const raw = response.data.results || response.data
      estagios.value = raw.map(v => ({
        id: v.estagio_id,
        nome: v.nome,
        tipo: v.tipo,
        is_padrao: v.is_padrao
      }))

      if (!isEdit.value && !form.value.estagio) {
        const defaultEstagio = estagios.value.find(e => e.is_padrao) || estagios.value[0]
        if (defaultEstagio) form.value.estagio = defaultEstagio.id
      }
    } catch (error) {
      console.error('Erro ao carregar estágios:', error)
      estagios.value = []
    }
  }
})

watch(() => props.oportunidade, async (newOp) => {
  if (newOp) {
    isEdit.value = true
    form.value = { 
       ...newOp,
       contatos: newOp.contatos || [],
       empresas: newOp.empresas || []
    }
    anexos.value = newOp.anexos || []
    diagnosticos.value = newOp.diagnosticos || []
    
    // Set search inputs
    const cp = contas.value.find(x => x.id === newOp.conta)
    if (cp) searchContaPrincipal.value = cp.nome_empresa
    
    const ctp = contatos.value.find(x => x.id === newOp.contato_principal)
    if (ctp) searchContatoPrincipal.value = ctp.nome

    // Historico
    try {
      const h = await api.get(`/oportunidades/${newOp.id}/historico_estagios/`)
      historico.value = h.data || []
    } catch (err) { console.error(err) }
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

async function loadOptions() {
  try {
    const [cRes, ctRes, fnRes, cnRes] = await Promise.all([
      api.get('/contas/'),
      api.get('/contatos/'),
      api.get('/funis/'),
      api.get('/canais/')
    ])
    contas.value = cRes.data.results || cRes.data
    contatos.value = ctRes.data.results || ctRes.data
    funis.value = (fnRes.data.results || fnRes.data).filter(f => f.tipo === 'OPORTUNIDADE')
    canais.value = cnRes.data.results || cnRes.data
  } catch (err) { console.error(err) }
}

async function handleFileUpload(event) {
  const files = event.target.files
  if (!files.length || !form.value.id) return
  
  loading.value = true
  for (const file of files) {
    const formData = new FormData()
    formData.append('arquivo', file)
    formData.append('nome', file.name)
    formData.append('oportunidade', form.value.id)

    try {
      const response = await api.post('/oportunidade-anexos/', formData)
      anexos.value.unshift(response.data)
    } catch (err) {
      console.error('Erro no upload:', err)
      alert(`Falha ao enviar ${file.name}`)
    }
  }
  loading.value = false
}

async function deleteAnexo(id) {
  if (!confirm('Excluir anexo?')) return
  try {
    await api.delete(`/oportunidade-anexos/${id}/`)
    anexos.value = anexos.value.filter(a => a.id !== id)
  } catch (err) { console.error(err) }
}

function verDiagnostico(diag) {
  localStorage.setItem('last_diagnosis_result', JSON.stringify(diag))
  window.open('/diagnostico-resultado', '_blank')
}

function resetForm() {
  form.value = {
    nome: '',
    conta: props.fixedContaId ? parseInt(props.fixedContaId) : null,
    contato_principal: null,
    funil: props.fixedFunilId ? parseInt(props.fixedFunilId) : null,
    estagio: props.fixedEstagioId ? parseInt(props.fixedEstagioId) : null,
    valor_estimado: 0,
    probabilidade: 0,
    contatos: [],
    empresas: []
  }
  searchContaPrincipal.value = ''
  searchContatoPrincipal.value = ''
  anexos.value = []
}

async function handleSubmit() {
  loading.value = true
  try {
    const payload = { ...form.value }
    // Remove null values that the API might reject if they are not expected
    if (payload.id === null) delete payload.id
    
    if (isEdit.value) {
      await api.put(`/oportunidades/${payload.id}/`, payload)
    } else {
      await api.post('/oportunidades/', payload)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (err) {
    console.error(err)
    alert('Erro ao salvar oportunidade')
  } finally { loading.value = false }
}

function formatDateShort(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

function handleNovaEmpresaSaved(conta) {
  contas.value.unshift(conta)
  selectContaPrincipal(conta)
  showNovaEmpresaModal.value = false
}

function handleNovoContatoSaved(contato) {
  contatos.value.unshift(contato)
  selectContatoPrincipal(contato)
  showNovoContatoModal.value = false
}

onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.group')) {
      showContasPrincipalDropdown.value = false
      showContatosPrincipalDropdown.value = false
      showM2MContatosDropdown.value = false
      showM2MEmpresasDropdown.value = false
    }
  })
})
</script>

<style scoped>
.input {
  @apply w-full px-4 py-3 rounded-xl border border-gray-200 bg-white shadow-sm transition-all focus:border-primary-500 focus:ring-4 focus:ring-primary-50 outline-none text-sm font-medium;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  @apply bg-transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-gray-200 rounded-full;
}
</style>
