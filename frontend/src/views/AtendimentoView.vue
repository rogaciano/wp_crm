<template>
  <div class="h-screen flex flex-col bg-gray-50 overflow-hidden">

    <!-- ─── Header ─── -->
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 shadow-sm flex-shrink-0">
      <!-- Ícone + Título -->
      <div class="flex items-center gap-2">
        <div class="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center shadow-sm">
          <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751z"/>
          </svg>
        </div>
        <div>
          <h1 class="text-sm font-bold text-gray-800 leading-none">Multiatendimento</h1>
          <p class="text-[10px] text-gray-400 mt-0.5">
            <span :class="wsStore.wsConectado ? 'text-emerald-500' : 'text-gray-300'">●</span>
            {{ wsStore.wsConectado ? 'Tempo real ativo' : 'Reconectando...' }}
          </p>
        </div>
      </div>

      <!-- Seletor de Canal (Admin) -->
      <div v-if="isAdmin && wsStore.canaisDisponiveis.length > 1" class="flex items-center gap-2">
        <span class="text-xs text-gray-400">Canal:</span>
        <select
          v-model="canalSelecionado"
          @change="mudarCanal"
          class="text-sm border border-gray-200 rounded-lg px-2 py-1.5 bg-white focus:ring-2 focus:ring-emerald-400 focus:border-transparent outline-none"
        >
          <option v-for="c in wsStore.canaisDisponiveis" :key="c.id" :value="c">
            {{ c.nome }} {{ c.evolution_phone_number ? `(${c.evolution_phone_number})` : '' }}
          </option>
        </select>
      </div>

      <!-- Canal do usuário (não-Admin) -->
      <div v-else-if="wsStore.canalAtual" class="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-1.5">
        <div :class="['w-2 h-2 rounded-full', wsStore.canalAtual.evolution_is_connected !== false ? 'bg-emerald-500' : 'bg-gray-300']"></div>
        <span class="text-sm font-medium text-emerald-700">{{ wsStore.canalAtual.nome }}</span>
        <span v-if="wsStore.canalAtual.evolution_phone_number" class="text-xs text-emerald-500">
          {{ wsStore.canalAtual.evolution_phone_number }}
        </span>
      </div>

      <!-- Tabs Inbox -->
      <div class="ml-auto flex items-center gap-1 bg-gray-100 rounded-xl p-1">
        <button
          v-for="tab in tabsInbox"
          :key="tab.value"
          @click="inboxFiltro = tab.value"
          :class="[
            'px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-150',
            inboxFiltro === tab.value
              ? 'bg-white text-emerald-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          {{ tab.label }}
          <span
            v-if="getTabCount(tab.value) > 0"
            class="ml-1 bg-red-500 text-white text-[9px] font-bold rounded-full px-1.5 py-0.5"
          >{{ getTabCount(tab.value) }}</span>
        </button>
      </div>

      <!-- Botão Atualizar -->
      <button
        @click="recarregar"
        :disabled="wsStore.conversasLoading"
        title="Atualizar conversas"
        class="p-2 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all"
      >
        <svg :class="['w-4 h-4', wsStore.conversasLoading ? 'animate-spin' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
      </button>
    </div>

    <!-- ─── Body Split-pane ─── -->
    <div class="flex-1 flex overflow-hidden">

      <!-- Painel Esquerdo: Lista de Conversas -->
      <div class="w-80 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 overflow-hidden">
        <ConversaList
          :conversas="conversasExibidas"
          :loading="wsStore.conversasLoading"
          :conversa-selecionada="conversaAtiva"
          @selecionar="abrirConversa"
        />
      </div>

      <!-- Painel Direito: Chat -->
      <div class="flex-1 flex flex-col overflow-hidden bg-[#e5ddd5]">

        <!-- Nenhuma conversa selecionada -->
        <div v-if="!conversaAtiva" class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <div class="w-24 h-24 bg-white/60 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
              <svg class="w-12 h-12 text-emerald-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751z"/>
              </svg>
            </div>
            <h2 class="text-lg font-semibold text-gray-600 mb-1">Selecione uma conversa</h2>
            <p class="text-sm text-gray-400">Clique em um contato para iniciar o atendimento</p>
          </div>
        </div>

        <!-- Chat Ativo: header + WhatsappChat embutido -->
        <template v-else>
          <!-- Header da conversa -->
          <div class="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 flex-shrink-0 shadow-sm">
            <div :class="['w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0', getAvatarColor(conversaAtiva.numero)]">
              {{ getInitials(conversaAtiva.nome_contato) }}
            </div>
            <div class="flex-1">
              <h3 class="text-sm font-bold text-gray-800">{{ conversaAtiva.nome_contato }}</h3>
              <p class="text-xs text-gray-400">{{ conversaAtiva.numero }}</p>
            </div>
            <!-- Badge de funil -->
            <span v-if="conversaAtiva.funil_tipo" :class="['text-xs px-2 py-1 rounded-full font-semibold', getFunilClass(conversaAtiva.funil_tipo)]">
              {{ getFunilLabel(conversaAtiva.funil_tipo) }}
            </span>
            <!-- Link para oportunidade -->
            <router-link
              v-if="conversaAtiva.oportunidade_id"
              :to="`/negocios/${conversaAtiva.oportunidade_id}`"
              target="_blank"
              title="Ver oportunidade"
              class="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
            </router-link>
            <!-- Fechar conversa -->
            <button @click="conversaAtiva = null" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Área de Mensagens (reutiliza WhatsappChat no modo embutido) -->
          <WhatsappChat
            :show="true"
            :number="conversaAtiva.numero"
            :title="conversaAtiva.nome_contato"
            :oportunidade="conversaAtiva.oportunidade_id"
            mode="embedded"
            @messages-read="wsStore.marcarConversaLida(conversaAtiva.numero)"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useWhatsappStore } from '@/stores/whatsapp'
