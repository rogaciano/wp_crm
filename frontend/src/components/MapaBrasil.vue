<template>
  <div class="mapa-wrapper" :style="{ height: height }">
    <div ref="mapContainer" class="mapa-leaflet" :style="{ height: height }"></div>

    <!-- Legenda -->
    <div v-if="legendaItems.length > 0" class="mapa-legenda">
      <p class="legenda-titulo">Legenda</p>
      <div v-for="item in legendaItems" :key="item.key" class="legenda-item">
        <!-- Círculo para contas -->
        <span v-if="item.tipo === 'conta'" class="legenda-icone legenda-circulo" :style="{ backgroundColor: item.cor }"></span>
        <!-- Losango para oportunidades -->
        <span v-else class="legenda-icone legenda-losango" :style="{ backgroundColor: item.cor }"></span>
        <span class="legenda-label">{{ item.nome }}</span>
        <span class="legenda-count">{{ item.total }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const ESTADOS_BR = {
  AC: { lat: -9.0238,  lng: -70.8120, nome: 'Acre', zoom: 7 },
  AL: { lat: -9.5713,  lng: -36.7820, nome: 'Alagoas', zoom: 8 },
  AP: { lat: 1.4002,   lng: -51.7700, nome: 'Amapá', zoom: 7 },
  AM: { lat: -3.4168,  lng: -65.8560, nome: 'Amazonas', zoom: 6 },
  BA: { lat: -12.9718, lng: -41.7330, nome: 'Bahia', zoom: 7 },
  CE: { lat: -5.4984,  lng: -39.3200, nome: 'Ceará', zoom: 7 },
  DF: { lat: -15.7801, lng: -47.9292, nome: 'Distrito Federal', zoom: 10 },
  ES: { lat: -19.1834, lng: -40.3089, nome: 'Espírito Santo', zoom: 8 },
  GO: { lat: -15.8270, lng: -49.8360, nome: 'Goiás', zoom: 7 },
  MA: { lat: -5.4200,  lng: -45.4440, nome: 'Maranhão', zoom: 7 },
  MT: { lat: -12.6819, lng: -56.9210, nome: 'Mato Grosso', zoom: 6 },
  MS: { lat: -20.7722, lng: -54.7852, nome: 'Mato Grosso do Sul', zoom: 7 },
  MG: { lat: -18.5122, lng: -44.5550, nome: 'Minas Gerais', zoom: 7 },
  PA: { lat: -3.4168,  lng: -52.3240, nome: 'Pará', zoom: 6 },
  PB: { lat: -7.2400,  lng: -36.7820, nome: 'Paraíba', zoom: 8 },
  PR: { lat: -24.8950, lng: -51.5510, nome: 'Paraná', zoom: 7 },
  PE: { lat: -8.8137,  lng: -36.9540, nome: 'Pernambuco', zoom: 8 },
  PI: { lat: -7.7183,  lng: -42.7280, nome: 'Piauí', zoom: 7 },
  RJ: { lat: -22.9068, lng: -43.1729, nome: 'Rio de Janeiro', zoom: 8 },
  RN: { lat: -5.8127,  lng: -36.2720, nome: 'Rio Grande do Norte', zoom: 8 },
  RS: { lat: -30.0346, lng: -51.2177, nome: 'Rio Grande do Sul', zoom: 7 },
  RO: { lat: -10.8328, lng: -63.3440, nome: 'Rondônia', zoom: 7 },
  RR: { lat: 2.7376,   lng: -62.0750, nome: 'Roraima', zoom: 7 },
  SC: { lat: -27.2423, lng: -50.2189, nome: 'Santa Catarina', zoom: 7 },
  SP: { lat: -23.5505, lng: -46.6333, nome: 'São Paulo', zoom: 7 },
  SE: { lat: -10.5741, lng: -37.3860, nome: 'Sergipe', zoom: 9 },
  TO: { lat: -10.1753, lng: -48.2982, nome: 'Tocantins', zoom: 7 },
}

const PALETA_CORES = [
  '#F97316', '#10B981', '#3B82F6', '#8B5CF6',
  '#EF4444', '#EAB308', '#EC4899', '#06B6D4',
  '#84CC16', '#F59E0B', '#6366F1', '#14B8A6',
]

const props = defineProps({
  contas: { type: Array, default: () => [] },
  oportunidades: { type: Array, default: () => [] },
  canais: { type: Array, default: () => [] },
  height: { type: String, default: '400px' },
  zoomEstado: { type: String, default: null },      // UF para auto-zoom (ex: 'PE')
  corCanal: { type: String, default: null },         // cor fixa para view do canal
  mostrarOportunidades: { type: Boolean, default: true },
})

const emit = defineEmits(['selectConta', 'selectEstado', 'selectOportunidade'])

const mapContainer = ref(null)
let mapInstance = null
let markersLayer = null
let oppsLayer = null
let canaisLayer = null

// Mapa Canal ID → cor (gerado ou do campo `cor` do canal)
const canalCores = ref({})

const legendaItems = computed(() => {
  const items = []
  const contasMapa = {}
  const oppsMapa = {}

  props.contas.forEach(c => {
    const canalId = c.canal_id
    const cor = c.canal_cor || getCanalCor(canalId)
    const key = `conta-${canalId}`
    if (!contasMapa[key]) contasMapa[key] = { key, tipo: 'conta', nome: c.canal_nome, cor, total: 0 }
    contasMapa[key].total++
  })

  if (props.mostrarOportunidades) {
    props.oportunidades.forEach(o => {
      const canalId = o.canal_id
      const cor = o.canal_cor || getCanalCor(canalId)
      const key = `opp-${canalId}`
      if (!oppsMapa[key]) oppsMapa[key] = { key, tipo: 'oportunidade', nome: `${o.canal_nome} (Opps)`, cor, total: 0 }
      oppsMapa[key].total++
    })
  }

  items.push(...Object.values(contasMapa).sort((a, b) => b.total - a.total))
  items.push(...Object.values(oppsMapa).sort((a, b) => b.total - a.total))
  return items
})

function getCanalCor(canalId) {
  if (!canalId) return '#64748b'
  if (!canalCores.value[canalId]) {
    const idx = Object.keys(canalCores.value).length % PALETA_CORES.length
    canalCores.value[canalId] = PALETA_CORES[idx]
  }
  return canalCores.value[canalId]
}

function resolverCorConta(conta) {
  // Prioriza a cor real do canal salva no banco
  if (conta.canal_cor) return conta.canal_cor
  if (props.corCanal) return props.corCanal
  return getCanalCor(conta.canal_id)
}

function resolverCorOpp(opp) {
  if (opp.canal_cor) return opp.canal_cor
  if (props.corCanal) return props.corCanal
  return getCanalCor(opp.canal_id)
}

// Pré-carregar cores dos canais passados como prop
watch(() => props.canais, (canaisArr) => {
  canaisArr.forEach(c => {
    if (c.id && c.cor) canalCores.value[c.id] = c.cor
  })
}, { immediate: true })

function criarIconeConta(cor, count) {
  const L = window.L
  const size = count > 1 ? 36 : 28
  const html = count > 1
    ? `<div style="width:${size}px;height:${size}px;background:${cor};border:3px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:11px;box-shadow:0 2px 8px rgba(0,0,0,0.3)">${count}</div>`
    : `<div style="width:${size}px;height:${size}px;background:${cor};border:3px solid white;border-radius:50%;box-shadow:0 2px 8px rgba(0,0,0,0.3)"></div>`

  return L.divIcon({ html, className: '', iconSize: [size, size], iconAnchor: [size / 2, size / 2], popupAnchor: [0, -(size / 2)] })
}

function criarIconeOportunidade(cor, count) {
  const L = window.L
  const size = 30
  const inner = count > 1 ? `<span style="transform:rotate(-45deg);display:block;font-weight:bold;font-size:11px;color:white;text-align:center;line-height:${size}px">${count}</span>` : ''
  const html = `<div style="width:${size}px;height:${size}px;background:${cor};border:3px solid white;border-radius:4px;transform:rotate(45deg);box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center">${inner}</div>`
  return L.divIcon({ html, className: '', iconSize: [size, size], iconAnchor: [size / 2, size / 2], popupAnchor: [0, -(size / 2)] })
}

function statusLabel(s) {
  const map = { PROSPECT: 'Prospect', CLIENTE_ATIVO: 'Cliente Ativo', INATIVO: 'Inativo' }
  return map[s] || s
}

// === GEOCODING CACHE ===
const obterCoordenadas = (() => {
  const cache = JSON.parse(localStorage.getItem('crm_geocache') || '{}')
  let lastRequestTime = 0
  const RATE_LIMIT_MS = 1100 // 1.1s para respeitar a API pública do Nominatim

  const delay = (ms) => new Promise(r => setTimeout(r, ms))

  return async (cidade, uf) => {
    if (!cidade || !uf) return ESTADOS_BR[uf]
    const key = `${cidade.trim().toUpperCase()}-${uf.toUpperCase()}`
    
    // Retorna do cache se existir
    if (cache[key]) return cache[key]

    // Se não, agenda a requisição respeitando o rate limit
    const now = Date.now()
    const timeToWait = Math.max(0, lastRequestTime + RATE_LIMIT_MS - now)
    lastRequestTime = now + timeToWait
    if (timeToWait > 0) await delay(timeToWait)

    try {
       console.log(`Geocodificando: ${cidade}, ${uf}...`)
       // Tenta buscar "Cidade, UF, Brazil" via Nominatim
       const url = `https://nominatim.openstreetmap.org/search?city=${encodeURIComponent(cidade)}&state=${encodeURIComponent(uf)}&country=Brazil&format=json&limit=1`
       const res = await fetch(url)
       const data = await res.json()

       if (data && data.length > 0) {
         const coords = { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon), nome: `${cidade}/${uf}` }
         cache[key] = coords
         localStorage.setItem('crm_geocache', JSON.stringify(cache))
         return coords
       }
    } catch (e) {
       console.warn('Erro ao geocodificar:', e)
    }

    // Fallback: Centro do Estado
    const fallback = { ...ESTADOS_BR[uf], nome: `${cidade}/${uf} (Sede)` }
    cache[key] = fallback
    localStorage.setItem('crm_geocache', JSON.stringify(cache))
    return fallback
  }
})()

