<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">Gestão de Usuários</h1>
      <button class="btn btn-primary w-full sm:w-auto shadow-sm">+ Novo Usuário</button>
    </div>

    <div class="card overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else>
        <!-- Desktop Table -->
        <div class="hidden md:block overflow-x-auto">
          <table class="table">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">Nome</th>
                <th class="table-header">Email</th>
                <th class="table-header">Perfil</th>
                <th class="table-header">Canal</th>
                <th class="table-header">Status</th>
                <th class="table-header text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="usuario in usuarios" :key="usuario.id" class="hover:bg-gray-50">
                <td class="table-cell font-medium text-gray-900">
                  {{ usuario.first_name }} {{ usuario.last_name }}
                </td>
                <td class="table-cell text-gray-500">{{ usuario.email }}</td>
                <td class="table-cell">
                  <span :class="getPerfilClass(usuario.perfil)">
                    {{ getPerfilLabel(usuario.perfil) }}
                  </span>
                </td>
                <td class="table-cell text-gray-500">{{ usuario.canal_nome || 'N/A' }}</td>
                <td class="table-cell">
                  <span :class="usuario.is_active ? 'text-green-600 font-medium' : 'text-red-600 font-medium'">
                    {{ usuario.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td class="table-cell text-right">
                  <div class="flex justify-end space-x-3">
                    <button class="text-primary-600 hover:text-primary-700 font-medium">Editar</button>
                    <button class="text-red-600 hover:text-red-700 font-medium">Desativar</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden divide-y divide-gray-100">
          <div v-for="usuario in usuarios" :key="usuario.id" class="p-4">
            <div class="flex justify-between items-start mb-2">
              <div>
                <h3 class="font-bold text-gray-900 leading-tight">
                  {{ usuario.first_name }} {{ usuario.last_name }}
                </h3>
                <p class="text-xs text-gray-500 mt-0.5">{{ usuario.email }}</p>
              </div>
              <span :class="getPerfilClass(usuario.perfil)">
                {{ getPerfilLabel(usuario.perfil) }}
              </span>
            </div>
            
            <div class="flex items-center justify-between mt-4">
               <div>
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Canal</p>
                  <p class="text-xs font-medium text-gray-700">{{ usuario.canal_nome || 'N/A' }}</p>
               </div>
               <div class="text-right">
                  <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Status</p>
                  <span :class="[usuario.is_active ? 'text-green-600' : 'text-red-600', 'text-xs font-bold uppercase']">
                     {{ usuario.is_active ? 'Ativo' : 'Inativo' }}
                  </span>
               </div>
            </div>

            <div class="flex justify-end space-x-6 border-t pt-3 mt-4">
              <button class="text-xs font-bold text-primary-600 uppercase tracking-widest">Editar</button>
              <button class="text-xs font-bold text-red-600 uppercase tracking-widest">Desativar</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const usuarios = ref([])
const loading = ref(false)

onMounted(() => {
  loadUsuarios()
})

async function loadUsuarios() {
  loading.value = true
  try {
    const response = await api.get('/usuarios/')
    usuarios.value = response.data.results || response.data
  } catch (error) {
    console.error('Erro ao carregar usuários:', error)
  } finally {
    loading.value = false
  }
}

function getPerfilLabel(perfil) {
  const labels = {
    'ADMIN': 'Administrador',
    'RESPONSAVEL': 'Responsável',
    'VENDEDOR': 'Vendedor'
  }
  return labels[perfil] || perfil
}

function getPerfilClass(perfil) {
  const classes = {
    'ADMIN': 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800',
    'RESPONSAVEL': 'px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800',
    'VENDEDOR': 'px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800'
  }
  return classes[perfil] || 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800'
}
</script>
