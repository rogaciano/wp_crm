<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Contatos</h1>
      <button @click="openModal()" class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Contato</button>
    </div>

    <!-- Cards de Estatísticas/Filtros por Tipo -->
    <div class="flex flex-nowrap gap-3 overflow-x-auto pb-1 -mb-1">
      <!-- Card Total -->
      <div
        @click="filterByTipo(undefined)"
        :class="['card cursor-pointer transition-all duration-200 hover:shadow-lg border-2 py-3 px-4 flex-shrink-0 min-w-[140px]', selectedTipo === undefined && !hasActiveExtraFilters ? 'border-primary-500 bg-primary-50' : 'border-transparent hover:border-gray-300']"
      >
        <div class="flex items-center justify-between gap-3 font-outfit">
          <div class="min-w-0">
            <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Total</p>
            <p class="text-2xl font-black text-gray-900">{{ stats.total }}</p>
          </div>
          <div class="h-10 w-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-100">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Cards por Tipo -->
      <div
        v-for="(tipo, index) in stats.por_tipo"
        :key="tipo.id || 'sem-tipo'"
        @click="filterByTipo(tipo.id)"
        :class="['card cursor-pointer transition-all duration-200 hover:shadow-lg border-2 py-3 px-4 flex-shrink-0 min-w-[140px]', selectedTipo === tipo.id ? 'border-teal-500 bg-teal-50' : 'border-transparent hover:border-gray-300']"
      >
        <div class="flex items-center justify-between gap-3 font-outfit">
          <div class="min-w-0">
            <p
              class="text-[10px] font-black text-gray-400 uppercase tracking-widest truncate max-w-[80px]"
              :title="tipo.nome"
            >{{ tipo.nome }}</p>
            <p class="text-2xl font-black text-gray-900">{{ tipo.total }}</p>
          </div>
          <div
            :class="['h-10 w-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0 shadow-lg shadow-gray-100', getTipoColor(index)]"
          >
            {{ tipo.emoji || '👤' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros Avançados -->
    <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm flex flex-wrap items-end gap-4 shadow-xl shadow-gray-100/50">
      <div class="w-full sm:flex-1 sm:min-w-[200px]">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Busca Rápida</label>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Pesquisar..."
            class="input pl-10 h-11"
            @input="debouncedSearch"
          />
          <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
            <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="w-full sm:w-44 md:w-48">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Empresa</label>
        <select v-model="selectedConta" class="input h-11" @change="loadContatos(1)">
          <option :value="undefined">Todas</option>
          <option v-for="c in todasContas" :key="c.id" :value="c.id">{{ c.nome_empresa }}</option>
        </select>
      </div>

      <div class="w-full sm:w-40 md:w-44">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Tag</label>
        <select v-model="selectedTag" class="input h-11" @change="loadContatos(1)">
          <option :value="undefined">Todas Tags</option>
          <option v-for="tag in todasTags" :key="tag.id" :value="tag.id">{{ tag.nome }}</option>
        </select>
      </div>

      <div class="w-full sm:w-40 md:w-44">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Responsável</label>
        <select v-model="selectedProprietario" class="input h-11" @change="loadContatos(1)">
          <option :value="undefined">Todos</option>
          <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.nome_completo || u.username }}</option>
        </select>
      </div>

      <div class="w-full sm:w-40 md:w-44">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Canal</label>
        <select v-model="selectedCanal" class="input h-11" @change="loadContatos(1)">
          <option :value="undefined">Todos Canais</option>
          <option v-for="c in todosCanais" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </div>

      <div class="w-full sm:w-44 md:w-52">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Situação Comercial</label>
        <select v-model="selectedSituacaoComercial" class="input h-11" @change="loadContatos(1)">
          <option :value="undefined">Todas</option>
          <option value="PROSPECT">Oportunidade</option>
          <option value="CLIENTE_ATIVO">Cliente Ativo</option>
          <option value="INATIVO">Ex-cliente</option>
          <option value="UPGRADE">Cliente com Upgrade</option>
        </select>
      </div>

      <button v-if="hasActiveFilters" @click="clearFilters" class="h-11 px-4 text-gray-400 hover:text-red-500 font-bold text-xs truncate transition-colors">
        Limpar Filtros
      </button>
    </div>

    <div class="card overflow-hidden border-none shadow-xl shadow-gray-100">
      <div v-if="loading" class="text-center py-24">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-100 border-b-primary-600"></div>
        <p class="mt-4 text-gray-400 font-bold uppercase text-[10px] tracking-widest">Carregando contatos...</p>
      </div>

      <div v-else>
        <!-- Desktop Table -->
        <div class="hidden md:block overflow-x-auto">
          <table class="table w-full">
            <thead class="bg-gray-50/50">
              <tr>
                <th class="table-header min-w-[200px]">Identificação</th>
                <th class="table-header min-w-[160px]">Contato</th>
                <th class="table-header min-w-[150px]">Empresa</th>
                <th class="table-header min-w-[140px]">Opp / Tags</th>
                <th class="table-header min-w-[100px]">Origem</th>
                <th class="table-header text-right min-w-[80px]">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-50">
              <tr v-for="contato in contatos" :key="contato.id" class="hover:bg-primary-50/30 transition-colors group">
                <td class="table-cell">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center font-black text-gray-400 shadow-sm transition-transform group-hover:scale-110">
                      {{ contato.nome.charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <div 
                        @click="viewContato(contato.id)"
                        class="font-black text-gray-800 hover:text-primary-600 cursor-pointer transition-colors"
                      >
                        {{ contato.nome }}
                      </div>
                      <div class="text-[10px] text-gray-400 font-bold uppercase tracking-tighter mt-0.5">
                        {{ contato.cargo || 'Sem Cargo' }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="table-cell text-gray-500">
                  <div v-if="contato.email" class="flex items-center gap-1.5 mb-1 group-link">
                    <svg class="w-3.5 h-3.5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                    <a :href="`mailto:${contato.email}`" class="text-xs hover:text-primary-600 truncate max-w-[160px]">{{ contato.email }}</a>
                  </div>
                  <div class="flex items-center gap-1.5 text-[11px] font-bold">
                    <svg class="w-3.5 h-3.5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                    {{ contato.celular_formatado || contato.telefone_formatado || 'Sem telefone' }}
                  </div>
                </td>
                <td class="table-cell">
                  <div v-if="contato.conta_nome">
                    <button 
                      @click="router.push(`/contas/${contato.conta}`)"
                      class="text-xs font-black text-gray-700 hover:text-primary-600 flex items-center gap-1.5"
                    >
                      <svg class="w-3.5 h-3.5 opacity-30" fill="currentColor" viewBox="0 0 24 24"><path d="M21 13v10h-6v-6h-6v6h-6v-10l9-9z"/></svg>
                      {{ contato.conta_nome }}
                    </button>
                  </div>
                  <div v-else class="text-[10px] text-gray-300 font-bold uppercase">Particular</div>
                </td>
                <td class="table-cell">
                  <div class="flex items-center gap-4">
                    <div class="flex flex-col items-center" v-if="contato.oportunidades?.length">
                      <span class="text-xs font-black text-primary-600">{{ contato.oportunidades.length }}</span>
                      <span class="text-[8px] font-black uppercase text-gray-300 tracking-tighter">Opps</span>
                    </div>
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-for="tag in contato.tags_detail?.slice(0, 2)" :key="tag.id"
                        class="px-1.5 py-0.5 rounded bg-gray-100 text-[9px] font-bold text-gray-500 uppercase"
                      >
                        {{ tag.nome }}
                      </span>
                      <span v-if="contato.tags_detail?.length > 2" class="text-[9px] font-black text-gray-300">+{{ contato.tags_detail.length - 2 }}</span>
                    </div>
                  </div>
                </td>
                <td class="table-cell">
                   <div v-if="contato.tipo_contato_nome" class="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-50 text-[10px] font-black text-gray-600 uppercase">
                     <span>{{ contato.tipo_contato_emoji }}</span>
                     {{ contato.tipo_contato_nome }}
                   </div>
                   <div class="text-[9px] text-gray-400 font-bold mt-1 flex items-center gap-1">
                     <span class="w-1 h-1 rounded-full bg-gray-200"></span>
                     {{ contato.canal_nome || 'Sem Canal' }}
                   </div>
                </td>
                 <td class="table-cell text-right">
                   <div class="flex justify-end gap-1">
                     <button @click.stop="openWhatsapp(contato)" class="p-2 text-emerald-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg" title="WhatsApp">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
                     </button>
                     <button @click.stop="openModal(contato)" class="p-2 text-gray-400 hover:text-primary-600" title="Editar">
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                     </button>
                     <button @click.stop="deleteContato(contato.id)" class="p-2 text-gray-400 hover:text-red-500" title="Excluir">
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                     </button>
                   </div>
                 </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Logic -->
        <div class="md:hidden divide-y divide-gray-50">
          <div v-for="contato in contatos" :key="contato.id" class="p-4" @click="viewContato(contato.id)">
             <div class="flex items-start justify-between">
                <div class="flex gap-3">
                   <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center font-black text-gray-400 text-sm">
                     {{ contato.nome.charAt(0) }}
                   </div>
                   <div>
                     <h4 class="font-black text-gray-800">{{ contato.nome }}</h4>
                     <p class="text-[10px] font-black text-gray-400 uppercase tracking-tighter">{{ contato.conta_nome || 'Particular' }}</p>
                   </div>
                </div>
                <div v-if="contato.tipo_contato_emoji" class="text-xl">{{ contato.tipo_contato_emoji }}</div>
             </div>
             <div class="mt-3 flex items-center justify-between gap-2">
                <div class="flex flex-wrap gap-1">
                  <span v-for="tag in contato.tags_detail" :key="tag.id" class="px-1.5 py-0.5 rounded-md bg-gray-50 text-[8px] font-black text-gray-400 uppercase">{{ tag.nome }}</span>
                </div>
                <button @click.stop="openWhatsapp(contato)" class="flex-shrink-0 text-emerald-500 hover:text-emerald-600 hover:bg-emerald-50 p-1.5 rounded-lg" title="WhatsApp">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
                </button>
             </div>
          </div>
        </div>

        <div v-if="contatos.length === 0" class="text-center py-24">
          <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
          <p class="text-gray-400 font-bold uppercase text-[10px] tracking-widest">Nenhum registro encontrado</p>
        </div>
      </div>

      <!-- Paginação -->
      <div v-if="pagination.count > 0" class="border-t border-gray-50 px-6 py-4">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest">
            Exibindo <span class="text-gray-900">{{ Math.min(pagination.count, (pagination.currentPage) * pagination.pageSize) }}</span> de <span class="text-gray-900">{{ pagination.count }}</span>
          </div>

          <div class="flex items-center space-x-1">
            <button
              @click="goToPage(pagination.currentPage - 1)"
              :disabled="!pagination.previous"
              class="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            </button>
            <div class="flex items-center">
               <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="['w-9 h-9 rounded-lg text-xs font-black transition-all',
                         page === pagination.currentPage
                           ? 'bg-primary-600 text-white shadow-lg shadow-primary-200 scale-110'
                           : 'text-gray-400 hover:bg-gray-100']"
              >
                {{ page }}
              </button>
            </div>
            <button
              @click="goToPage(pagination.currentPage + 1)"
              :disabled="!pagination.next"
              class="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <ContatoModal
      :show="showModal"
      :contato="selectedContato"
      @close="showModal = false"
      @saved="handleContatoSaved"
    />

    <!-- WhatsApp -->
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
import { useRouter } from 'vue-router'
import api from '@/services/api'
import ContatoModal from '@/components/ContatoModal.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'

const router = useRouter()

const contatos = ref([])
const searchQuery = ref('')
const showModal = ref(false)
const selectedContato = ref(null)
const loading = ref(false)

const showWhatsapp = ref(false)
const whatsappData = ref({ number: '', title: '', oportunidade: null })
const stats = ref({ total: 0, por_tipo: [], por_canal: [] })

const selectedTipo = ref(undefined)
const selectedCanal = ref(undefined)
const selectedTag = ref(undefined)
const selectedProprietario = ref(undefined)
const selectedConta = ref(undefined)
const selectedSituacaoComercial = ref(undefined)

const todasTags = ref([])
const todosCanais = ref([])
const usuarios = ref([])
const todasContas = ref([])

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 10,
  totalPages: 0
})