async function renderMarkers() {
  if (!mapInstance) return
  const L = window.L

  if (markersLayer) markersLayer.clearLayers()
  else markersLayer = L.layerGroup().addTo(mapInstance)

  const porLocal = {}
  props.contas.forEach(conta => {
    const uf = conta.estado?.toUpperCase()
    if (!uf || !ESTADOS_BR[uf]) return
    const cidade = conta.cidade ? conta.cidade.trim() : ''
    const chave = cidade ? `${cidade.toUpperCase()}-${uf}` : uf
    
    if (!porLocal[chave]) porLocal[chave] = { uf, cidade, contas: [] }
    porLocal[chave].contas.push(conta)
  })

  for (const [chave, dados] of Object.entries(porLocal)) {
    const { uf, cidade, contas } = dados
    // Tenta buscar a latitude/longitude da cidade (ou cai pro estado como fallback)
    const { lat, lng, nome } = cidade ? await obterCoordenadas(cidade, uf) : ESTADOS_BR[uf]
    const cor = resolverCorConta(contas[0])

    const icone = criarIconeConta(cor, contas.length)

    const linhas = contas.slice(0, 8).map(c =>
      `<div style="padding:4px 0;border-bottom:1px solid #f0f0f0;cursor:pointer" onclick="window.__mapaSelectConta(${c.id})">
        <div style="font-weight:600;font-size:12px;color:#111">${c.nome_empresa}</div>
        <div style="font-size:11px;color:#666">${c.cidade ? c.cidade + ' · ' : ''}${c.canal_nome} · <span style="color:${cor}">${statusLabel(c.status_cliente)}</span></div>
      </div>`
    ).join('')
    const maisLabel = contas.length > 8 ? `<div style="font-size:11px;color:#999;margin-top:4px">+${contas.length - 8} mais...</div>` : ''

    const popupContent = `
      <div style="min-width:200px;max-width:280px">
        <div style="font-weight:700;font-size:13px;margin-bottom:8px;color:#111">
          🏢 ${nome} (${contas.length} ${contas.length === 1 ? 'empresa' : 'empresas'})
        </div>
        ${linhas}${maisLabel}
      </div>`

    // Verifica de novo pois pode ter sido destruído no await
    if (!mapInstance || !markersLayer) return

    const marker = L.marker([lat, lng], { icon: icone })
      .bindPopup(popupContent, { maxWidth: 300 })
      .addTo(markersLayer)

    marker.on('click', () => emit('selectEstado', { uf, nome, contas, tipo: 'contas' }))
  }
}

