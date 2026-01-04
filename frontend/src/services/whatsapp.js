import api from './api'

export const whatsappService = {
    getMessages(params) {
        return api.get('/whatsapp/', { params })
    },

    sendMessage(data) {
        // data: { number, text, lead, oportunidade }
        return api.post('/whatsapp/send/', data)
    },

    // Sincroniza mensagens da Evolution API para o banco local
    syncMessages(data) {
        // data: { number, lead, oportunidade, limit }
        return api.post('/whatsapp/sync/', data)
    },

    // Helper to normalize number if needed on frontend
    formatNumber(number) {
        if (!number) return ''
        return number.replace(/\D/g, '')
    }
}

export default whatsappService

