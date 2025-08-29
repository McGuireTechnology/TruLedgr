/// <reference types="../../../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
const features = [
    {
        id: 1,
        title: "Lightning Fast",
        description: "Built with FastAPI for maximum performance. Sub-second response times guaranteed.",
        icon: "fas fa-tachometer-alt"
    },
    {
        id: 2,
        title: "Bank-Level Security",
        description: "JWT authentication, encrypted data, and biometric support for ultimate security.",
        icon: "fas fa-shield-alt"
    },
    {
        id: 3,
        title: "Mobile First",
        description: "Native iOS and Android apps with offline capabilities and real-time sync.",
        icon: "fas fa-mobile-alt"
    },
    {
        id: 4,
        title: "Cloud Native",
        description: "Deployed on Digital Ocean with auto-scaling and 99.9% uptime guarantee.",
        icon: "fas fa-cloud"
    },
    {
        id: 5,
        title: "Advanced Analytics",
        description: "Real-time insights, custom reports, and predictive analytics powered by AI.",
        icon: "fas fa-chart-bar"
    },
    {
        id: 6,
        title: "Developer API",
        description: "RESTful API with comprehensive documentation for seamless integrations.",
        icon: "fas fa-code"
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
    id: "features",
    ...{ class: "features" },
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
    ...{ class: "features-grid" },
});
for (const [feature] of __VLS_getVForSourceType((__VLS_ctx.features))) {
    // @ts-ignore
    [features,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        key: (feature.id),
        ...{ class: "feature-card" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "feature-icon" },
    });
    __VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
        ...{ class: (feature.icon) },
    });
    __VLS_asFunctionalElement(__VLS_elements.h3, __VLS_elements.h3)({});
    (feature.title);
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({});
    (feature.description);
}
/** @type {__VLS_StyleScopedClasses['features']} */ ;
/** @type {__VLS_StyleScopedClasses['container']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['features-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['feature-card']} */ ;
/** @type {__VLS_StyleScopedClasses['feature-icon']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        features: features,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
