import { watch } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import { useSession } from '../composables/useSession'
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/login', component: () => import('../views/LoginView.vue') },
    {
      path: '/',
      component: () => import('../views/DashboardView.vue'),
      meta: { title: 'Dashboard' },
    },
    {
      path: '/pipeline',
      component: () => import('../views/PipelineView.vue'),
      meta: { title: 'Pipeline' },
    },
    {
      path: '/target',
      component: () => import('../views/TargetView.vue'),
      meta: { title: 'Target' },
    },
    { path: '/tim', component: () => import('../views/TeamView.vue'), meta: { title: 'Tim' } },
    {
      path: '/history',
      component: () => import('../views/HistoryView.vue'),
      meta: { title: 'Riwayat' },
    },
    { path: '/pipeline/new', redirect: '/pipeline' },
    { path: '/pipeline/:id/edit', redirect: '/pipeline' },
    { path: '/analitik', redirect: '/' },
    { path: '/tim/:name', redirect: '/tim' },
    { path: '/bantuan', redirect: '/' },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
router.beforeEach(async (to) => {
  const session = useSession()
  await session.initialize()
  if (to.path !== '/login' && !session.user.value) return '/login'
  if (to.path === '/login' && session.user.value) return '/'
})
router.afterEach((to) => {
  document.title = (to.meta.title || 'Masuk') + ' · Pipeline Funding'
})
watch(useSession().user, (value) => {
  if (!value && router.currentRoute.value.path !== '/login') router.replace('/login')
})
export default router