async function renderOportunidades() {
  if (!mapInstance || !props.mostrarOportunidades) return
  const L = window.L

  if (oppsLayer) oppsLayer.clearLayers()
  else oppsLayer = L.layerGroup().addTo(mapInstance)

  const porLocal = {}
  props.oportunidades.forEach(opp => {
    // O backend já passa a cidade na oportunidade?
    // Atualmente as oportunidades só retornam `estado` e `empresa_nome`.
    // Se não houver cidade na prop da oportunidade, ele cairá na capital do Estado.
    // Daria pra extrair da conta, mas requer ajuste do backend se não estiver retornando a cidade da opp no momento.
    // Vamos agrupar pelo dado que temos (estado ou cidade futura)
    const uf = opp.estado?.toUpperCase()
    if (!uf || !ESTADOS_BR[uf]) return
    const cidade = opp.cidade ? opp.cidade.trim() : ''
    const chave = cidade ? `${cidade.toUpperCase()}-${uf}` : uf
    
    if (!porLocal[chave]) porLocal[chave] = { uf, cidade, opps: [] }
    porLocal[chave].opps.push(opp)
  })

  for (const [chave, dados] of Object.entries(porLocal)) {
    const { uf, cidade, opps } = dados
    const { lat, lng, nome } = cidade ? await obterCoordenadas(cidade, uf) : ESTADOS_BR[uf]
    const cor = resolverCorOpp(opps[0])

    const icone = criarIconeOportunidade(cor, opps.length)

    const linhas = opps.slice(0, 6).map(o =>
      `<div style="padding:4px 0;border-bottom:1px solid #f0f0f0">
        <div style="font-weight:600;font-size:12px;color:#111">${o.nome}</div>
        <div style="font-size:11px;color:#666">${o.empresa_nome ? o.empresa_nome + ' · ' : ''}${o.estagio_nome}</div>
        ${o.valor_estimado > 0 ? `<div style="font-size:11px;color:${cor};font-weight:600">R$ ${o.valor_estimado.toLocaleString('pt-BR')}</div>` : ''}
      </div>`
    ).join('')
    const maisLabel = opps.length > 6 ? `<div style="font-size:11px;color:#999;margin-top:4px">+${opps.length - 6} mais...</div>` : ''

    const popupContent = `
      <div style="min-width:200px;max-width:280px">
        <div style="font-weight:700;font-size:13px;margin-bottom:8px;color:${cor}">
          ◆ ${nome} — ${opps.length} oportunidade${opps.length !== 1 ? 's' : ''}
        </div>
        ${linhas}${maisLabel}
      </div>`

    if (!mapInstance || !oppsLayer) return

    L.marker([lat + 0.1, lng - 0.1], { icon: icone })
      .bindPopup(popupContent, { maxWidth: 300 })
      .addTo(oppsLayer)
  }
}

