import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.perfil === 'ADMIN')
  const isResponsavel = computed(() => user.value?.perfil === 'RESPONSAVEL')
  const isVendedor = computed(() => user.value?.perfil === 'VENDEDOR')

  async function login(username, password) {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password
      })

      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh

      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)

      await fetchUser()
      return true
    } catch (error) {
      throw error
    }
  }

  async function fetchUser() {
    try {
      const response = await api.get('/usuarios/me/')
      user.value = response.data
    } catch (error) {
      if (error.response?.status === 401) {
        logout()
      }
      throw error
    }
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    isAdmin,
    isResponsavel,
    isVendedor,
    login,
    fetchUser,
    logout
  }
})