import ConversaList from '@/components/atendimento/ConversaList.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'

const authStore = useAuthStore()
const wsStore = useWhatsappStore()

const isAdmin = computed(() => authStore.user?.perfil === 'ADMIN' || authStore.user?.is_superuser)
const conversaAtiva = ref(null)
const canalSelecionado = ref(null)

const inboxFiltro = ref('oportunidades')
const tabsInbox = [
  { label: 'Clientes', value: 'clientes' },
  { label: 'Oportunidades', value: 'oportunidades' },
  { label: 'Todos', value: 'todos' },
  { label: 'Desconhecidos', value: 'desconhecidos' },
]

const conversasExibidas = computed(() => {
  const todas = wsStore.conversas
  switch (inboxFiltro.value) {
    case 'clientes':
      return todas.filter(c => c.contato_id && c.conta_id)
    case 'oportunidades':
      return todas.filter(c => c.oportunidade_id)
    case 'desconhecidos':
      return todas.filter(c => !c.contato_id)
    default:
      return todas
  }
})

const getTabCount = (tipo) => {
  let lista
  switch (tipo) {
    case 'clientes':
      lista = wsStore.conversas.filter(c => c.contato_id && c.conta_id)
      break
    case 'oportunidades':
      lista = wsStore.conversas.filter(c => c.oportunidade_id)
      break
    case 'desconhecidos':
      lista = wsStore.conversas.filter(c => !c.contato_id)
      break
    default:
      lista = wsStore.conversas
  }
  return lista.reduce((acc, c) => acc + (c.nao_lidas || 0), 0)
}

const recarregar = () => wsStore.fetchConversas()

const mudarCanal = () => {
  wsStore.setCanal(canalSelecionado.value)
}

const abrirConversa = (conversa) => {
  conversaAtiva.value = conversa
  wsStore.marcarConversaLida(conversa.numero)
}

// Helpers visuais
const avatarColors = [
  'bg-teal-500', 'bg-blue-500', 'bg-indigo-500', 'bg-violet-500',
  'bg-pink-500', 'bg-rose-500', 'bg-amber-500', 'bg-lime-600',
]
const getAvatarColor = (numero) => {
  const sum = (numero || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  return avatarColors[sum % avatarColors.length]
}
const getInitials = (nome) => {
  if (!nome) return '?'
  return nome.split(' ').slice(0, 2).map(n => n[0]?.toUpperCase()).join('')
}
const getFunilClass = (tipo) => {
  switch (tipo) {
    case 'VENDAS': return 'bg-blue-100 text-blue-700'
    case 'SUPORTE': return 'bg-orange-100 text-orange-700'
    case 'POS_VENDA': return 'bg-purple-100 text-purple-700'
    default: return 'bg-gray-100 text-gray-500'
  }
}
const getFunilLabel = (tipo) => {
  switch (tipo) {
    case 'VENDAS': return 'Vendas'
    case 'SUPORTE': return 'Suporte'
    case 'POS_VENDA': return 'Pós-Venda'
    default: return tipo
  }
}

onMounted(async () => {
  await wsStore.fetchCanais()
  await wsStore.fetchConversas()
  wsStore.conectarWebSocket()
  if (wsStore.canalAtual) canalSelecionado.value = wsStore.canalAtual
})

onUnmounted(() => {
  wsStore.desconectarWebSocket()
})
</script>