function renderCanais() {
  if (!mapInstance) return
  const L = window.L

  if (canaisLayer) canaisLayer.clearLayers()
  else canaisLayer = L.layerGroup().addTo(mapInstance)

  props.canais.forEach(canal => {
    const uf = canal.estado?.toUpperCase()
    if (!uf || !ESTADOS_BR[uf]) return

    const { lat, lng } = ESTADOS_BR[uf]
    // Usa a cor real do canal ou gera da paleta
    const cor = canal.cor || getCanalCor(canal.id)
    if (canal.id && canal.cor) canalCores.value[canal.id] = canal.cor

    const html = `<div style="width:40px;height:40px;background:${cor};border:3px solid white;border-radius:8px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:11px;box-shadow:0 3px 12px rgba(0,0,0,0.35);transform:rotate(45deg)">
      <span style="transform:rotate(-45deg);font-size:10px">${canal.nome.charAt(0).toUpperCase()}</span>
    </div>`

    const icone = L.divIcon({ html, className: '', iconSize: [40, 40], iconAnchor: [20, 20], popupAnchor: [0, -22] })

    const popupContent = `
      <div style="min-width:180px">
        <div style="font-weight:700;font-size:13px;margin-bottom:4px;color:${cor}">🏢 Canal: ${canal.nome}</div>
        <div style="font-size:12px;color:#555">Estado: <b>${uf}</b></div>
        ${canal.responsavel_nome ? `<div style="font-size:11px;color:#888;margin-top:4px">Responsável: ${canal.responsavel_nome}</div>` : ''}
      </div>`

    L.marker([lat + 0.3, lng + 0.3], { icon: icone })
      .bindPopup(popupContent, { maxWidth: 260 })
      .addTo(canaisLayer)
  })
}

