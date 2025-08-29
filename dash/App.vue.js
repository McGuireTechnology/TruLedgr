/// <reference types="../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useUIStore } from '@/stores/ui';
import Navbar from '@/components/layout/Navbar.vue';
const route = useRoute();
const authStore = useAuthStore();
const uiStore = useUIStore();
const isLoginPage = computed(() => route.name === 'login');
const isMobileMenuOpen = computed(() => uiStore.isMobileMenuOpen);
const closeMobileMenu = () => {
    uiStore.closeMobileMenu();
};
onMounted(async () => {
    // Check if user is authenticated on app load
    await authStore.checkAuth();
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_elements;
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    id: "app",
    ...{ class: "min-h-screen bg-gray-50" },
});
if (!__VLS_ctx.authStore.initialized) {
    // @ts-ignore
    [authStore,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "flex items-center justify-center min-h-screen" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "text-center" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto" },
    });
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
        ...{ class: "mt-4 text-gray-600" },
    });
}
else {
    if (!__VLS_ctx.isLoginPage) {
        // @ts-ignore
        [isLoginPage,];
        /** @type {[typeof Navbar, ]} */ ;
        // @ts-ignore
        const __VLS_0 = __VLS_asFunctionalComponent(Navbar, new Navbar({}));
        const __VLS_1 = __VLS_0({}, ...__VLS_functionalComponentArgsRest(__VLS_0));
    }
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: ({ 'ml-64': !__VLS_ctx.isLoginPage && !__VLS_ctx.isMobileMenuOpen, 'ml-0': __VLS_ctx.isLoginPage || __VLS_ctx.isMobileMenuOpen }) },
    });
    // @ts-ignore
    [isLoginPage, isLoginPage, isMobileMenuOpen, isMobileMenuOpen,];
    const __VLS_4 = {}.RouterView;
    /** @type {[typeof __VLS_components.RouterView, typeof __VLS_components.routerView, ]} */ ;
    // @ts-ignore
    RouterView;
    // @ts-ignore
    const __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4({}));
    const __VLS_6 = __VLS_5({}, ...__VLS_functionalComponentArgsRest(__VLS_5));
    if (__VLS_ctx.isMobileMenuOpen && !__VLS_ctx.isLoginPage) {
        // @ts-ignore
        [isLoginPage, isMobileMenuOpen,];
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ onClick: (__VLS_ctx.closeMobileMenu) },
            ...{ class: "fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden" },
        });
        // @ts-ignore
        [closeMobileMenu,];
    }
}
/** @type {__VLS_StyleScopedClasses['min-h-screen']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gray-50']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['min-h-screen']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['animate-spin']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-full']} */ ;
/** @type {__VLS_StyleScopedClasses['h-12']} */ ;
/** @type {__VLS_StyleScopedClasses['w-12']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border-primary-600']} */ ;
/** @type {__VLS_StyleScopedClasses['mx-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-gray-600']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-64']} */ ;
/** @type {__VLS_StyleScopedClasses['ml-0']} */ ;
/** @type {__VLS_StyleScopedClasses['fixed']} */ ;
/** @type {__VLS_StyleScopedClasses['inset-0']} */ ;
/** @type {__VLS_StyleScopedClasses['z-40']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gray-600']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-opacity-75']} */ ;
/** @type {__VLS_StyleScopedClasses['lg:hidden']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        Navbar: Navbar,
        authStore: authStore,
        isLoginPage: isLoginPage,
        isMobileMenuOpen: isMobileMenuOpen,
        closeMobileMenu: closeMobileMenu,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
