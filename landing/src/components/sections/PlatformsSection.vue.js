/// <reference types="../../../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
const platforms = [
    {
        id: 1,
        title: "Web Dashboard",
        description: "Powerful Vue.js dashboard with real-time updates and advanced features",
        icon: "fas fa-desktop",
        link: "https://dash.truledgr.app",
        linkText: "Visit Dashboard"
    },
    {
        id: 2,
        title: "iOS App",
        description: "Native Swift app with Touch ID, Face ID, and offline-first architecture",
        icon: "fab fa-apple",
        link: "#",
        linkText: "App Store"
    },
    {
        id: 3,
        title: "Android App",
        description: "Material Design app with fingerprint auth and seamless sync",
        icon: "fab fa-android",
        link: "#",
        linkText: "Google Play"
    },
    {
        id: 4,
        title: "Developer API",
        description: "RESTful API with OpenAPI documentation and SDKs",
        icon: "fas fa-code",
        link: "https://api.truledgr.app",
        linkText: "API Docs"
    }
];
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_elements;
let __VLS_components;
let __VLS_directives;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_elements.section, __VLS_elements.section)({
    id: "platforms",
    ...{ class: "platforms" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "container" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "section-header" },
});
__VLS_asFunctionalElement(__VLS_elements.h2, __VLS_elements.h2)({});
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "platforms-grid" },
});
for (const [platform] of __VLS_getVForSourceType((__VLS_ctx.platforms))) {
    // @ts-ignore
    [platforms,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        key: (platform.id),
        ...{ class: "platform-card" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "platform-icon" },
    });
    __VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
        ...{ class: (platform.icon) },
    });
    __VLS_asFunctionalElement(__VLS_elements.h3, __VLS_elements.h3)({});
    (platform.title);
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({});
    (platform.description);
    __VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
        href: (platform.link),
        ...{ class: "platform-link" },
    });
    (platform.linkText);
    __VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
        ...{ class: "fas fa-arrow-right" },
    });
}
/** @type {__VLS_StyleScopedClasses['platforms']} */ ;
/** @type {__VLS_StyleScopedClasses['container']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['platforms-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['platform-card']} */ ;
/** @type {__VLS_StyleScopedClasses['platform-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['platform-link']} */ ;
/** @type {__VLS_StyleScopedClasses['fas']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-arrow-right']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        platforms: platforms,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
