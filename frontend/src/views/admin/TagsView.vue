<template>
  <div class="space-y-6">
    <!-- Cabeçalho -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Tags / Etiquetas</h1>
        <p class="text-sm text-gray-500 mt-1">Gerencie as etiquetas usadas em oportunidades, contatos e empresas.</p>
      </div>
      <button @click="openCreateForm" class="btn btn-primary w-full sm:w-auto shadow-sm">
        + Nova Etiqueta
      </button>
    </div>

    <!-- Busca -->
    <div class="card p-4">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="search"
          type="text"
          placeholder="Buscar etiqueta..."
          class="flex-1 bg-transparent text-sm text-gray-700 focus:outline-none placeholder-gray-400"
        />
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
          {{ filteredTags.length }} etiquetas
        </span>
      </div>
    </div>

    <!-- Formulário de criação inline -->
    <div v-if="showCreateForm" class="card p-5 border-2 border-primary-100 bg-primary-50/30">
      <h3 class="text-sm font-black text-gray-700 uppercase tracking-widest mb-4">Nova Etiqueta</h3>
      <div class="flex flex-col sm:flex-row items-start sm:items-end gap-4">
        <div class="flex-1">
          <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Nome</label>
          <input
            v-model="newTag.nome"
            type="text"
            class="input w-full"
            placeholder="Ex: VIP, Urgente, Potencial..."
            @keydown.enter="saveNewTag"
          />
        </div>
        <div>
          <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Cor</label>
          <div class="flex gap-2 items-center">
            <div class="flex gap-1.5 flex-wrap">
              <button
                v-for="color in colorPalette"
                :key="color"
                type="button"
                @click="newTag.cor = color"
                class="w-6 h-6 rounded-full border-2 transition-transform hover:scale-110"
                :style="{ backgroundColor: color, borderColor: newTag.cor === color ? '#111' : 'transparent' }"
              />
            </div>
            <input type="color" v-model="newTag.cor" class="w-8 h-8 rounded cursor-pointer border border-gray-200" />
          </div>
        </div>
        <div class="flex items-center gap-2">
          <!-- Preview pill -->
          <span
            class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold"
            :style="{ backgroundColor: newTag.cor + '22', color: newTag.cor, border: `1px solid ${newTag.cor}55` }"
          >
            <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: newTag.cor }"></span>
            {{ newTag.nome || 'Preview' }}
          </span>
        </div>
      </div>
      <div class="flex gap-2 mt-4 justify-end">
        <button @click="cancelCreate" class="btn btn-secondary text-sm">Cancelar</button>
        <button @click="saveNewTag" :disabled="!newTag.nome.trim() || saving" class="btn btn-primary text-sm">
          {{ saving ? 'Salvando...' : 'Criar Etiqueta' }}
        </button>
      </div>
    </div>

    <!-- Lista de Tags -->
    <div class="card p-0 overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="filteredTags.length === 0" class="text-center py-12 text-gray-400">
        <svg class="w-12 h-12 mx-auto mb-3 text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
        <p class="font-medium text-sm">Nenhuma etiqueta encontrada</p>
      </div>

      <div v-else class="divide-y divide-gray-100">
        <div
          v-for="tag in filteredTags"
          :key="tag.id"
          class="flex flex-col sm:flex-row sm:items-center gap-4 p-4 md:p-5 hover:bg-gray-50/50 transition-colors"
        >
          <!-- Pill + Edit inline -->
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <!-- Seletor de cor -->
            <div class="relative group/color shrink-0">
              <div
                class="w-8 h-8 rounded-full cursor-pointer shadow-sm border-2 border-white hover:scale-110 transition-transform"
                :style="{ backgroundColor: tag.cor }"
                @click="openColorPicker(tag)"
              ></div>
              <div
                v-if="editingColorId === tag.id"
                class="absolute left-0 top-full mt-1 z-50 bg-white rounded-xl shadow-xl border border-gray-100 p-3"
              >
                <div class="flex gap-1.5 flex-wrap mb-2">
                  <button
                    v-for="color in colorPalette"
                    :key="color"
                    @click.stop="applyColor(tag, color)"
                    class="w-6 h-6 rounded-full border-2 hover:scale-110 transition-transform"
                    :style="{ backgroundColor: color, borderColor: tag.cor === color ? '#111' : 'transparent' }"
                  />
                </div>
                <input type="color" :value="tag.cor" @input="applyColor(tag, $event.target.value)" class="w-full h-6 rounded cursor-pointer" />
                <button @click="editingColorId = null" class="mt-1 text-xs text-gray-400 hover:text-gray-600 w-full text-center">Fechar</button>
              </div>
              <!-- Backdrop color picker -->
              <div v-if="editingColorId === tag.id" class="fixed inset-0 z-40" @click="editingColorId = null" />
            </div>

            <!-- Nome editável -->
            <div class="flex-1 min-w-0">
              <input
                v-if="editingNameId === tag.id"
                :ref="el => { if (el) nameInputRefs[tag.id] = el }"
                v-model="tag._editName"
                class="text-sm font-bold text-gray-900 bg-transparent border-b border-primary-400 focus:outline-none w-full max-w-xs"
                @keydown.enter="saveName(tag)"
                @keydown.escape="cancelEditName(tag)"
                @blur="saveName(tag)"
              />
              <div v-else class="group/name flex items-center gap-2 cursor-pointer" @click="startEditName(tag)">
                <span class="text-sm font-bold text-gray-900">{{ tag.nome }}</span>
                <svg class="w-3 h-3 text-gray-300 opacity-0 group-hover/name:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Uso por entidade -->
          <div class="flex items-center gap-3 text-xs">
            <div class="flex items-center gap-1 text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg" title="Oportunidades">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="font-bold">{{ tag.uso_oportunidades }}</span>
            </div>
            <div class="flex items-center gap-1 text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg" title="Contatos">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span class="font-bold">{{ tag.uso_contatos }}</span>
            </div>
            <div class="flex items-center gap-1 text-amber-600 bg-amber-50 px-2 py-1 rounded-lg" title="Empresas">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span class="font-bold">{{ tag.uso_contas }}</span>
            </div>
          </div>

          <!-- Botão excluir (somente admin) -->
          <div class="flex items-center justify-end shrink-0">
            <button
              @click="confirmDelete(tag)"
              class="flex items-center gap-1 text-xs font-bold text-red-500 hover:text-red-700 hover:bg-red-50 px-2 py-1.5 rounded-lg transition-colors"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Excluir
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de confirmação de exclusão -->
    <div v-if="tagToDelete" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0">
            <svg class="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div>
            <h3 class="font-black text-gray-900">Excluir etiqueta</h3>
            <p class="text-sm text-gray-500">Esta ação não pode ser desfeita</p>
          </div>
        </div>

        <!-- Pill da tag a excluir -->
        <div class="bg-gray-50 rounded-xl p-4 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <span
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-bold"
              :style="{ backgroundColor: tagToDelete.cor + '22', color: tagToDelete.cor, border: `1px solid ${tagToDelete.cor}55` }"
            >
              <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: tagToDelete.cor }"></span>
              {{ tagToDelete.nome }}
            </span>
          </div>
          <div class="text-xs text-gray-600 space-y-1">
            <p v-if="tagToDelete.uso_oportunidades > 0">
              <span class="font-bold text-indigo-600">{{ tagToDelete.uso_oportunidades }}</span> oportunidade(s) serão desvinculadas
            </p>
            <p v-if="tagToDelete.uso_contatos > 0">
              <span class="font-bold text-emerald-600">{{ tagToDelete.uso_contatos }}</span> contato(s) serão desvinculados
            </p>
            <p v-if="tagToDelete.uso_contas > 0">
              <span class="font-bold text-amber-600">{{ tagToDelete.uso_contas }}</span> empresa(s) serão desvinculadas
            </p>
            <p v-if="tagToDelete.total_uso === 0" class="text-gray-400 italic">
              Esta etiqueta não está vinculada a nenhum registro.
            </p>
          </div>
        </div>

        <div class="flex gap-3 justify-end">
          <button @click="tagToDelete = null" class="btn btn-secondary">Cancelar</button>
          <button @click="deleteTag" :disabled="deleting" class="btn btn-danger">
            {{ deleting ? 'Excluindo...' : 'Sim, excluir' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import api from '@/services/api'

const tags = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const search = ref('')
const showCreateForm = ref(false)
const tagToDelete = ref(null)
const editingColorId = ref(null)
const editingNameId = ref(null)
const nameInputRefs = ref({})

const colorPalette = [
  '#6C5CE7', '#00B894', '#0984E3', '#E17055',
  '#FDCB6E', '#A29BFE', '#74B9FF', '#FD79A8',
  '#636E72', '#00CEC9', '#D63031', '#2D3436'
]

const newTag = ref({ nome: '', cor: '#6C5CE7' })

const filteredTags = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return tags.value
  return tags.value.filter(t => t.nome.toLowerCase().includes(q))
})

