<template>
  <div class="min-h-screen bg-white text-gray-900 font-sans selection:bg-primary-100">
    <!-- Progress Bar -->
    <div v-if="state !== 'welcome' && state !== 'loading'" class="fixed top-0 left-0 w-full h-1.5 bg-gray-100 z-50">
      <div 
        class="h-full bg-primary-600 transition-all duration-500 ease-out"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>

    <main class="max-w-4xl mx-auto px-6 py-12 min-h-screen flex flex-col justify-center">
      
      <!-- State: Loading -->
      <div v-if="state === 'loading'" class="text-center animate-pulse">
        <div class="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-500">Preparando seu diagnóstico...</p>
      </div>

      <!-- State: Welcome -->
      <div v-else-if="state === 'welcome'" class="text-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div class="inline-block px-4 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm font-semibold tracking-wide uppercase mb-2">
          Exclusivo para Confecções
        </div>
        <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight text-gray-900 leading-tight">
          Descubra o Nível de Maturidade da sua <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-primary-400">Fábrica de Roupas</span>
        </h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
          Responda a algumas perguntas rápidas sobre seus processos e receba um diagnóstico completo dos seus pontos fortes e onde você está perdendo dinheiro.
        </p>
        <div class="pt-8">
          <button 
            @click="startDiagnosis"
            class="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-primary-600 font-pj rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 hover:bg-primary-700 shadow-xl hover:shadow-primary-200"
          >
            Começar Diagnóstico Gratuito
            <svg class="w-5 h-5 ml-3 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
          <p class="mt-4 text-sm text-gray-400">Leva menos de 3 minutos</p>
        </div>
      </div>

      <!-- State: Questions -->
      <div v-else-if="state === 'questions'" class="animate-in fade-in slide-in-from-right-4 duration-500">
        <div class="mb-12">
          <span class="text-xs font-bold text-primary-600 uppercase tracking-widest">{{ currentPilar.nome }}</span>
          <h2 class="text-3xl font-bold text-gray-900 mt-2">{{ currentQuestion.texto }}</h2>
          <p v-if="currentQuestion.ajuda" class="text-gray-500 mt-2 text-sm italic">{{ currentQuestion.ajuda }}</p>
        </div>

        <div class="grid gap-4">
          <button 
            v-for="resp in currentQuestion.respostas" 
            :key="resp.id"
            @click="selectResponse(resp.id)"
            class="flex items-center p-6 text-left border-2 rounded-2xl transition-all duration-200 hover:border-primary-500 group"
            :class="selectedResponses[currentQuestion.id] === resp.id ? 'border-primary-600 bg-primary-50 ring-4 ring-primary-50' : 'border-gray-100 bg-white'"
          >
            <div 
              class="w-6 h-6 rounded-full border-2 mr-4 flex items-center justify-center transition-colors shadow-inner"
              :class="selectedResponses[currentQuestion.id] === resp.id ? 'border-primary-600 bg-primary-600' : 'border-gray-300 group-hover:border-primary-400'"
            >
              <div v-if="selectedResponses[currentQuestion.id] === resp.id" class="w-2 h-2 bg-white rounded-full"></div>
            </div>
            <span class="text-lg font-medium text-gray-800">{{ resp.texto }}</span>
          </button>
        </div>

        <div class="mt-12 flex justify-between items-center">
          <button 
            @click="prevQuestion"
            :disabled="isFirstQuestion"
            class="px-6 py-2 text-gray-400 font-medium hover:text-gray-600 disabled:opacity-0 transition-all flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            Anterior
          </button>
          
          <button 
            @click="nextQuestion"
            :disabled="!selectedResponses[currentQuestion.id]"
            class="px-10 py-4 bg-gray-900 text-white rounded-xl font-bold hover:bg-black transition-all shadow-lg disabled:opacity-30 flex items-center"
          >
            {{ isLastQuestion ? 'Próximo Passo' : 'Próxima Pergunta' }}
            <svg v-if="!isLastQuestion" class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>

      <!-- State: Contact Info -->
      <div v-else-if="state === 'contact_info'" class="max-w-md mx-auto animate-in zoom-in-95 duration-500">
        <div class="text-center mb-10">
          <div class="w-20 h-20 bg-primary-100 text-primary-600 rounded-3xl flex items-center justify-center mx-auto mb-6 rotate-3">
            <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <h2 class="text-3xl font-bold text-gray-900">Quase lá!</h2>
          <p class="text-gray-500 mt-2">Para onde enviamos o seu diagnóstico detalhado?</p>
        </div>

        <form @submit.prevent="submitDiagnosis" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">Seu Nome Completo</label>
            <input v-model="contactForm.nome" type="text" required class="w-full px-5 py-4 rounded-xl border-2 border-gray-100 focus:border-primary-500 focus:ring-0 transition-all outline-none" placeholder="João Silva">
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1">E-mail Profissional</label>
            <input v-model="contactForm.email" type="email" required class="w-full px-5 py-4 rounded-xl border-2 border-gray-100 focus:border-primary-500 focus:ring-0 transition-all outline-none" placeholder="joao@suaempresa.com.br">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">WhatsApp</label>
              <input v-model="contactForm.telefone" type="text" class="w-full px-5 py-4 rounded-xl border-2 border-gray-100 focus:border-primary-500 focus:ring-0 transition-all outline-none" placeholder="(11) 99999-9999">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Nome da Empresa</label>
              <input v-model="contactForm.empresa" type="text" class="w-full px-5 py-4 rounded-xl border-2 border-gray-100 focus:border-primary-500 focus:ring-0 transition-all outline-none" placeholder="Minha Confecção">
            </div>
          </div>

          <button 
            type="submit" 
            :disabled="submitting"
            class="w-full py-5 bg-primary-600 text-white rounded-2xl font-bold text-lg hover:bg-primary-700 transition-all shadow-xl hover:shadow-primary-100 disabled:opacity-50 mt-4 flex items-center justify-center"
          >
            <span v-if="submitting" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3"></span>
            {{ submitting ? 'Gerando Diagnóstico...' : 'Ver Meu Resultado Agora' }}
          </button>
        </form>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const state = ref('welcome') // welcome, loading, questions, contact_info
