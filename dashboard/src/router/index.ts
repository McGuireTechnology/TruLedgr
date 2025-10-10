import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView
    }
  ]
})

// Navigation guard for authentication
// TODO: Replace with actual auth check (e.g., check for JWT token in localStorage)
router.beforeEach((to, from, next) => {
  const isAuthenticated = false // Replace with: !!localStorage.getItem('authToken')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if trying to access protected route
    next('/login')
  } else if ((to.name === 'login' || to.name === 'signup') && isAuthenticated) {
    // Redirect to dashboard if already authenticated
    next('/')
  } else {
    next()
  }
})

export default router