const hasActiveFilters = computed(() => {
  return selectedTipo.value !== undefined || 
         selectedCanal.value !== undefined || 
         selectedTag.value !== undefined || 
         selectedProprietario.value !== undefined ||
         selectedConta.value !== undefined ||
         selectedSituacaoComercial.value !== undefined ||
         searchQuery.value !== ''
})

const hasActiveExtraFilters = computed(() => {
  return selectedCanal.value !== undefined || 
         selectedTag.value !== undefined || 
         selectedProprietario.value !== undefined ||
         selectedConta.value !== undefined ||
         selectedSituacaoComercial.value !== undefined
})

const tipoColors = [
  'bg-purple-50 text-purple-600',
  'bg-emerald-50 text-emerald-600',
  'bg-amber-50 text-amber-600',
  'bg-rose-50 text-rose-600',
  'bg-indigo-50 text-indigo-600',
  'bg-cyan-50 text-cyan-600',
]

const visiblePages = computed(() => {
  const total = pagination.value.totalPages
  const current = pagination.value.currentPage
  const pages = []
  if (total <= 0) return []
  let start = Math.max(1, current - 2)
  let end = Math.min(total, start + 4)
  if (end === total) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) {
    if (i >= 1) pages.push(i)
  }
  return pages
})

onMounted(async () => {
  await Promise.all([
    loadEstatisticas(),
    loadOptions(),
    loadContatos()
  ])
})

