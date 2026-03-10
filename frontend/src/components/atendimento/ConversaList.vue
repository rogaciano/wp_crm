<template>
  <div class="flex flex-col h-full">
    <!-- Search -->
    <div class="p-3 border-b border-gray-100">
      <div class="relative">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="busca"
          type="text"
          placeholder="Pesquisar por nome ou número..."
          class="w-full pl-9 pr-4 py-2 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent"
        />
      </div>
    </div>

    <!-- Lista -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <div v-else-if="conversasFiltradas.length === 0" class="text-center py-12 px-4">
        <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
          </svg>
        </div>
        <p class="text-sm text-gray-400">Nenhuma conversa encontrada</p>
      </div>

      <div
        v-for="conversa in conversasFiltradas"
        :key="conversa.numero"
        @click="$emit('selecionar', conversa)"
        :class="[
          'flex items-center gap-3 px-4 py-3 cursor-pointer border-b border-gray-50 transition-all duration-150 group',
          conversaSelecionada?.numero === conversa.numero
            ? 'bg-emerald-50 border-l-4 border-l-emerald-500'
            : 'hover:bg-gray-50 border-l-4 border-l-transparent'
        ]"
      >
        <!-- Avatar -->
        <div :class="['w-11 h-11 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0 shadow-sm', getAvatarColor(conversa.numero)]">
          {{ getInitials(conversa.nome_contato) }}
        </div>

        <!-- Conteúdo -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-0.5">
            <span class="text-sm font-semibold text-gray-800 truncate">{{ conversa.nome_contato }}</span>
            <span class="text-[10px] text-gray-400 flex-shrink-0 ml-2">{{ formatTime(conversa.ultima_mensagem_timestamp) }}</span>
          </div>
          <div class="flex items-center justify-between">
            <p class="text-xs text-gray-500 truncate flex-1">
              <span v-if="conversa.de_mim" class="text-gray-400">✓ </span>
              {{ conversa.ultima_mensagem || 'Sem mensagens' }}
            </p>
            <div class="flex items-center gap-1 ml-2 flex-shrink-0">
              <!-- Badge funil -->
              <span
                v-if="conversa.funil_tipo"
                :class="['text-[9px] px-1 py-0.5 rounded-full font-bold uppercase', getFunilClass(conversa.funil_tipo)]"
              >{{ getFunilLabel(conversa.funil_tipo) }}</span>
              <!-- Badge não lidas -->
              <span
                v-if="conversa.nao_lidas > 0"
                class="bg-emerald-500 text-white text-[10px] font-bold rounded-full px-1.5 py-0.5 min-w-[18px] text-center leading-none"
              >{{ conversa.nao_lidas > 99 ? '99+' : conversa.nao_lidas }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  conversas: { type: Array, default: () => [] },
  loading: Boolean,
  conversaSelecionada: { type: Object, default: null },
})

const emit = defineEmits(['selecionar'])
const busca = ref('')

const conversasFiltradas = computed(() => {
  if (!busca.value.trim()) return props.conversas
  const q = busca.value.toLowerCase()
  return props.conversas.filter(c =>
    c.nome_contato?.toLowerCase().includes(q) ||
    c.numero?.includes(q)
  )
})

const getInitials = (nome) => {
  if (!nome) return '?'
  return nome.split(' ').slice(0, 2).map(n => n[0]?.toUpperCase()).join('')
}

const avatarColors = [
  'bg-teal-500', 'bg-blue-500', 'bg-indigo-500', 'bg-violet-500',
  'bg-pink-500', 'bg-rose-500', 'bg-amber-500', 'bg-lime-600',
]
const getAvatarColor = (numero) => {
  const sum = (numero || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  return avatarColors[sum % avatarColors.length]
}

const formatTime = (iso) => {
  if (!iso) return ''
  const date = new Date(iso)
  const now = new Date()
  const diffDays = Math.floor((now - date) / 86400000)
  if (diffDays === 0) return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  if (diffDays === 1) return 'Ontem'
  if (diffDays < 7) return date.toLocaleDateString('pt-BR', { weekday: 'short' })
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
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
    case 'VENDAS': return 'Venda'
    case 'SUPORTE': return 'Suporte'
    case 'POS_VENDA': return 'Pós-V'
    default: return tipo
  }
}
</script>
