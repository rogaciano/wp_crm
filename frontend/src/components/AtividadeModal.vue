<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Atividade' : 'Nova Atividade'"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Título <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.titulo"
            type="text"
            required
            class="input"
            placeholder="Ex: Ligar para prospecto"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Tipo <span class="text-red-500">*</span>
          </label>
          <select v-model="form.tipo" required class="input">
            <option value="TAREFA">Tarefa</option>
            <option value="LIGACAO">Ligação</option>
            <option value="REUNIAO">Reunião</option>
            <option value="EMAIL">E-mail</option>
            <option value="NOTA">Nota</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select v-model="form.status" class="input" :disabled="!isEdit">
            <option value="Pendente">Pendente</option>
            <option value="Concluída">Concluída</option>
            <option value="Cancelada">Cancelada</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Data de Vencimento
          </label>
          <input
            v-model="form.data_vencimento"
            type="datetime-local"
            class="input"
          />
        </div>

        <div v-if="!associationFixed">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Associado a
          </label>
          <div class="flex gap-2">
            <select v-model="selectedType" class="input w-1/3" @change="handleTypeChange">
              <option value="">Selecione...</option>
              <option v-for="ct in contentTypes" :key="ct.id" :value="ct.id">
                {{ ct.nome }}
              </option>
            </select>
            <select v-model="form.object_id" class="input flex-1" :disabled="!selectedType">
              <option value="">Selecione o registro...</option>
              <option v-for="obj in objectsList" :key="obj.id" :value="obj.id">
                {{ obj.display_name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Descrição
        </label>
        <textarea
          v-model="form.descricao"
          rows="3"
          class="input"
          placeholder="Detalhes da atividade..."
        ></textarea>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  atividade: Object,
  associationFixed: Boolean, // Se true, não permite trocar a associação (fixo via props parent)
  initialAssociation: Object // { content_type: ID, object_id: ID }
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const isEdit = ref(false)
const contentTypes = ref([])
const selectedType = ref('')
const objectsList = ref([])

const form = ref({
  titulo: '',
  tipo: 'TAREFA',
  status: 'Pendente',
  data_vencimento: '',
  descricao: '',
  content_type: '',
  object_id: ''
})

onMounted(() => {
  fetchContentTypes()
})

async function fetchContentTypes() {
  try {
    const response = await api.get('/atividades/content_types/')
    contentTypes.value = response.data
  } catch (error) {
    console.error('Erro ao carregar tipos de conteúdo:', error)
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.atividade) {
      isEdit.value = true
      form.value = { ...props.atividade }
      // Formatar data para input datetime-local (YYYY-MM-DDThh:mm)
      if (form.value.data_vencimento) {
        const date = new Date(form.value.data_vencimento)
        form.value.data_vencimento = date.toISOString().slice(0, 16)
      }
      selectedType.value = form.value.content_type
      fetchObjects(selectedType.value)
    } else {
      isEdit.value = false
      resetForm()
      if (props.initialAssociation) {
        form.value.content_type = props.initialAssociation.content_type
        form.value.object_id = props.initialAssociation.object_id
        selectedType.value = props.initialAssociation.content_type
      }
    }
  }
})

function resetForm() {
  form.value = {
    titulo: '',
    tipo: 'TAREFA',
    status: 'Pendente',
    data_vencimento: '',
    descricao: '',
    content_type: '',
    object_id: ''
  }
  selectedType.value = ''
  objectsList.value = []
}

async function handleTypeChange() {
  form.value.content_type = selectedType.value
  form.value.object_id = ''
  if (selectedType.value) {
    fetchObjects(selectedType.value)
  } else {
    objectsList.value = []
  }
}

async function fetchObjects(typeId) {
  const ct = contentTypes.value.find(c => c.id === typeId)
  if (!ct) return

  loading.value = true
  try {
    let endpoint = ''
    switch (ct.model) {
      case 'lead': endpoint = '/leads/'; break
      case 'conta': endpoint = '/contas/'; break
      case 'contato': endpoint = '/contatos/'; break
      case 'oportunidade': endpoint = '/oportunidades/'; break
    }

    if (endpoint) {
      const response = await api.get(endpoint)
      const results = response.data.results || response.data
      
      objectsList.value = results.map(obj => ({
        id: obj.id,
        display_name: obj.nome || obj.nome_empresa || obj.titulo || `ID: ${obj.id}`
      }))
    }
  } catch (error) {
    console.error('Erro ao buscar objetos:', error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!form.value.content_type || !form.value.object_id) {
    alert('Por favor, selecione a quem esta atividade está associada.')
    return
  }

  loading.value = true
  try {
    const data = { ...form.value }
    
    // Garantir que IDs sejam números
    data.content_type = parseInt(data.content_type)
    data.object_id = parseInt(data.object_id)

    // Formatar data para o backend (ISO String) ou remover se vazia
    if (data.data_vencimento && data.data_vencimento !== '') {
      data.data_vencimento = new Date(data.data_vencimento).toISOString()
    } else {
      data.data_vencimento = null
    }

    // Remover campos que o backend não aceita ou que são read-only
    delete data.proprietario_nome
    delete data.data_criacao
    delete data.data_atualizacao
    delete data.data_conclusao

    if (isEdit.value) {
      await api.put(`/atividades/${data.id}/`, data)
    } else {
      await api.post('/atividades/', data)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Erro ao salvar atividade:', error)
    const errorMsg = error.response?.data 
      ? JSON.stringify(error.response.data) 
      : error.message
    alert('Erro ao salvar atividade: ' + errorMsg)
  } finally {
    loading.value = false
  }
}
</script>
