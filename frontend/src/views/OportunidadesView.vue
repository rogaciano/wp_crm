<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Oportunidades</h1>
      <button class="btn btn-primary w-full sm:w-auto shadow-sm">+ Nova Oportunidade</button>
    </div>

    <div class="card overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else>
        <!-- Desktop Table -->
        <div class="hidden md:block overflow-x-auto">
          <table class="table">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">Nome</th>
                <th class="table-header">Conta</th>
                <th class="table-header">Valor</th>
                <th class="table-header">Estágio</th>
                <th class="table-header">Previsão</th>
                <th class="table-header">Probabilidade</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="oportunidade in oportunidades" :key="oportunidade.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900">{{ oportunidade.nome }}</td>
                <td class="table-cell text-gray-500">{{ oportunidade.conta_nome }}</td>
                <td class="table-cell font-semibold text-green-600">
                  R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
                </td>
                <td class="table-cell">
                  <span class="px-2 py-1 text-xs rounded-full font-medium" :style="{ backgroundColor: oportunidade.estagio_cor + '20', color: oportunidade.estagio_cor }">
                    {{ oportunidade.estagio_nome }}
                  </span>
                </td>
                <td class="table-cell text-gray-500">{{ formatDate(oportunidade.data_fechamento_esperada) }}</td>
                <td class="table-cell text-gray-500">{{ oportunidade.probabilidade }}%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="oportunidade in oportunidades" :key="oportunidade.id" class="p-4">
            <div class="flex justify-between items-start mb-2">
               <div>
                  <h3 class="font-bold text-gray-900">{{ oportunidade.nome }}</h3>
                  <p class="text-sm text-gray-500">{{ oportunidade.conta_nome }}</p>
               </div>
               <span class="px-2 py-1 text-[10px] font-bold uppercase rounded-full" :style="{ backgroundColor: oportunidade.estagio_cor + '20', color: oportunidade.estagio_cor }">
                  {{ oportunidade.estagio_nome }}
               </span>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mt-3 pt-3 border-t border-gray-50">
               <div>
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Valor Estimado</p>
                  <p class="text-sm font-bold text-green-600">R$ {{ Number(oportunidade.valor_estimado || 0).toLocaleString('pt-BR') }}</p>
               </div>
               <div class="text-right">
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Probabilidade</p>
                  <p class="text-sm font-bold text-gray-700">{{ oportunidade.probabilidade }}%</p>
               </div>
               <div>
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Previsão</p>
                  <p class="text-xs text-gray-600">{{ formatDate(oportunidade.data_fechamento_esperada) }}</p>
               </div>
            </div>
          </div>
        </div>

        <div v-if="oportunidades.length === 0" class="text-center py-12 text-gray-500">
          Nenhuma oportunidade registrada.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const oportunidades = ref([])
const loading = ref(false)

onMounted(() => {
  loadOportunidades()
})

async function loadOportunidades() {
  loading.value = true
  try {
    const response = await api.get('/oportunidades/')
    oportunidades.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar oportunidades:', error)
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR')
}
</script>