function loadLeaflet() {
  return new Promise((resolve, reject) => {
    if (window.L) return resolve(window.L)
    
    // Adiciona o CSS
    if (!document.querySelector('link[href*="leaflet.css"]')) {
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
      document.head.appendChild(link)
    }

    // Adiciona o JS
    const script = document.createElement('script')
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    script.onload = () => resolve(window.L)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

async function initMap() {
  if (!mapContainer.value) return

  // Carrega pacotes do Leaflet via CDN
  const L = await loadLeaflet()

  // Evita reinicialização do erro "Map container is already initialized"
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }

  // Cria o mapa centrado no Brasil
  mapInstance = L.map(mapContainer.value).setView([-15.7801, -47.9292], 4)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(mapInstance)

  // Configuração global manual para ícones do Leaflet (Evita erro 404 de assets Vite/Rollup)
  L.Icon.Default.mergeOptions({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  window.__mapaSelectConta = (id) => {
    const conta = props.contas.find(c => c.id === id)
    if (conta) emit('selectConta', conta)
  }

  // Auto-zoom no estado do canal se informado
  if (props.zoomEstado) {
    const uf = props.zoomEstado.toUpperCase()
    const estado = ESTADOS_BR[uf]
    if (estado) {
      mapInstance.setView([estado.lat, estado.lng], estado.zoom || 7)
    }
  }

  renderMarkers()
  renderOportunidades()
  renderCanais()
}

// Função pública para zoom num estado
function zoomParaEstado(uf) {
  if (!mapInstance) return
  const estado = ESTADOS_BR[uf?.toUpperCase()]
  if (estado) mapInstance.flyTo([estado.lat, estado.lng], estado.zoom || 7, { duration: 1.2 })
}

defineExpose({ zoomParaEstado })

onMounted(() => initMap())

onUnmounted(() => {
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
  delete window.__mapaSelectConta
})

watch(() => props.contas, () => { if (mapInstance) renderMarkers() }, { deep: true })
watch(() => props.oportunidades, () => { if (mapInstance) renderOportunidades() }, { deep: true })
watch(() => props.canais, () => { if (mapInstance) renderCanais() }, { deep: true })
watch(() => props.zoomEstado, (uf) => { if (uf) zoomParaEstado(uf) })
</script>

<style scoped>
.mapa-wrapper {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.mapa-leaflet {
  width: 100%;
  z-index: 0;
}

.mapa-legenda {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: white;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  padding: 12px 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  z-index: 1000;
  min-width: 170px;
  max-height: 240px;
  overflow-y: auto;
}

.legenda-titulo {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #71717a;
  margin-bottom: 8px;
}

.legenda-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 12px;
}

.legenda-icone {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.legenda-circulo {
  border-radius: 50%;
}

.legenda-losango {
  border-radius: 2px;
  transform: rotate(45deg);
}

.legenda-label {
  color: #3f3f46;
  font-weight: 500;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.legenda-count {
  font-weight: 700;
  color: #18181b;
  font-size: 11px;
}
</style>
