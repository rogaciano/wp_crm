import { defineStore } from 'pinia'
import api from '@/services/api'
import { whatsappService } from '@/services/whatsapp'

export const useWhatsappStore = defineStore('whatsapp', {
    state: () => ({
        unreadCounts: { novas: 0, oportunidades: 0, total: 0 },
        loading: false,
        error: null,
        lastUpdated: null,
        unreadCooldownUntil: 0,

        // Multiatendimento Inbox
        conversas: [],
        conversasLoading: false,
        conversasCooldownUntil: 0,
        canalAtual: null,
        canaisDisponiveis: [],
        funilFiltro: null,   // null | 'VENDAS' | 'SUPORTE' | 'POS_VENDA'

        // WebSocket
        ws: null,
        wsConectado: false,
        wsReconnectTimer: null,
    }),

    getters: {
        conversasFiltradas: (state) => {
            if (!state.funilFiltro) return state.conversas
            return state.conversas.filter(c => c.funil_tipo === state.funilFiltro)
        },
        totalNaoLidas: (state) => {
            return state.conversas.reduce((acc, c) => acc + (c.nao_lidas || 0), 0)
        },
    },

    actions: {
        // ──────────────────────────────
        // Unread counts (menu global)
        // ──────────────────────────────
        async fetchUnreadCounts() {
            if (Date.now() < this.unreadCooldownUntil) return
            if (this.loading) return
            this.loading = true
            try {
                const response = await api.get('/whatsapp/unread_counts/')
                this.unreadCounts = response.data
                this.lastUpdated = new Date()
                this.error = null
                this.unreadCooldownUntil = 0
            } catch (error) {
                console.error('Erro ao buscar mensagens não lidas:', error)
                if (error.response?.status === 429) {
                    const retryAfter = Number(error.response?.headers?.['retry-after']) || 60
                    this.unreadCooldownUntil = Date.now() + (retryAfter * 1000)
                }
                this.error = error.message
            } finally {
                this.loading = false
            }
        },

        // ──────────────────────────────
        // Inbox: Conversas & Canais
        // ──────────────────────────────
        async fetchCanais() {
            try {
                const res = await whatsappService.getCanaisAtendimento()
                this.canaisDisponiveis = res.data.canais || []
                if (!this.canalAtual && this.canaisDisponiveis.length > 0) {
                    this.canalAtual = this.canaisDisponiveis[0]
                }
            } catch (e) {
                console.error('[Atendimento] Erro ao carregar canais:', e)
            }
        },

        async fetchConversas() {
            if (Date.now() < this.conversasCooldownUntil) return
            if (this.conversasLoading) return
            this.conversasLoading = true
            try {
                const params = {}
                if (this.canalAtual?.id) params.canal_id = this.canalAtual.id
                if (this.funilFiltro) params.funil_tipo = this.funilFiltro

                const res = await whatsappService.getConversas(params)
                this.conversas = res.data.conversas || []
                this.conversasCooldownUntil = 0
                if (res.data.canal && !this.canalAtual) {
                    this.canalAtual = res.data.canal
                }
            } catch (e) {
                console.error('[Atendimento] Erro ao carregar conversas:', e)
                if (e.response?.status === 429) {
                    const retryAfter = Number(e.response?.headers?.['retry-after']) || 60
                    this.conversasCooldownUntil = Date.now() + (retryAfter * 1000)
                }
            } finally {
                this.conversasLoading = false
            }
        },

        setFunilFiltro(tipo) {
            this.funilFiltro = tipo
            this.fetchConversas()
        },

        setCanal(canal) {
            this.canalAtual = canal
            this.fetchConversas()
            this.conectarWebSocket()
        },

        // Insere ou atualiza uma conversa recebida via WebSocket
        upsertConversa(payload) {
            const idx = this.conversas.findIndex(c => c.numero === payload.numero)
            if (idx >= 0) {
                // Atualiza conversa existente
                const existente = this.conversas[idx]
                this.conversas.splice(idx, 1, {
                    ...existente,
                    ultima_mensagem: payload.ultima_mensagem,
                    ultima_mensagem_timestamp: payload.ultima_mensagem_timestamp,
                    nao_lidas: (existente.nao_lidas || 0) + 1,
                })
                // Move para o topo
                const updated = this.conversas.splice(idx, 1)[0]
                this.conversas.unshift(updated)
            } else {
                // Nova conversa: insere no topo
                this.conversas.unshift({
                    ...payload,
                    nao_lidas: 1,
                })
            }
        },

        marcarConversaLida(numero) {
            const idx = this.conversas.findIndex(c => c.numero === numero)
            if (idx >= 0) {
                this.conversas[idx] = { ...this.conversas[idx], nao_lidas: 0 }
            }
        },

        // ──────────────────────────────
        // WebSocket
        // ──────────────────────────────
        conectarWebSocket() {
            if (!this.canalAtual?.id) return

            this.desconectarWebSocket()

            const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
            if (!token) return

            const wsBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000')
                .replace(/^http/, 'ws')
                .replace(/\/api\/?$/, '')

            const url = `${wsBase}/ws/atendimento/${this.canalAtual.id}/?token=${token}`

            try {
                this.ws = new WebSocket(url)

                this.ws.onopen = () => {
                    this.wsConectado = true
                }

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data)
                        if (data.tipo === 'nova_mensagem' && data.conversa) {
                            this.upsertConversa(data.conversa)
                        }
                    } catch (e) {
                        console.error('[WS] Erro ao processar mensagem:', e)
                    }
                }

                this.ws.onclose = (event) => {
                    this.wsConectado = false
                    // Reconecta automaticamente (exceto se foi desconexão intencional ou erro de autenticação)
                    if (event.code !== 1000 && event.code !== 4001 && event.code !== 4003) {
                        this.wsReconnectTimer = setTimeout(() => this.conectarWebSocket(), 5000)
                    } else if (event.code === 4001 || event.code === 4003) {
                        console.error('[WS] Erro de autenticação/permissão. Não reconectando.')
                    }
                }

                this.ws.onerror = (e) => {
                    console.error('[WS] Erro na conexão:', e)
                }
            } catch (e) {
                console.error('[WS] Falha ao criar WebSocket:', e)
            }
        },

        desconectarWebSocket() {
            if (this.wsReconnectTimer) clearTimeout(this.wsReconnectTimer)
            if (this.ws) {
                this.ws.close(1000, 'Desconexão intencional')
                this.ws = null
            }
            this.wsConectado = false
        },
    },
})
