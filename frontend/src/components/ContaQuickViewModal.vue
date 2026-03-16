<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
    <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">

      <!-- Loading -->
      <div v-if="loading" class="p-12 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <!-- Conteúdo -->
      <div v-else-if="conta" class="p-6 space-y-5">
        <!-- Header -->
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-xl font-black text-gray-900">{{ conta.nome_empresa }}</h2>
            <div class="flex items-center gap-2 mt-1">
              <span v-if="conta.marca" class="text-sm text-gray-500">{{ conta.marca }}</span>
              <span v-if="conta.status_cliente_display"
                class="text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-wide border"
                :class="conta.status_cliente === 'CLIENTE_ATIVO'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : conta.status_cliente === 'INATIVO'
                    ? 'bg-amber-50 text-amber-700 border-amber-200'
                    : 'bg-sky-50 text-sky-700 border-sky-200'"
              >{{ conta.status_cliente_display }}</span>
            </div>
          </div>
          <button @click="$emit('close')" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <!-- Dados da Empresa -->
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div v-if="conta.cnpj">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">CNPJ</span>
            <p class="font-semibold text-gray-800">{{ conta.cnpj }}</p>
          </div>
          <div v-if="conta.telefone_principal">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Telefone</span>
            <p class="font-semibold text-gray-800">{{ conta.telefone_principal }}</p>
          </div>
          <div v-if="conta.email">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Email</span>
            <p class="font-semibold text-gray-800 truncate">{{ conta.email }}</p>
          </div>
          <div v-if="conta.cidade || conta.estado">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Localização</span>
            <p class="font-semibold text-gray-800">{{ [conta.cidade, conta.estado].filter(Boolean).join(' / ') }}</p>
          </div>
          <div v-if="conta.endereco" class="col-span-2">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Endereço</span>
            <p class="font-semibold text-gray-800">{{ conta.endereco }}</p>
          </div>
          <div v-if="conta.setor">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Setor</span>
            <p class="font-semibold text-gray-800">{{ conta.setor }}</p>
          </div>
          <div v-if="conta.canal_nome">
            <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Canal</span>
            <p class="font-semibold text-gray-800">{{ conta.canal_nome }}</p>
          </div>
        </div>

        <!-- Contatos -->
        <div v-if="contatos.length" class="border-t pt-4">
          <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">
            Contatos ({{ contatos.length }})
          </h3>
          <div class="space-y-3">
            <div v-for="c in contatos" :key="c.id" class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
              <div class="w-10 h-10 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center flex-shrink-0">
                <span class="text-sm font-black">{{ c.nome?.charAt(0)?.toUpperCase() }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-bold text-gray-900 text-sm truncate">{{ c.nome }}</p>
                <p v-if="c.cargo" class="text-xs text-gray-400">{{ c.cargo }}</p>
                <div class="flex flex-wrap items-center gap-3 mt-1">
                  <a v-if="c.celular || c.telefone" :href="'tel:' + (c.celular || c.telefone)" class="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M6.62 10.79a15.053 15.053 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24c1.12.37 2.33.57 3.57.57a1 1 0 011 1v3.5a1 1 0 01-1 1C10.07 22.5 1.5 13.93 1.5 3.5A1 1 0 012.5 2.5H6a1 1 0 011 1c0 1.25.2 2.45.57 3.57a1 1 0 01-.24 1.01l-2.2 2.2z"/></svg>
                    {{ c.celular_formatado || c.telefone_formatado || c.celular || c.telefone }}
                  </a>
                  <a v-if="c.email" :href="'mailto:' + c.email" class="text-xs text-blue-600 font-semibold truncate">{{ c.email }}</a>
                </div>
              </div>
              <a v-if="c.celular || c.telefone"
                :href="'https://wa.me/' + formatWhatsapp(c.celular || c.telefone)"
                target="_blank"
                class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors flex-shrink-0"
                title="WhatsApp"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
              </a>
            </div>
          </div>
        </div>

        <!-- Notas -->
        <div v-if="conta.notas" class="border-t pt-4">
          <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Observações</h3>
          <p class="text-sm text-gray-600 whitespace-pre-line">{{ conta.notas }}</p>
        </div>

        <!-- Ações -->
        <div class="border-t pt-4 flex justify-end gap-3">
          <button @click="$emit('close')" class="btn btn-white text-sm">Fechar</button>
          <button @click="goToFull" class="btn btn-primary text-sm">Ver Ficha Completa</button>
        </div>
      </div>

      <!-- Erro / Sem dados -->
      <div v-else class="p-12 text-center text-gray-400">
        <p>Empresa não encontrada.</p>
        <button @click="$emit('close')" class="btn btn-white text-sm mt-4">Fechar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  contaId: Number,
})

const emit = defineEmits(['close'])
const router = useRouter()

const loading = ref(false)
const conta = ref(null)
const contatos = ref([])

watch(() => props.show, async (val) => {
  if (val && props.contaId) {
    loading.value = true
    conta.value = null
    contatos.value = []
    try {
      const [contaRes, contatosRes] = await Promise.all([
        api.get(`/contas/${props.contaId}/`),
        api.get('/contatos/', { params: { conta: props.contaId } })
      ])
      conta.value = contaRes.data
      contatos.value = contatosRes.data.results || contatosRes.data
    } catch (e) {
      console.error('Erro ao carregar dados da empresa:', e)
    } finally {
      loading.value = false
    }
  }
})

function formatWhatsapp(phone) {
  if (!phone) return ''
  let digits = phone.replace(/\D/g, '')
  if (digits.length <= 11 && !digits.startsWith('55')) digits = '55' + digits
  return digits
}

function goToFull() {
  emit('close')
  router.push({ name: 'conta-detail', params: { id: props.contaId } })
}
</script>
