<template>
  <BaseModal
    :show="show"
    title="Atualização em Lote de Endereços via CNPJ"
    size="xl"
    :show-footer="false"
    :close-on-backdrop="false"
    @close="handleClose"
  >
    <!-- Barra de ações -->
    <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
      <div class="text-sm text-gray-600">
        <span v-if="loading">Carregando empresas...</span>
        <span v-else>
          <strong>{{ rows.length }}</strong> empresa{{ rows.length !== 1 ? 's' : '' }} com endereço incompleto
        </span>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button
          type="button"
          class="btn btn-secondary text-sm"
          :disabled="buscando || confirmando || totalParaBuscar === 0"
          @click="buscarSelecionados"
        >
          <svg v-if="buscando" class="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
          </svg>
          <svg v-else class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 105 11a6 6 0 0012 0z"/>
          </svg>
          {{ buscando ? (pausando ? `Aguardando... (${progresso}/${totalParaBuscar})` : `Buscando ${progresso}/${totalParaBuscar}...`) : `Buscar ${totalParaBuscar} selecionada${totalParaBuscar !== 1 ? 's' : ''}` }}
        </button>

        <button
          type="button"
          class="btn btn-primary text-sm"
          :disabled="totalParaConfirmar === 0 || confirmando || buscando"
          @click="confirmarSelecionados"
        >
          <svg v-if="confirmando" class="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
          </svg>
          {{ confirmando ? 'Salvando...' : `Confirmar ${totalParaConfirmar} atualiza${totalParaConfirmar !== 1 ? 'ções' : 'ção'}` }}
        </button>

        <button type="button" class="btn btn-secondary text-sm" @click="handleClose" :disabled="buscando || confirmando">
          Fechar
        </button>
      </div>
    </div>

    <!-- Mensagem de resultado final -->
    <div v-if="resultadoFinal" class="mb-4 p-3 rounded-lg text-sm"
      :class="resultadoFinal.erro > 0 ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'bg-green-50 text-green-800 border border-green-200'">
      {{ resultadoFinal.msg }}
    </div>

    <!-- Loading inicial -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="w-8 h-8 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
      </svg>
    </div>

    <!-- Sem resultados -->
    <div v-else-if="rows.length === 0" class="text-center py-12 text-gray-500">
      <svg class="w-12 h-12 mx-auto mb-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p class="font-medium text-green-700">Todas as empresas já têm endereço completo!</p>
    </div>

    <!-- Tabela -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-200">
            <!-- Checkbox: Buscar -->
            <th class="px-3 py-2 text-center w-14">
              <div class="flex flex-col items-center gap-0.5">
                <input
                  type="checkbox"
                  :checked="todosBuscaSelecionados"
                  :indeterminate="algunsBuscaSelecionados && !todosBuscaSelecionados"
                  @change="toggleTodosBusca"
                  class="rounded border-gray-300"
                  :disabled="buscando || confirmando"
                  title="Selecionar todos para busca"
                />
                <span class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide">Buscar</span>
              </div>
            </th>
            <!-- Checkbox: Confirmar -->
            <th class="px-3 py-2 text-center w-16">
              <div class="flex flex-col items-center gap-0.5">
                <input
                  type="checkbox"
                  :checked="todosConfirmarSelecionados"
                  :indeterminate="algunsConfirmarSelecionados && !todosConfirmarSelecionados"
                  @change="toggleTodosConfirmar"
                  class="rounded border-gray-300"
                  :disabled="buscando || confirmando || rowsFound.length === 0"
                  title="Selecionar todos para confirmar"
                />
                <span class="text-[10px] font-semibold text-gray-500 uppercase tracking-wide">Confirmar</span>
              </div>
            </th>
            <th class="px-3 py-2 text-left text-gray-600 font-medium">Empresa</th>
            <th class="px-3 py-2 text-left text-gray-600 font-medium">CNPJ</th>
            <th class="px-3 py-2 text-left text-gray-600 font-medium">Status</th>
            <th class="px-3 py-2 text-left text-gray-600 font-medium">Endereço (preview)</th>
            <th class="px-3 py-2 text-left text-gray-600 font-medium">Cidade</th>
            <th class="px-3 py-2 text-center text-gray-600 font-medium w-10">UF</th>
            <th class="px-3 py-2 text-left text-gray-600 font-medium">CEP</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in rows"
            :key="row.conta.id"
            class="border-b border-gray-100 transition-colors"
            :class="{
              'bg-green-50': row.status === 'found' || row.status === 'updated',
              'bg-amber-50': row.status === 'not_found',
              'bg-red-50': row.status === 'error',
              'opacity-50': row.status === 'no_cnpj',
              'bg-blue-50': row.status === 'fetching',
            }"
          >
            <!-- Checkbox: Buscar -->
            <td class="px-3 py-2 text-center">
              <input
                type="checkbox"
                v-model="row.selecionadoBusca"
                :disabled="!row.conta.cnpj || buscando || confirmando || row.status === 'updated'"
                class="rounded border-gray-300"
                title="Incluir na busca"
              />
            </td>

            <!-- Checkbox: Confirmar -->
            <td class="px-3 py-2 text-center">
              <input
                type="checkbox"
                v-model="row.selecionadoConfirmar"
                :disabled="row.status !== 'found' || buscando || confirmando"
                class="rounded border-gray-300"
                title="Confirmar atualização"
              />
            </td>

            <!-- Nome -->
            <td class="px-3 py-2 font-medium text-gray-900 max-w-[180px] truncate" :title="row.conta.nome_empresa">
              {{ row.conta.nome_empresa }}
            </td>

            <!-- CNPJ -->
            <td class="px-3 py-2 text-gray-600 whitespace-nowrap">
              <span v-if="row.conta.cnpj">{{ row.conta.cnpj }}</span>
              <span v-else class="text-gray-400 italic">sem CNPJ</span>
            </td>

            <!-- Status badge -->
            <td class="px-3 py-2 whitespace-nowrap">
              <span v-if="row.status === 'idle'" class="text-gray-400 text-xs">Aguardando</span>
              <span v-else-if="row.status === 'no_cnpj'" class="text-gray-400 text-xs">Sem CNPJ</span>
              <span v-else-if="row.status === 'fetching'" class="flex items-center gap-1 text-blue-600 text-xs">
                <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                </svg>
                Buscando...
              </span>
              <span v-else-if="row.status === 'found'" class="text-green-600 text-xs font-medium">✓ Encontrado</span>
              <span v-else-if="row.status === 'not_found'" class="text-amber-600 text-xs">Não encontrado</span>
              <span v-else-if="row.status === 'error'" class="text-red-600 text-xs">Erro na API</span>
              <span v-else-if="row.status === 'updated'" class="text-green-700 text-xs font-medium">✓ Salvo</span>
            </td>

            <!-- Preview: Endereço -->
            <td class="px-3 py-2 text-gray-700 max-w-[200px] truncate" :title="row.preview?.endereco || row.conta.endereco || '—'">
              <span v-if="row.preview?.endereco" class="text-green-700">{{ row.preview.endereco }}</span>
              <span v-else-if="row.conta.endereco" class="text-gray-500">{{ row.conta.endereco }}</span>
              <span v-else class="text-gray-300">—</span>
            </td>

            <!-- Cidade -->
            <td class="px-3 py-2 text-gray-700 whitespace-nowrap">
              <span v-if="row.preview?.cidade" class="text-green-700">{{ row.preview.cidade }}</span>
              <span v-else-if="row.conta.cidade" class="text-gray-500">{{ row.conta.cidade }}</span>
              <span v-else class="text-gray-300">—</span>
            </td>

            <!-- Estado -->
            <td class="px-3 py-2 text-center text-gray-700 whitespace-nowrap">
              <span v-if="row.preview?.estado" class="text-green-700">{{ row.preview.estado }}</span>
              <span v-else-if="row.conta.estado" class="text-gray-500">{{ row.conta.estado }}</span>
              <span v-else class="text-gray-300">—</span>
            </td>

            <!-- CEP -->
            <td class="px-3 py-2 text-gray-700 whitespace-nowrap">
              <span v-if="row.preview?.cep" class="text-green-700">{{ row.preview.cep }}</span>
              <span v-else-if="row.conta.cep" class="text-gray-500">{{ row.conta.cep }}</span>
              <span v-else class="text-gray-300">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Legenda -->
    <div v-if="rows.length > 0" class="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
      <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm bg-green-100 border border-green-300 inline-block"></span> Dados encontrados</span>
      <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm bg-amber-100 border border-amber-300 inline-block"></span> CNPJ não encontrado na Receita Federal</span>
      <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-sm bg-red-100 border border-red-300 inline-block"></span> Erro de conexão</span>
      <span class="flex items-center gap-1 opacity-50"><span class="w-3 h-3 rounded-sm bg-gray-200 border border-gray-300 inline-block"></span> Sem CNPJ cadastrado</span>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'saved'])

