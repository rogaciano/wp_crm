<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <!-- Header -->
    <header class="bg-white/10 backdrop-blur-lg border-b border-white/10">
      <div class="max-w-4xl mx-auto px-4 py-6">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-white">Diagnóstico de Maturidade</h1>
            <p class="text-purple-200">Descubra o nível de maturidade da sua empresa</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center">
        <div class="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-purple-200">Carregando perguntas...</p>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center bg-red-500/20 backdrop-blur-lg rounded-2xl p-8 max-w-md mx-4">
        <div class="w-16 h-16 bg-red-500/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-white mb-2">Ops!</h2>
        <p class="text-red-200">{{ error }}</p>
      </div>
    </div>

    <!-- Resultado -->
    <div v-else-if="resultado" class="max-w-4xl mx-auto px-4 py-12">
      <div class="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
        <div class="text-center mb-8">
          <div class="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-3xl font-bold text-white mb-2">Diagnóstico Concluído!</h2>
          <p class="text-purple-200">Confira abaixo o resultado da sua análise</p>
        </div>

        <!-- Gráfico de Resultados -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div 
            v-for="(dados, pilar) in resultado" 
            :key="pilar"
            class="bg-white/5 rounded-xl p-6 border border-white/10"
          >
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-lg font-semibold text-white">{{ pilar }}</h3>
              <span 
                class="text-2xl font-bold"
                :style="{ color: dados.cor }"
              >{{ dados.score }}/10</span>
            </div>
            <div class="h-3 bg-white/10 rounded-full overflow-hidden">
              <div 
                class="h-full rounded-full transition-all duration-1000"
                :style="{ 
                  width: `${dados.score * 10}%`,
                  backgroundColor: dados.cor 
                }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Análise IA -->
        <div v-if="analiseIa" class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl p-6 border border-purple-400/30">
          <h3 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Análise Estratégica
          </h3>
          <div class="text-purple-100 whitespace-pre-line">{{ analiseIa }}</div>
        </div>

        <div class="text-center mt-8">
          <p class="text-purple-200 mb-4">Em breve, um de nossos consultores entrará em contato!</p>
        </div>
      </div>
    </div>

    <!-- Formulário -->
    <div v-else class="max-w-4xl mx-auto px-4 py-8">
      <!-- Progress Bar -->
      <div class="mb-8">
        <div class="flex items-center justify-between text-sm text-purple-200 mb-2">
          <span>Progresso</span>
          <span>{{ Math.round(progresso) }}%</span>
        </div>
        <div class="h-2 bg-white/10 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-300"
            :style="{ width: `${progresso}%` }"
          ></div>
        </div>
      </div>

      <!-- Pilar Atual -->
      <div v-if="pilarAtual" class="mb-6">
        <div 
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium"
          :style="{ backgroundColor: pilarAtual.cor + '33', color: pilarAtual.cor }"
        >
          <span>{{ pilarAtualIndex + 1 }}/{{ pilares.length }}</span>
          <span class="font-semibold">{{ pilarAtual.nome }}</span>
        </div>
      </div>

      <!-- Pergunta Atual -->
      <div v-if="perguntaAtual" class="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 mb-6">
        <h2 class="text-xl md:text-2xl font-semibold text-white mb-2">
          {{ perguntaAtual.texto }}
        </h2>
        <p v-if="perguntaAtual.ajuda" class="text-purple-200 text-sm mb-6">
          💡 {{ perguntaAtual.ajuda }}
        </p>

        <!-- Opções de Resposta -->
        <div class="space-y-3">
          <button
            v-for="resposta in perguntaAtual.respostas"
            :key="resposta.id"
            @click="selecionarResposta(resposta)"
            class="w-full text-left p-4 rounded-xl border-2 transition-all duration-200"
            :class="respostaSelecionada === resposta.id 
              ? 'bg-purple-500/30 border-purple-400 text-white' 
              : 'bg-white/5 border-white/10 text-purple-100 hover:bg-white/10 hover:border-white/20'"
          >
            <div class="flex items-center gap-3">
              <div 
                class="w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                :class="respostaSelecionada === resposta.id 
                  ? 'border-purple-400 bg-purple-500' 
                  : 'border-white/30'"
              >
                <div 
                  v-if="respostaSelecionada === resposta.id" 
                  class="w-2 h-2 bg-white rounded-full"
                ></div>
              </div>
              <span>{{ resposta.texto }}</span>
            </div>
          </button>
        </div>
      </div>

      <!-- Formulário de Dados (última etapa) -->
      <div v-if="mostrarFormularioDados" class="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 mb-6">
        <h2 class="text-2xl font-bold text-white mb-2">Quase lá! 🎉</h2>
        <p class="text-purple-200 mb-6">Preencha seus dados para receber o resultado personalizado</p>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-purple-200 mb-2">Nome Completo *</label>
            <input 
              v-model="dadosCliente.nome"
              type="text"
              class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Seu nome"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-purple-200 mb-2">E-mail *</label>
            <input 
              v-model="dadosCliente.email"
              type="email"
              class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="seu@email.com"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-purple-200 mb-2">Telefone/WhatsApp *</label>
            <input 
              v-model="dadosCliente.telefone"
              type="tel"
              class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="(00) 00000-0000"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-purple-200 mb-2">Nome da Empresa *</label>
            <input 
              v-model="dadosCliente.empresa"
              type="text"
              class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Sua empresa"
            />
          </div>
        </div>

        <p v-if="formError" class="text-red-400 text-sm mt-4">{{ formError }}</p>
      </div>

      <!-- Botões de Navegação -->
      <div class="flex items-center justify-between">
        <button
          v-if="podeVoltar"
          @click="voltarPergunta"
          class="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Voltar
        </button>
        <div v-else></div>

        <button
          v-if="!mostrarFormularioDados"
          @click="proximaPergunta"
          :disabled="!respostaSelecionada"
          class="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all flex items-center gap-2"
        >
          Próxima
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <button
          v-else
          @click="enviarDiagnostico"
          :disabled="enviando"
          class="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all flex items-center gap-2"
        >
          <span v-if="enviando">Enviando...</span>
          <span v-else>Ver Resultado</span>
          <svg v-if="!enviando" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const canalSlug = computed(() => route.params.canalSlug || 'matriz')

