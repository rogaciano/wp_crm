import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/diagnostico',
      name: 'diagnostico',
      component: () => import('@/views/public/DiagnosisView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/diagnostico/resultado',
      name: 'diagnostico-resultado',
      component: () => import('@/views/public/DiagnosisResultView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          redirect: '/dashboard'
        },
        {
          path: '/dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue')
        },
        {
          path: '/kanban',
          name: 'kanban',
          component: () => import('@/views/KanbanView.vue')
        },
        {
          path: '/leads',
          name: 'leads',
          component: () => import('@/views/LeadsView.vue')
        },
        {
          path: '/contas',
          name: 'contas',
          component: () => import('@/views/ContasView.vue')
        },
        {
          path: '/contas/:id',
          name: 'conta-detail',
          component: () => import('@/views/ContaDetailView.vue')
        },
        {
          path: '/contatos',
          name: 'contatos',
          component: () => import('@/views/ContatosView.vue')
        },
        {
          path: '/oportunidades',
          name: 'oportunidades',
          component: () => import('@/views/OportunidadesView.vue')
        },
        {
          path: '/atividades',
          name: 'atividades',
          component: () => import('@/views/AtividadesView.vue')
        },
        {
          path: '/config/funis',
          name: 'admin-funis',
          component: () => import('@/views/admin/FunisView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/tipos-contato',
          name: 'admin-tipos-contato',
          component: () => import('@/views/admin/TiposContatoView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/canais',
          name: 'admin-canais',
          component: () => import('@/views/admin/CanaisView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/usuarios',
          name: 'admin-usuarios',
          component: () => import('@/views/admin/UsuariosView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/estagios',
          name: 'admin-estagios',
          component: () => import('@/views/admin/EstagiosView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/planos',
          name: 'admin-planos',
          component: () => import('@/views/admin/PlanosView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/whatsapp',
          name: 'admin-whatsapp',
          component: () => import('@/views/admin/WhatsappView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/logs',
          name: 'admin-logs',
          component: () => import('@/views/admin/LogsView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/config/organograma',
          name: 'admin-organograma',
          component: () => import('@/views/admin/OrganogramaView.vue'),
          meta: { requiresAdmin: true }
        }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
  } else {
    // Busca dados do usuário se necessário
    if (authStore.isAuthenticated && !authStore.user) {
      await authStore.fetchUser()
    }
    next()
  }
})

export default router
