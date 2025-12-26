<template>
  <div class="min-h-screen bg-gray-50 py-12 px-6">
    <div class="max-w-5xl mx-auto">
      
      <!-- Loading State -->
      <div v-if="!results" class="flex flex-col items-center justify-center py-20">
        <div class="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-gray-500 font-medium">Carregando seu diagnóstico...</p>
      </div>

      <template v-else>
        <!-- Voltar -->
        <router-link to="/diagnostico" class="inline-flex items-center text-sm font-medium text-gray-500 hover:text-primary-600 mb-8 transition-colors">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7 7-7" /></svg>
          Refazer Diagnóstico
        </router-link>

        <div class="bg-white rounded-3xl shadow-xl shadow-gray-200/50 overflow-hidden border border-gray-100">
          <div class="grid md:grid-cols-2">
            
            <!-- Lado Esquerdo: Gráfico e Score Geral -->
            <div class="p-8 md:p-12 bg-white border-b md:border-b-0 md:border-r border-gray-100 flex flex-col items-center">
              <div class="text-center mb-8">
                <h1 class="text-4xl font-extrabold text-gray-900 tracking-tight">Seu Resultado</h1>
                <p class="text-gray-500 mt-2">Veja o mapa de maturidade da sua confecção</p>
              </div>

              <!-- Gráfico de Radar -->
              <div class="w-full aspect-square max-w-sm mb-8 relative">
                <Radar v-if="chartDataLoaded" :data="chartData" :options="chartOptions" />
              </div>

              <div class="w-full bg-primary-50 rounded-2xl p-6 text-center">
                <span class="text-sm font-bold text-primary-600 uppercase tracking-widest">Score de Maturidade Global</span>
                <div class="text-6xl font-black text-primary-700 mt-1">{{ averageScore }}<span class="text-2xl text-primary-400">/10</span></div>
              </div>
            </div>

            <!-- Lado Direito: Detalhamento por Pilar -->
            <div class="p-8 md:p-12 flex flex-col">
              <h2 class="text-2xl font-bold text-gray-900 mb-8">Análise por Pilar</h2>
              
              <div class="space-y-6 flex-grow">
                <div v-for="(data, pilar) in results.resultado" :key="pilar" class="space-y-2">
                  <div class="flex justify-between items-end">
                    <span class="font-bold text-gray-700">{{ pilar }}</span>
                    <span class="text-lg font-black" :style="{ color: data.cor }">{{ data.score }}</span>
                  </div>
                  <div class="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      class="h-full rounded-full transition-all duration-1000 ease-out"
                      :style="{ width: `${data.score * 10}%`, backgroundColor: data.cor }"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- Análise da IA -->
              <div v-if="results.analise_ia" class="mt-12 bg-indigo-50 rounded-2xl p-6 border border-indigo-100">
                <div class="flex items-center mb-4">
                  <div class="p-2 bg-indigo-600 rounded-lg mr-3">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  </div>
                  <h3 class="text-lg font-bold text-indigo-900">Análise Estratégica da IA</h3>
                </div>
                <div class="prose prose-sm text-indigo-800 max-w-none ai-analysis-content" v-html="formatAiText(results.analise_ia)">
                </div>
              </div>

              <div class="mt-8 bg-gray-900 rounded-2xl p-8 text-white relative overflow-hidden group">
                <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                  <svg class="w-24 h-24" fill="currentColor" viewBox="0 0 20 20"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3.005 3.005 0 013.75-2.906z"></path></svg>
                </div>
                <h3 class="text-xl font-bold mb-2">Quer ajuda para melhorar esses índices?</h3>
                <p class="text-gray-400 text-sm mb-6 leading-relaxed">Nosso especialista em gestão têxtil está disponível para uma mentoria gratuita de 15 minutos focada no seu diagnóstico.</p>
                <button class="w-full py-4 bg-primary-600 hover:bg-primary-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-primary-900/20">
                  Falar com Especialista via WhatsApp
                </button>
              </div>
            </div>

          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'
import { Radar } from 'vue-chartjs'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

const router = useRouter()
const results = ref(null)
const chartDataLoaded = ref(false)

onMounted(() => {
  const data = localStorage.getItem('last_diagnosis_result')
  if (!data) {
    router.push({ name: 'diagnostico' })
    return
  }
  results.value = JSON.parse(data)
  chartDataLoaded.value = true
})

const averageScore = computed(() => {
  if (!results.value) return 0
  const rs = results.value.resultado || results.value  // Handle different formats
  const scores = Object.values(rs).map(r => r.score)
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length
  return avg.toFixed(1)
})

const chartData = computed(() => {
  if (!results.value) return {}
  
  // Se houver comparação (dados de histórico)
  const comparison = ref(null)
  const compData = localStorage.getItem('comparison_diagnosis_result')
  if (compData) comparison.value = JSON.parse(compData)

  const labels = Object.keys(results.value.resultado)
  const datasets = [
    {
      label: comparison.value ? 'Diagnóstico Atual' : 'Maturidade Atual',
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      borderColor: '#3B82F6',
      pointBackgroundColor: '#3B82F6',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#3B82F6',
      data: Object.values(results.value.resultado).map(r => r.score)
    }
  ]

  if (comparison.value) {
    datasets.unshift({
      label: 'Diagnóstico Anterior',
      backgroundColor: 'rgba(156, 163, 175, 0.2)',
      borderColor: '#9CA3AF',
      pointBackgroundColor: '#9CA3AF',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#9CA3AF',
      data: labels.map(label => comparison.value.resultado[label]?.score || 0)
    })
  }
  
  return {
    labels,
    datasets
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  scales: {
    r: {
      angleLines: {
        display: true
      },
      suggestedMin: 0,
      suggestedMax: 10,
      ticks: {
        stepSize: 2,
        display: false
      }
    }
  },
  plugins: {
    legend: {
      display: false
    }
  }
}

function formatAiText(text) {
  if (!text) return ''
  return text
    .replace(/^### (.*$)/gim, '<h3 class="font-bold text-lg mt-4 mb-2">$1</h3>')
    .replace(/^#### (.*$)/gim, '<h4 class="font-bold text-md mt-3 mb-1 text-indigo-700">$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-indigo-900">$1</strong>')
    .replace(/^- (.*$)/gim, '<li class="ml-4 mb-1">$1</li>')
    .replace(/\n/g, '<br>')
}
</script>