async function loadTags() {
  loading.value = true
  try {
    const res = await api.get('/tags/', { params: { page_size: 500 } })
    tags.value = (res.data.results || res.data).map(t => ({ ...t, _editName: t.nome }))
  } catch (e) {
    console.error('Erro ao carregar tags:', e)
  } finally {
    loading.value = false
  }
}

function openCreateForm() {
  newTag.value = { nome: '', cor: colorPalette[0] }
  showCreateForm.value = true
}

function cancelCreate() {
  showCreateForm.value = false
  newTag.value = { nome: '', cor: '#6C5CE7' }
}

async function saveNewTag() {
  if (!newTag.value.nome.trim()) return
  saving.value = true
  try {
    const res = await api.post('/tags/', { nome: newTag.value.nome.trim(), cor: newTag.value.cor })
    tags.value.unshift({ ...res.data, _editName: res.data.nome })
    cancelCreate()
  } catch (e) {
    alert(e.response?.data?.nome?.[0] || 'Erro ao criar etiqueta.')
  } finally {
    saving.value = false
  }
}

function openColorPicker(tag) {
  editingColorId.value = editingColorId.value === tag.id ? null : tag.id
}

async function applyColor(tag, color) {
  tag.cor = color
  try {
    await api.patch(`/tags/${tag.id}/`, { cor: color })
  } catch (e) {
    console.error('Erro ao salvar cor:', e)
  }
}

function startEditName(tag) {
  tag._editName = tag.nome
  editingNameId.value = tag.id
  nextTick(() => {
    nameInputRefs.value[tag.id]?.focus()
    nameInputRefs.value[tag.id]?.select()
  })
}

async function saveName(tag) {
  if (!tag._editName?.trim() || tag._editName === tag.nome) {
    cancelEditName(tag)
    return
  }
  try {
    await api.patch(`/tags/${tag.id}/`, { nome: tag._editName.trim() })
    tag.nome = tag._editName.trim()
  } catch (e) {
    alert(e.response?.data?.nome?.[0] || 'Erro ao salvar nome.')
    tag._editName = tag.nome
  }
  editingNameId.value = null
}

function cancelEditName(tag) {
  tag._editName = tag.nome
  editingNameId.value = null
}

function confirmDelete(tag) {
  tagToDelete.value = tag
}

async function deleteTag() {
  if (!tagToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/tags/${tagToDelete.value.id}/`)
    tags.value = tags.value.filter(t => t.id !== tagToDelete.value.id)
    tagToDelete.value = null
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir etiqueta.')
  } finally {
    deleting.value = false
  }
}

onMounted(loadTags)
</script>