const submitting = ref(false)

const pilares = ref([])
const currentPilarIndex = ref(0)
const currentQuestionIndex = ref(0)
const selectedResponses = ref({})

const contactForm = ref({
  nome: '',
  email: '',
  telefone: '',
  empresa: ''
})

// Flatten questions for easier navigation
const allQuestions = computed(() => {
  return pilares.value.flatMap(p => p.perguntas)
})

const currentQuestion = computed(() => {
  return allQuestions.value[allQuestionIndex.value] || {}
})

const currentPilar = computed(() => {
  return pilares.value.find(p => p.perguntas.some(q => q.id === currentQuestion.value.id)) || {}
})

const allQuestionIndex = ref(0)
const progress = computed(() => {
  if (state.value === 'welcome') return 0
  if (state.value === 'contact_info') return 100
  return ((allQuestionIndex.value) / allQuestions.value.length) * 100
})

const isFirstQuestion = computed(() => allQuestionIndex.value === 0)
const isLastQuestion = computed(() => allQuestionIndex.value === allQuestions.value.length - 1)

async function startDiagnosis() {
  state.value = 'loading'
  try {
    const response = await api.get('/diagnosticos/perguntas/')
    pilares.value = response.data
    state.value = 'questions'
  } catch (error) {
    console.error('Erro ao carregar perguntas:', error)
    alert('Erro ao carregar o diagnóstico. Por favor, tente novamente mais tarde.')
    state.value = 'welcome'
  }
}

function selectResponse(respId) {
  selectedResponses.value[currentQuestion.value.id] = respId
}

function nextQuestion() {
  if (isLastQuestion.value) {
    state.value = 'contact_info'
  } else {
    allQuestionIndex.value++
  }
}

function prevQuestion() {
  if (allQuestionIndex.value > 0) {
    allQuestionIndex.value--
  }
}

async function submitDiagnosis() {
  submitting.value = true
  try {
    const payload = {
      ...contactForm.value,
      respostas_ids: Object.values(selectedResponses.value),
      oportunidade_id: route.query.oportunidade_id || null,
      contato_id: route.query.contato_id || null
    }
    
    const response = await api.post('/diagnosticos/submeter/', payload)
    
    // Armazena o resultado para exibir na próxima tela
    localStorage.setItem('last_diagnosis_result', JSON.stringify(response.data))
    
    router.push({ name: 'diagnostico-resultado' })
  } catch (error) {
    console.error('Erro ao submeter diagnóstico:', error)
    alert('Ocorreu um erro ao processar seu diagnóstico.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
