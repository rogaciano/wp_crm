import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useOportunidadesStore = defineStore('oportunidades', () => {
  const oportunidades = ref([])
  const kanbanData = ref([])
  const funis = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchFunis() {
    try {
      const response = await api.get('/funis/')
      funis.value = response.data.results || response.data
      return funis.value
    } catch (err) {
      console.error('Error fetching funis:', err)
      return []
    }
  }

  async function fetchKanban(funilId = null, canalId = null) {
    loading.value = true
    error.value = null
    try {
      let endpoint = '/oportunidades/kanban/'
      let params = {}

      if (canalId) params.canal = canalId
      if (funilId) params.funil_id = funilId

      const response = await api.get(endpoint, { params })

      // Padroniza a resposta
      const data = response.data.map(col => ({
        ...col,
        items: col.oportunidades || col.items || []
      }))

      kanbanData.value = data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching kanban:', err)
    } finally {
      loading.value = false
    }
  }

  async function createOportunidade(data) {
    try {
      const response = await api.post('/oportunidades/', data)
      await fetchKanban()
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function updateOportunidade(id, data) {
    try {
      const response = await api.patch(`/oportunidades/${id}/`, data)
      await fetchKanban()
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function mudarEstagio(id, estagioId) {
    try {
      const response = await api.patch(`/oportunidades/${id}/mudar_estagio/`, {
        estagio_id: estagioId
      })
      await fetchKanban()
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function fetchOportunidades() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/oportunidades/')
      oportunidades.value = response.data.results || response.data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching oportunidades:', err)
    } finally {
      loading.value = false
    }
  }

  async function deleteOportunidade(id) {
    try {
      await api.delete(`/oportunidades/${id}/`)
      await fetchKanban()
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    oportunidades,
    kanbanData,
    funis,
    loading,
    error,
    fetchFunis,
    fetchOportunidades,
    fetchKanban,
    createOportunidade,
    updateOportunidade,
    mudarEstagio,
    deleteOportunidade
  }
})