// Estado
const loading = ref(false)
const buscando = ref(false)
const confirmando = ref(false)
const rows = ref([])
const progresso = ref(0)
const pausando = ref(false)
const resultadoFinal = ref(null)

// --- Computed: coluna Buscar ---
const rowsParaBuscar = computed(() => rows.value.filter(r => r.selecionadoBusca && r.conta.cnpj))
const totalParaBuscar = computed(() => rowsParaBuscar.value.length)

const rowsComCnpj = computed(() => rows.value.filter(r => r.conta.cnpj))
const todosBuscaSelecionados = computed(
  () => rowsComCnpj.value.length > 0 && rowsComCnpj.value.every(r => r.selecionadoBusca)
)
const algunsBuscaSelecionados = computed(() => rowsComCnpj.value.some(r => r.selecionadoBusca))

// --- Computed: coluna Confirmar ---
const rowsFound = computed(() => rows.value.filter(r => r.status === 'found'))
const totalParaConfirmar = computed(() => rows.value.filter(r => r.selecionadoConfirmar && r.status === 'found').length)

const todosConfirmarSelecionados = computed(
  () => rowsFound.value.length > 0 && rowsFound.value.every(r => r.selecionadoConfirmar)
)
const algunsConfirmarSelecionados = computed(() => rowsFound.value.some(r => r.selecionadoConfirmar))

