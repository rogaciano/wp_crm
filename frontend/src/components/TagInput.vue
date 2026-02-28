<template>
  <div class="tag-input-wrapper">
    <!-- Pills das tags selecionadas -->
    <div class="flex flex-wrap gap-1.5 mb-1.5" v-if="selectedTags.length > 0">
      <span
        v-for="tag in selectedTags"
        :key="tag.id"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold transition-all"
        :style="{ backgroundColor: tag.cor + '22', color: tag.cor, borderColor: tag.cor + '55', border: '1px solid' }"
      >
        <span class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ backgroundColor: tag.cor }"></span>
        {{ tag.nome }}
        <button
          v-if="!readonly"
          type="button"
          @click="removeTag(tag.id)"
          class="ml-0.5 hover:opacity-70 transition-opacity leading-none"
          :style="{ color: tag.cor }"
        >
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>
    </div>

    <!-- Input de busca/criação (oculto em readonly) -->
    <div v-if="!readonly" class="relative" ref="wrapperRef">
      <div class="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-50 border border-gray-100 focus-within:border-primary-400 focus-within:bg-white transition-colors">
        <svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
        <input
          ref="inputRef"
          v-model="inputText"
          type="text"
          class="flex-1 bg-transparent text-xs text-gray-700 focus:outline-none placeholder-gray-400 min-w-0"
          :placeholder="placeholder"
          @input="onInput"
          @keydown.enter.prevent="onEnter"
          @keydown.escape="closeDropdown"
          @focus="showDropdown = true"
        />
        <span v-if="loading" class="text-gray-300">
          <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
        </span>
      </div>

      <!-- Dropdown de sugestões -->
      <div
        v-if="showDropdown && (filteredSuggestions.length > 0 || inputText.trim())"
        class="absolute left-0 top-full mt-1 w-full bg-white shadow-xl rounded-lg border border-gray-100 z-50 overflow-hidden"
      >
        <!-- Opção de criar nova tag -->
        <div
          v-if="inputText.trim() && !exactMatch"
          @click="createAndAdd"
          class="flex items-center gap-2 px-3 py-2 hover:bg-primary-50 cursor-pointer border-b border-gray-50 transition-colors"
        >
          <div class="w-4 h-4 rounded-full flex items-center justify-center text-white text-[10px] font-black" :style="{ backgroundColor: newTagColor }">+</div>
          <span class="text-xs text-gray-700">Criar <b>{{ inputText.trim() }}</b></span>
          <!-- Seletor de cor rápido -->
          <div class="flex gap-1 ml-auto">
            <button
              v-for="color in colorPalette"
              :key="color"
              type="button"
              @click.stop="newTagColor = color"
              class="w-4 h-4 rounded-full border-2 transition-transform hover:scale-110"
              :style="{ backgroundColor: color, borderColor: newTagColor === color ? color : 'transparent' }"
            />
          </div>
        </div>

        <!-- Sugestões existentes -->
        <div class="max-h-40 overflow-y-auto custom-scrollbar">
          <div
            v-for="tag in filteredSuggestions"
            :key="tag.id"
            @click="addTag(tag)"
            class="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <span class="w-3 h-3 rounded-full shrink-0" :style="{ backgroundColor: tag.cor }"></span>
            <span class="text-xs text-gray-700 flex-1">{{ tag.nome }}</span>
            <span v-if="isSelected(tag.id)" class="text-primary-500">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
            </span>
          </div>

          <div v-if="filteredSuggestions.length === 0 && !inputText.trim()" class="px-3 py-2 text-xs text-gray-400 italic">
            Nenhuma tag disponível
          </div>
        </div>
      </div>

      <!-- Backdrop para fechar dropdown -->
      <div v-if="showDropdown" class="fixed inset-0 z-40" @click="closeDropdown" />
    </div>

    <!-- Mensagem vazio (readonly) -->
    <p v-if="readonly && selectedTags.length === 0" class="text-xs text-gray-400 italic">Sem etiquetas</p>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '@/services/api'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  tagsDetail: {
    type: Array,
    default: () => []
  },
  readonly: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: 'Adicionar etiqueta...'
  }
})

const emit = defineEmits(['update:modelValue', 'update:tagsDetail'])

const inputText = ref('')
const showDropdown = ref(false)
const loading = ref(false)
const allTags = ref([])
const newTagColor = ref('#6C5CE7')
const inputRef = ref(null)
const wrapperRef = ref(null)

const colorPalette = [
  '#6C5CE7', '#00B894', '#0984E3', '#E17055',
  '#FDCB6E', '#A29BFE', '#55EFC4', '#FD79A8'
]

// Tags selecionadas com detalhes (para exibir pills)
const selectedTags = computed(() => {
  if (props.tagsDetail && props.tagsDetail.length > 0) {
    // Usar tagsDetail se disponível
    return props.tagsDetail.filter(t => props.modelValue.includes(t.id))
  }
  // Fallback: buscar em allTags
  return allTags.value.filter(t => props.modelValue.includes(t.id))
})

const filteredSuggestions = computed(() => {
  const q = inputText.value.trim().toLowerCase()
  return allTags.value.filter(t =>
    (!q || t.nome.toLowerCase().includes(q)) && !isSelected(t.id)
  )
})

const exactMatch = computed(() => {
  const q = inputText.value.trim().toLowerCase()
  return allTags.value.some(t => t.nome.toLowerCase() === q)
})

function isSelected(id) {
  return props.modelValue.includes(id)
}

async function loadTags() {
  try {
    const res = await api.get('/tags/', { params: { page_size: 200 } })
    allTags.value = res.data.results || res.data
  } catch (e) {
    console.error('Erro ao carregar tags:', e)
  }
}

let debounceTimer = null
function onInput() {
  showDropdown.value = true
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {}, 300)
}

function onEnter() {
  if (inputText.value.trim()) {
    // Verifica se há match exato
    const found = allTags.value.find(
      t => t.nome.toLowerCase() === inputText.value.trim().toLowerCase()
    )
    if (found) {
      addTag(found)
    } else {
      createAndAdd()
    }
  }
}

function addTag(tag) {
  if (!isSelected(tag.id)) {
    const newIds = [...props.modelValue, tag.id]
    const newDetail = [...(props.tagsDetail || []).filter(t => newIds.includes(t.id))]
    if (!newDetail.find(t => t.id === tag.id)) newDetail.push(tag)
    emit('update:modelValue', newIds)
    emit('update:tagsDetail', newDetail)
    // Garantir que está em allTags
    if (!allTags.value.find(t => t.id === tag.id)) {
      allTags.value.push(tag)
    }
  }
  inputText.value = ''
  showDropdown.value = false
  inputRef.value?.focus()
}

function removeTag(id) {
  const newIds = props.modelValue.filter(i => i !== id)
  const newDetail = (props.tagsDetail || []).filter(t => t.id !== id)
  emit('update:modelValue', newIds)
  emit('update:tagsDetail', newDetail)
}

async function createAndAdd() {
  const nome = inputText.value.trim()
  if (!nome) return
  loading.value = true
  try {
    const res = await api.post('/tags/', { nome, cor: newTagColor.value })
    const tag = res.data
    allTags.value.push(tag)
    addTag(tag)
    newTagColor.value = colorPalette[Math.floor(Math.random() * colorPalette.length)]
  } catch (e) {
    console.error('Erro ao criar tag:', e)
  } finally {
    loading.value = false
  }
}

function closeDropdown() {
  showDropdown.value = false
}

onMounted(() => {
  loadTags()
})
</script>
