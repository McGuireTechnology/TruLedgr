import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: () => import('@/views/auth/LoginView.vue'),
            meta: { requiresGuest: true },
        },
        {
            path: '/',
            name: 'dashboard',
            component: () => import('@/views/DashboardView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/users',
            name: 'users',
            component: () => import('@/views/users/UsersView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/users/:id',
            name: 'user-detail',
            component: () => import('@/views/users/UserDetailView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/groups',
            name: 'groups',
            component: () => import('@/views/groups/GroupsView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/groups/:id',
            name: 'group-detail',
            component: () => import('@/views/groups/GroupDetailView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/groups/:id/edit',
            name: 'group-edit',
            component: () => import('@/views/groups/GroupEditView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/items',
            name: 'items',
            component: () => import('@/views/items/ItemsView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/roles',
            name: 'roles',
            component: () => import('@/views/authorization/RolesView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/permissions',
            name: 'permissions',
            component: () => import('@/views/permissions/PermissionsView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/security',
            name: 'security',
            component: () => import('@/views/security/SecurityView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/settings',
            name: 'settings',
            component: () => import('@/views/SettingsView.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'not-found',
            component: () => import('@/views/NotFoundView.vue'),
        },
    ],
});
// Navigation guards
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();
    // Wait for auth initialization if not already done
    if (!authStore.initialized) {
        await authStore.checkAuth();
    }
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/login');
    }
    else if (to.meta.requiresGuest && authStore.isAuthenticated) {
        next('/');
    }
    else {
        next();
    }
});
export default router;