// Carrega a lista quando o modal abre
watch(() => props.show, async (val) => {
  if (val) {
    await carregarEmpresas()
  } else {
    reset()
  }
})

async function carregarEmpresas() {
  loading.value = true
  resultadoFinal.value = null
  try {
    const res = await api.get('/contas/sem_endereco/')
    rows.value = res.data.map(conta => ({
      conta,
      status: conta.cnpj ? 'idle' : 'no_cnpj',
      selecionadoBusca: !!conta.cnpj,       // por padrão: todas com CNPJ selecionadas para busca
      selecionadoConfirmar: false,           // só ativo após encontrar dados
      preview: null,
    }))
  } catch (e) {
    console.error('Erro ao carregar empresas sem endereço:', e)
  } finally {
    loading.value = false
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function buscarSelecionados() {
  if (buscando.value) return
  buscando.value = true
  progresso.value = 0
  resultadoFinal.value = null

  const alvo = rowsParaBuscar.value

  for (const row of alvo) {
    const cnpjLimpo = row.conta.cnpj.replace(/\D/g, '')
    row.status = 'fetching'
    row.preview = null
    row.selecionadoConfirmar = false

    try {
      const res = await api.get(`/contas/buscar_cnpj/?cnpj=${cnpjLimpo}`)
      const data = res.data

      if (data.status === 'ERROR') {
        row.status = 'not_found'
      } else {
        const nomeEmpresaNovo = data.nome || data.fantasia || ''
        // Se marca estiver vazia, preserva o nome atual antes de sobrescrever com a razão social
        const marcaPreservar = !row.conta.marca?.trim() && nomeEmpresaNovo
          ? row.conta.nome_empresa
          : undefined

        row.preview = {
          endereco: [data.logradouro, data.numero, data.complemento, data.bairro]
            .filter(Boolean).join(', ') || '',
          cidade: data.municipio || '',
          estado: data.uf || '',
          cep: data.cep || '',
          nome_empresa: nomeEmpresaNovo,
          ...(marcaPreservar ? { marca: marcaPreservar } : {}),
          telefone_principal: data.telefone || '',
          email: data.email || '',
          setor: data.atividade_principal?.[0]?.text?.substring(0, 100) || '',
        }
        row.status = 'found'
        row.selecionadoConfirmar = true  // auto-seleciona para confirmar
      }
    } catch {
      row.status = 'error'
    }

    progresso.value++
    // A cada 3 requisições, pausa 5s para não ser bloqueado pela ReceitaWS
    if (progresso.value % 3 === 0 && progresso.value < alvo.length) {
      pausando.value = true
      await sleep(5000)
      pausando.value = false
    } else {
      await sleep(1200)
    }
  }

  buscando.value = false
}

function toggleTodosBusca(e) {
  const valor = e.target.checked
  rows.value.forEach(row => {
    if (row.conta.cnpj && row.status !== 'updated') row.selecionadoBusca = valor
  })
}

function toggleTodosConfirmar(e) {
  const valor = e.target.checked
  rows.value.forEach(row => {
    if (row.status === 'found') row.selecionadoConfirmar = valor
  })
}

async function confirmarSelecionados() {
  if (confirmando.value) return
  confirmando.value = true
  resultadoFinal.value = null

  const payload = rows.value
    .filter(r => r.selecionadoConfirmar && r.status === 'found')
    .map(r => ({ id: r.conta.id, ...r.preview }))

  try {
    const res = await api.post('/contas/atualizar_lote/', payload)
    const resultados = res.data

    let ok = 0
    let erro = 0
    resultados.forEach(r => {
      const row = rows.value.find(rw => rw.conta.id === r.id)
      if (row) {
        if (r.status === 'ok') {
          row.status = 'updated'
          row.selecionadoConfirmar = false
          row.selecionadoBusca = false
          ok++
        } else {
          row.status = 'error'
          erro++
        }
      }
    })

    resultadoFinal.value = {
      erro,
      msg: erro === 0
        ? `${ok} empresa${ok !== 1 ? 's' : ''} atualizada${ok !== 1 ? 's' : ''} com sucesso!`
        : `${ok} atualizada${ok !== 1 ? 's' : ''} com sucesso, ${erro} com erro.`,
    }

    emit('saved')
  } catch (e) {
    console.error('Erro ao salvar em lote:', e)
    resultadoFinal.value = { erro: 1, msg: 'Erro ao salvar. Tente novamente.' }
  } finally {
    confirmando.value = false
  }
}

function reset() {
  rows.value = []
  buscando.value = false
  confirmando.value = false
  pausando.value = false
  progresso.value = 0
  resultadoFinal.value = null
}

function handleClose() {
  if (buscando.value || confirmando.value) return
  emit('close')
}
</script>
