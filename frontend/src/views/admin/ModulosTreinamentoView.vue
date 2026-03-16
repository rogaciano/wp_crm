<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Módulos de Treinamento</h1>
        <p class="text-gray-500 text-sm">Gerencie os módulos disponíveis para o onboarding de clientes.</p>
      </div>
      <button @click="openCreateModal" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Novo Módulo
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="modulo in modulos" 
        :key="modulo.id" 
        class="card group hover:shadow-xl transition-all duration-300 border border-transparent hover:border-primary-100 relative overflow-hidden flex flex-col"
      >
        <!-- Badge Status -->
        <div class="absolute top-0 right-0 p-4 text-right">
          <div 
            class="text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wide"
            :class="modulo.ativo ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-gray-100 text-gray-500 border border-gray-200'"
          >
            {{ modulo.ativo ? 'Ativo' : 'Inativo' }}
          </div>
        </div>

        <div class="p-6 flex-grow">
          <div class="flex items-center space-x-3 mb-4">
            <div class="p-2 bg-violet-100 rounded-lg text-violet-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
            </div>
            <div class="min-w-0">
              <h3 class="text-lg font-bold text-gray-900 truncate">{{ modulo.nome }}</h3>
              <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Ordem: {{ modulo.ordem }}</p>
            </div>
          </div>

          <p class="text-gray-500 text-sm mb-6 min-h-[40px]">{{ modulo.descricao || 'Sem descrição.' }}</p>

          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span class="font-semibold">{{ formatDuracao(modulo.carga_horaria_estimada) }}</span>
            </div>
          </div>
        </div>

        <!-- Ações -->
        <div class="p-4 bg-gray-50 border-t border-gray-100 flex justify-end space-x-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            @click="openEditModal(modulo)" 
            class="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            title="Editar Módulo"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
          </button>
          <button 
            @click="deleteModulo(modulo.id)" 
            class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Excluir Módulo"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
          </button>
        </div>
      </div>

      <div v-if="modulos.length === 0" class="col-span-full text-center py-20 bg-white rounded-3xl border-2 border-dashed border-gray-100">
        <div class="inline-block p-4 bg-gray-50 rounded-full mb-4">
          <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900">Nenhum módulo cadastrado</h3>
        <p class="text-gray-500 max-w-xs mx-auto mt-2">Os módulos cadastrados aqui serão usados nas fichas de onboarding dos clientes.</p>
        <button @click="openCreateModal" class="btn btn-primary mt-6">Criar Primeiro Módulo</button>
      </div>
    </div>

    <!-- Modal -->
    <ModuloTreinamentoModal
      :show="showModal"
      :modulo="selectedModulo"
      @close="closeModal"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import ModuloTreinamentoModal from '@/components/ModuloTreinamentoModal.vue'

const modulos = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedModulo = ref(null)

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await api.get('/modulos-treinamento/')
    modulos.value = res.data.results || res.data
  } catch (error) {
    console.error('Erro ao carregar módulos:', error)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedModulo.value = null
  showModal.value = true
}

function openEditModal(modulo) {
  selectedModulo.value = modulo
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedModulo.value = null
}

async function deleteModulo(id) {
  if (!confirm('Tem certeza que deseja excluir este módulo de treinamento?')) return
  try {
    await api.delete(`/modulos-treinamento/${id}/`)
    await loadData()
  } catch (error) {
    console.error('Erro ao excluir módulo:', error)
    alert('Erro ao excluir módulo. Verifique se existem sessões vinculadas.')
  }
}

function formatDuracao(minutos) {
  if (!minutos) return '-'
  if (minutos < 60) return `${minutos}min`
  const h = Math.floor(minutos / 60)
  const m = minutos % 60
  return m > 0 ? `${h}h ${m}min` : `${h}h`
}
</script>