// Estados
const loading = ref(true)
const error = ref(null)
const pilares = ref([])
const respostas = ref({}) // { pergunta_id: resposta_id }
const perguntaAtualIndex = ref(0)
const respostaSelecionada = ref(null)
const mostrarFormularioDados = ref(false)
const enviando = ref(false)
const resultado = ref(null)
const analiseIa = ref(null)
const formError = ref(null)

const dadosCliente = ref({
  nome: '',
  email: '',
  telefone: '',
  empresa: ''
})

// Computed
const todasPerguntas = computed(() => {
  return pilares.value.flatMap(p => 
    p.perguntas.map(perg => ({
      ...perg,
      pilar: p
    }))
  )
})

const perguntaAtual = computed(() => todasPerguntas.value[perguntaAtualIndex.value])
const pilarAtual = computed(() => perguntaAtual.value?.pilar)
const pilarAtualIndex = computed(() => pilares.value.findIndex(p => p.id === pilarAtual.value?.id))

const progresso = computed(() => {
  if (todasPerguntas.value.length === 0) return 0
  if (mostrarFormularioDados.value) return 100
  return (perguntaAtualIndex.value / todasPerguntas.value.length) * 100
})

const podeVoltar = computed(() => perguntaAtualIndex.value > 0 || mostrarFormularioDados.value)

// Métodos
async function carregarPerguntas() {
  try {
    loading.value = true
    const response = await axios.get('/api/diagnosticos/perguntas/')
    pilares.value = response.data
    
    if (pilares.value.length === 0) {
      error.value = 'Nenhuma pergunta configurada no sistema.'
    }
  } catch (err) {
    console.error('Erro ao carregar perguntas:', err)
    error.value = 'Erro ao carregar o diagnóstico. Tente novamente mais tarde.'
  } finally {
    loading.value = false
  }
}

function selecionarResposta(resposta) {
  respostaSelecionada.value = resposta.id
  respostas.value[perguntaAtual.value.id] = resposta.id
}

function proximaPergunta() {
  if (!respostaSelecionada.value) return
  
  if (perguntaAtualIndex.value < todasPerguntas.value.length - 1) {
    perguntaAtualIndex.value++
    // Carrega resposta salva se existir
    respostaSelecionada.value = respostas.value[perguntaAtual.value?.id] || null
  } else {
    mostrarFormularioDados.value = true
  }
}

function voltarPergunta() {
  if (mostrarFormularioDados.value) {
    mostrarFormularioDados.value = false
    respostaSelecionada.value = respostas.value[perguntaAtual.value?.id] || null
  } else if (perguntaAtualIndex.value > 0) {
    perguntaAtualIndex.value--
    respostaSelecionada.value = respostas.value[perguntaAtual.value?.id] || null
  }
}

async function enviarDiagnostico() {
  formError.value = null
  
  // Validação
  if (!dadosCliente.value.nome.trim()) {
    formError.value = 'Por favor, informe seu nome.'
    return
  }
  if (!dadosCliente.value.email.trim() || !dadosCliente.value.email.includes('@')) {
    formError.value = 'Por favor, informe um e-mail válido.'
    return
  }
  if (!dadosCliente.value.telefone.trim()) {
    formError.value = 'Por favor, informe seu telefone.'
    return
  }
  if (!dadosCliente.value.empresa.trim()) {
    formError.value = 'Por favor, informe o nome da empresa.'
    return
  }
  
  try {
    enviando.value = true
    
    const payload = {
      nome: dadosCliente.value.nome,
      email: dadosCliente.value.email,
      telefone: dadosCliente.value.telefone,
      empresa: dadosCliente.value.empresa,
      respostas_ids: Object.values(respostas.value)
    }
    
    const response = await axios.post(`/api/diagnosticos/submeter-publico/${canalSlug.value}/`, payload)
    
    resultado.value = response.data.resultado
    analiseIa.value = response.data.analise_ia
    
  } catch (err) {
    console.error('Erro ao enviar diagnóstico:', err)
    formError.value = err.response?.data?.error || 'Erro ao enviar. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

onMounted(() => {
  carregarPerguntas()
})
</script>
