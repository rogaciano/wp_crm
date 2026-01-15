import { defineStore } from 'pinia'
import api from '@/services/api'

export const useWhatsappStore = defineStore('whatsapp', {
    state: () => ({
        unreadCounts: { novas: 0, oportunidades: 0, total: 0 },
        loading: false,
        error: null,
        lastUpdated: null
    }),
    actions: {
        async fetchUnreadCounts() {
            if (this.loading) return
            this.loading = true
            try {
                // console.log('Buscando contagens de WhatsApp...')
                const response = await api.get('/whatsapp/unread_counts/')
                // console.log('Resposta unread_counts:', response.data)
                this.unreadCounts = response.data
                this.lastUpdated = new Date()
                this.error = null
            } catch (error) {
                console.error('Erro ao buscar mensagens não lidas:', error)
                this.error = error.message
            } finally {
                this.loading = false
            }
        }
    }
})
