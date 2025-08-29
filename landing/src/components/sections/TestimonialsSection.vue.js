/// <reference types="../../../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
const testimonials = [
    {
        id: 1,
        content: "TruLedgr transformed our financial workflow. The mobile app is incredible and the API integration was seamless.",
        author: {
            name: "Sarah Chen",
            title: "CFO, TechStart Inc."
        }
    },
    {
        id: 2,
        content: "The best financial management platform we've used. Fast, secure, and the support team is outstanding.",
        author: {
            name: "Michael Rodriguez",
            title: "Founder, GrowthCo"
        }
    },
    {
        id: 3,
        content: "TruLedgr's analytics helped us identify cost savings worth $50k in the first quarter alone.",
        author: {
            name: "Emily Johnson",
            title: "Finance Director, Scale LLC"
        }
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
    ...{ class: "testimonials" },
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
    ...{ class: "testimonials-grid" },
});
for (const [testimonial] of __VLS_getVForSourceType((__VLS_ctx.testimonials))) {
    // @ts-ignore
    [testimonials,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        key: (testimonial.id),
        ...{ class: "testimonial-card" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "testimonial-content" },
    });
    (testimonial.content);
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "testimonial-author" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "author-avatar" },
    });
    __VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
        ...{ class: "fas fa-user" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "author-info" },
    });
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "author-name" },
    });
    (testimonial.author.name);
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "author-title" },
    });
    (testimonial.author.title);
}
/** @type {__VLS_StyleScopedClasses['testimonials']} */ ;
/** @type {__VLS_StyleScopedClasses['container']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['testimonials-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['testimonial-card']} */ ;
/** @type {__VLS_StyleScopedClasses['testimonial-content']} */ ;
/** @type {__VLS_StyleScopedClasses['testimonial-author']} */ ;
/** @type {__VLS_StyleScopedClasses['author-avatar']} */ ;
/** @type {__VLS_StyleScopedClasses['fas']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-user']} */ ;
/** @type {__VLS_StyleScopedClasses['author-info']} */ ;
/** @type {__VLS_StyleScopedClasses['author-name']} */ ;
/** @type {__VLS_StyleScopedClasses['author-title']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        testimonials: testimonials,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
