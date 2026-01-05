import api from './api'

export const whatsappService = {
    // ==================== MENSAGENS ====================

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

    // Marca mensagens como lidas
    marcarLidas(data) {
        // data: { number, lead, oportunidade }
        return api.post('/whatsapp/marcar_lidas/', data)
    },

    // Busca contagem global de não lidas para o menu
    getUnreadCounts() {
        return api.get('/whatsapp/unread_counts/')
    },

    // ==================== CONEXÃO ====================

    // Verifica status da conexão
    getStatus() {
        return api.get('/whatsapp/status/')
    },

    // Obtém QR Code para conexão
    getQRCode() {
        return api.get('/whatsapp/qrcode/')
    },

    // Inicia processo de conexão (retorna status + QR code se necessário)
    connect() {
        return api.post('/whatsapp/connect/')
    },

    // Desconecta o WhatsApp
    disconnect() {
        return api.post('/whatsapp/disconnect/')
    },

    // Reinicia a instância
    restart() {
        return api.post('/whatsapp/restart/')
    },

    // Obtém informações da instância
    getInstanceInfo() {
        return api.get('/whatsapp/instance_info/')
    },

    // ==================== HELPERS ====================

    formatNumber(number) {
        if (!number) return ''
        return number.replace(/\D/g, '')
    }
}

export default whatsappService