async function loadOptions() {
  try {
    const [tRes, cRes, uRes, accRes] = await Promise.all([
      api.get('/tags/'),
      api.get('/canais/'),
      api.get('/usuarios/'),
      api.get('/contas/')
    ])
    todasTags.value = tRes.data.results || tRes.data
    todosCanais.value = cRes.data.results || cRes.data
    usuarios.value = uRes.data.results || uRes.data
    todasContas.value = accRes.data.results || accRes.data
  } catch (err) { console.error(err) }
}

async function loadEstatisticas() {
  try {
    const response = await api.get('/contatos/estatisticas/')
    stats.value = response.data
  } catch (error) { console.error(error) }
}

async function loadContatos(page = 1) {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      page: page,
      page_size: pagination.value.pageSize
    }

    if (selectedTipo.value !== undefined) {
      params.tipo_contato = selectedTipo.value === 'null' ? '' : selectedTipo.value
    }
    if (selectedCanal.value !== undefined) params.canal = selectedCanal.value
    if (selectedTag.value !== undefined) params.tags = selectedTag.value
    if (selectedProprietario.value !== undefined) params.proprietario = selectedProprietario.value
    if (selectedConta.value !== undefined) params.conta = selectedConta.value
    if (selectedSituacaoComercial.value === 'UPGRADE') {
      params.apenas_upgrade = true
    } else if (selectedSituacaoComercial.value !== undefined) {
      params.conta_status_cliente = selectedSituacaoComercial.value
    }

    const response = await api.get('/contatos/', { params })
    if (response.data.results) {
      contatos.value = response.data.results
      pagination.value.count = response.data.count
      pagination.value.next = response.data.next
      pagination.value.previous = response.data.previous
      pagination.value.currentPage = page
      pagination.value.totalPages = Math.ceil(response.data.count / pagination.value.pageSize)
    }
  } catch (error) {
    console.error('Erro ao carregar contatos:', error)
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
function debouncedSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadContatos(1)
  }, 300)
}

