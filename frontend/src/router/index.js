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
          path: '/admin/canais',
          name: 'admin-canais',
          component: () => import('@/views/admin/CanaisView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/admin/usuarios',
          name: 'admin-usuarios',
          component: () => import('@/views/admin/UsuariosView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/admin/estagios',
          name: 'admin-estagios',
          component: () => import('@/views/admin/EstagiosView.vue'),
          meta: { requiresAdmin: true }
        },
        {
          path: '/admin/planos',
          name: 'admin-planos',
          component: () => import('@/views/admin/PlanosView.vue'),
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
