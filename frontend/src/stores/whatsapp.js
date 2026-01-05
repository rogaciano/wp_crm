import { defineStore } from 'pinia'
import api from '@/services/api'

export const useWhatsappStore = defineStore('whatsapp', {
    state: () => ({
        unreadCounts: { leads: 0, oportunidades: 0, total: 0 },
        loading: false
    }),
    actions: {
        async fetchUnreadCounts() {
            try {
                const response = await api.get('/whatsapp/unread_counts/')
                this.unreadCounts = response.data
            } catch (error) {
                console.error('Erro ao buscar mensagens não lidas:', error)
            }
        }
    }
})
