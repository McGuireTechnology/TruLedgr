/// <reference types="../../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
import { ref, onMounted, onUnmounted } from 'vue';
const isScrolled = ref(false);
const isMenuOpen = ref(false);
const handleScroll = () => {
    isScrolled.value = window.scrollY > 50;
};
const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value;
};
const closeMenu = () => {
    isMenuOpen.value = false;
};
onMounted(() => {
    window.addEventListener('scroll', handleScroll);
});
onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_elements;
let __VLS_components;
let __VLS_directives;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_elements.nav, __VLS_elements.nav)({
    ...{ class: "navbar" },
    ...{ class: ({ scrolled: __VLS_ctx.isScrolled }) },
});
// @ts-ignore
[isScrolled,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "nav-container" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "nav-brand" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "nav-logo" },
});
__VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
    ...{ class: "fas fa-chart-line" },
});
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
    ...{ class: "nav-title" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "nav-menu" },
    ...{ class: ({ active: __VLS_ctx.isMenuOpen }) },
    id: "nav-menu",
});
// @ts-ignore
[isMenuOpen,];
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    ...{ onClick: (__VLS_ctx.closeMenu) },
    href: "#features",
    ...{ class: "nav-link" },
});
// @ts-ignore
[closeMenu,];
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    ...{ onClick: (__VLS_ctx.closeMenu) },
    href: "#platforms",
    ...{ class: "nav-link" },
});
// @ts-ignore
[closeMenu,];
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    ...{ onClick: (__VLS_ctx.closeMenu) },
    href: "#pricing",
    ...{ class: "nav-link" },
});
// @ts-ignore
[closeMenu,];
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    ...{ onClick: (__VLS_ctx.closeMenu) },
    href: "#contact",
    ...{ class: "nav-link" },
});
// @ts-ignore
[closeMenu,];
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    href: "https://dash.truledgr.app",
    ...{ class: "nav-link nav-cta" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ onClick: (__VLS_ctx.toggleMenu) },
    ...{ class: "nav-toggle" },
    ...{ class: ({ active: __VLS_ctx.isMenuOpen }) },
});
// @ts-ignore
[isMenuOpen, toggleMenu,];
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
    ...{ class: "bar" },
});
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
    ...{ class: "bar" },
});
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
    ...{ class: "bar" },
});
/** @type {__VLS_StyleScopedClasses['navbar']} */ ;
/** @type {__VLS_StyleScopedClasses['scrolled']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-container']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-brand']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-logo']} */ ;
/** @type {__VLS_StyleScopedClasses['fas']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-chart-line']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-title']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-menu']} */ ;
/** @type {__VLS_StyleScopedClasses['active']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-link']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-link']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-link']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-link']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-link']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-cta']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-toggle']} */ ;
/** @type {__VLS_StyleScopedClasses['active']} */ ;
/** @type {__VLS_StyleScopedClasses['bar']} */ ;
/** @type {__VLS_StyleScopedClasses['bar']} */ ;
/** @type {__VLS_StyleScopedClasses['bar']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        isScrolled: isScrolled,
        isMenuOpen: isMenuOpen,
        toggleMenu: toggleMenu,
        closeMenu: closeMenu,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
