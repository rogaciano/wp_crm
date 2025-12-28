<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Configurações de Planos</h1>
        <p class="text-gray-500 text-sm">Gerencie os planos e produtos disponíveis para venda.</p>
      </div>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Novo Plano
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="plano in planos" 
        :key="plano.id" 
        class="card group hover:shadow-xl transition-all duration-300 border border-transparent hover:border-primary-100 relative overflow-hidden flex flex-col"
      >
        <!-- Badge Preço -->
        <div class="absolute top-0 right-0 p-4 text-right">
          <div class="bg-primary-50 text-primary-700 text-sm font-black px-3 py-1 rounded-full border border-primary-100 italic">
            R$ {{ Number(plano.preco_mensal).toLocaleString('pt-BR') }}/mês
          </div>
          <div v-if="plano.preco_anual" class="mt-1 bg-violet-50 text-violet-700 text-[10px] font-black px-3 py-1 rounded-full border border-violet-100 italic">
            R$ {{ Number(plano.preco_anual).toLocaleString('pt-BR') }}/ano
          </div>
        </div>

        <div class="p-6 flex-grow">
          <div class="flex items-center space-x-3 mb-4">
            <div class="p-2 bg-primary-100 rounded-lg text-primary-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-10-10l-10 10m16 0l-10 10l-10-10" /></svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900">{{ plano.nome }}</h3>
          </div>

          <p class="text-gray-500 text-sm mb-6 min-h-[40px]">{{ plano.descricao || 'Sem descrição.' }}</p>

          <div class="space-y-2">
            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Recursos Inclusos</p>
            <ul class="space-y-2">
              <li v-for="(recurso, idx) in plano.recursos.slice(0, 5)" :key="idx" class="flex items-start text-sm text-gray-600">
                <svg class="w-4 h-4 text-emerald-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                <span>{{ recurso }}</span>
              </li>
              <li v-if="plano.recursos.length > 5" class="text-[10px] text-gray-400 font-bold pl-6 italic">
                + {{ plano.recursos.length - 5 }} outros recursos
              </li>
            </ul>
          </div>
        </div>

        <!-- Ações -->
        <div class="p-4 bg-gray-50 border-t border-gray-100 flex justify-end space-x-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            @click="openEditModal(plano)" 
            class="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            title="Editar Planos"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
          </button>
          <button 
            @click="deletePlano(plano.id)" 
            class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Excluir Plano"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
          </button>
        </div>
      </div>

      <div v-if="planos.length === 0" class="col-span-full text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-100">
        <div class="inline-block p-4 bg-gray-50 rounded-full mb-4">
          <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-10-10l-10 10m16 0l-10 10l-10-10" /></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900">Nenhum plano cadastrado</h3>
        <p class="text-gray-500 max-w-xs mx-auto mt-2">Os planos cadastrados aqui aparecerão na seleção de oportunidades para faturamento.</p>
        <button @click="openCreateModal" class="btn btn-primary mt-6">Criar Primeiro Plano</button>
      </div>
    </div>

    <!-- Adicionais Section -->
    <div class="mt-12 pt-12 border-t border-gray-100">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Recursos Adicionais (Add-ons)</h2>
          <p class="text-gray-500 text-sm">Personalize os planos com itens extras e cobranças específicas.</p>
        </div>
        <button @click="openCreateAdicionalModal" class="btn bg-emerald-600 text-white hover:bg-emerald-700 w-full sm:w-auto shadow-sm">
          + Novo Adicional
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="ad in adicionais" :key="ad.id" class="p-4 bg-white border border-gray-100 rounded-2xl flex flex-col justify-between hover:shadow-md transition-shadow">
          <div>
            <h4 class="font-bold text-gray-800">{{ ad.nome }}</h4>
            <p class="text-emerald-600 font-bold text-lg mt-1">
              R$ {{ Number(ad.preco).toLocaleString('pt-BR') }}
              <span class="text-[10px] text-gray-400 font-medium">/ {{ ad.unidade }}</span>
            </p>
          </div>
          <div class="flex justify-end mt-4 space-x-2">
            <button @click="openEditAdicionalModal(ad)" class="p-1.5 text-primary-600 hover:bg-primary-50 rounded-lg">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
            </button>
            <button @click="deleteAdicional(ad.id)" class="p-1.5 text-red-600 hover:bg-red-50 rounded-lg">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modais -->
    <PlanoModal
      :show="showModal"
      :plano="selectedPlano"
      @close="closeModal"
      @saved="loadData"
    />

    <PlanoAdicionalModal
      :show="showAdicionalModal"
      :adicional="selectedAdicional"
      @close="closeAdicionalModal"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import PlanoModal from '@/components/PlanoModal.vue'
import PlanoAdicionalModal from '@/components/PlanoAdicionalModal.vue'

const planos = ref([])
const adicionais = ref([])
const loading = ref(false)

const showModal = ref(false)
const selectedPlano = ref(null)

const showAdicionalModal = ref(false)
const selectedAdicional = ref(null)

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [planosRes, adicionaisRes] = await Promise.all([
      api.get('/planos/'),
      api.get('/adicionais-plano/')
    ])
    planos.value = planosRes.data.results || planosRes.data
    adicionais.value = adicionaisRes.data.results || adicionaisRes.data
  } catch (error) {
    console.error('Erro ao carregar dados:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedPlano.value = null
  showModal.value = true
}

function openEditModal(plano) {
  selectedPlano.value = plano
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedPlano.value = null
}

function openCreateAdicionalModal() {
  selectedAdicional.value = null
  showAdicionalModal.value = true
}

function openEditAdicionalModal(ad) {
  selectedAdicional.value = ad
  showAdicionalModal.value = true
}

function closeAdicionalModal() {
  showAdicionalModal.value = false
  selectedAdicional.value = null
}

async function deletePlano(id) {
  if (!confirm('Tem certeza que deseja excluir este plano? Estágios e faturamentos vinculados podem ser afetados.')) return
  
  try {
    await api.delete(`/planos/${id}/`)
    await loadData()
  } catch (error) {
    console.error('Erro ao excluir plano:', error)
    alert('Erro ao excluir plano. Verifique se existem oportunidades vinculadas.')
  }
}

async function deleteAdicional(id) {
  if (!confirm('Deseja excluir este recurso adicional?')) return
  try {
    await api.delete(`/adicionais-plano/${id}/`)
    await loadData()
  } catch (error) {
    console.error('Erro ao excluir:', error)
  }
}
</script>
