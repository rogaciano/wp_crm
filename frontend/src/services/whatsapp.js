import api from './api'

export const whatsappService = {
    // ==================== MENSAGENS ====================

    getMessages(params) {
        return api.get('/whatsapp/', { params })
    },

    sendMessage(data) {
        // data: { number, text, oportunidade }
        return api.post('/whatsapp/send/', data)
    },

    sendMedia(data) {
        // data: { number, media (base64), mediaType, fileName, caption, oportunidade }
        return api.post('/whatsapp/send_media/', data)
    },

    // Sincroniza mensagens da Evolution API para o banco local
    syncMessages(data) {
        // data: { number, oportunidade, limit }
        return api.post('/whatsapp/sync/', data)
    },

    // Marca mensagens como lidas
    marcarLidas(data) {
        // data: { number, oportunidade }
        return api.post('/whatsapp/marcar_lidas/', data)
    },

    // Busca contagem global de não lidas para o menu
    getUnreadCounts() {
        return api.get('/whatsapp/unread_counts/')
    },

    // Processa mídias pendentes (áudios, imagens) quando o chat abre
    processPendingMedia(number) {
        return api.post('/whatsapp/process_pending_media/', { number })
    },

    // Busca uma mensagem completa (com media_base64) pelo ID
    getMessage(id) {
        return api.get(`/whatsapp/${id}/`)
    },

    // Baixa apenas o áudio (sem transcrever)
    getAudio(messageId) {
        return api.post('/whatsapp/get_audio/', { message_id: messageId })
    },

    // Transcreve um áudio específico por ID
    transcribeAudio(messageId) {
        return api.post('/whatsapp/transcribe_audio/', { message_id: messageId })
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

    // ==================== ATENDIMENTO (INBOX) ====================

    // Lista conversas do canal (inbox multiatendimento)
    getConversas(params) {
        // params: { canal_id?, funil_tipo?, search? }
        return api.get('/atendimento/conversas/', { params })
    },

    // Lista canais disponíveis (para seletor admin)
    getCanaisAtendimento() {
        return api.get('/atendimento/canais/')
    },
}

export default whatsappService