function goToPage(page) {
  if (page >= 1 && page <= pagination.value.totalPages) {
    loadContatos(page)
  }
}

function getTipoColor(index) {
  return tipoColors[index % tipoColors.length]
}

function filterByTipo(tipoId) {
  selectedTipo.value = tipoId
  loadContatos(1)
}

function clearFilters() {
  selectedTipo.value = undefined
  selectedCanal.value = undefined
  selectedTag.value = undefined
  selectedProprietario.value = undefined
  selectedConta.value = undefined
  selectedSituacaoComercial.value = undefined
  searchQuery.value = ''
  loadContatos(1)
}

function openModal(contato = null) {
  selectedContato.value = contato
  showModal.value = true
}

function handleContatoSaved() {
  loadContatos(pagination.value.currentPage)
  loadEstatisticas()
}

function viewContato(id) {
  router.push(`/contatos/${id}`)
}

async function deleteContato(id) {
  if (!confirm('Excluir este contato permanentemente?')) return
  try {
    await api.delete(`/contatos/${id}/`)
    loadContatos(pagination.value.currentPage)
    loadEstatisticas()
  } catch (error) {
    console.error(error)
    alert('Erro ao excluir contato')
  }
}

function openWhatsapp(contato) {
  const phone = contato.celular || contato.telefone
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
</script>

<style scoped>
.font-outfit { font-family: 'Outfit', sans-serif; }
.btn { @apply px-5 py-2.5 rounded-xl font-black text-xs uppercase tracking-widest transition-all active:scale-95 shadow-sm; }
.btn-primary { @apply bg-primary-600 text-white hover:bg-primary-700 shadow-primary-200; }
.input { @apply w-full px-4 py-2.5 rounded-xl border border-gray-100 bg-gray-50/50 focus:bg-white focus:border-primary-500 focus:ring-4 focus:ring-primary-50 transition-all outline-none text-sm font-bold; }
.card { @apply bg-white p-5 rounded-3xl border border-gray-100; }
.table-header { @apply px-6 py-4 text-left text-[10px] font-black text-gray-400 uppercase tracking-widest; }
.table-cell { @apply px-6 py-4 text-sm text-gray-600; }
</style>
