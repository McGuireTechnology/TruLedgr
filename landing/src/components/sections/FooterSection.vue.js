/// <reference types="../../../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
const footerSections = [
    {
        title: "Product",
        links: [
            { text: "Features", url: "#features" },
            { text: "Pricing", url: "#pricing" },
            { text: "API", url: "https://api.truledgr.app" },
            { text: "Documentation", url: "https://docs.truledgr.app" }
        ]
    },
    {
        title: "Platforms",
        links: [
            { text: "Web Dashboard", url: "https://dash.truledgr.app" },
            { text: "iOS App", url: "#" },
            { text: "Android App", url: "#" },
            { text: "Developer API", url: "https://api.truledgr.app" }
        ]
    },
    {
        title: "Company",
        links: [
            { text: "About", url: "#about" },
            { text: "Careers", url: "#careers" },
            { text: "Blog", url: "#blog" },
            { text: "Contact", url: "mailto:support@truledgr.app" }
        ]
    },
    {
        title: "Resources",
        links: [
            { text: "Documentation", url: "https://docs.truledgr.app" },
            { text: "Support", url: "#support" },
            { text: "Privacy Policy", url: "#privacy" },
            { text: "Terms of Service", url: "#terms" }
        ]
    }
];
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_elements;
let __VLS_components;
let __VLS_directives;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_elements.footer, __VLS_elements.footer)({
    id: "contact",
    ...{ class: "footer" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "container" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "footer-content" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "footer-section" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "footer-brand" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "footer-logo" },
});
__VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
    ...{ class: "fas fa-chart-line" },
});
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
    ...{ class: "footer-title" },
});
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({
    ...{ class: "footer-description" },
});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "footer-social" },
});
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    href: "https://github.com/McGuireTechnology",
    'aria-label': "GitHub",
});
__VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
    ...{ class: "fab fa-github" },
});
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    href: "#",
    'aria-label': "Twitter",
});
__VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
    ...{ class: "fab fa-twitter" },
});
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    href: "#",
    'aria-label': "LinkedIn",
});
__VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
    ...{ class: "fab fa-linkedin" },
});
for (const [section] of __VLS_getVForSourceType((__VLS_ctx.footerSections))) {
    // @ts-ignore
    [footerSections,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        key: (section.title),
        ...{ class: "footer-section" },
    });
    __VLS_asFunctionalElement(__VLS_elements.h4, __VLS_elements.h4)({});
    (section.title);
    for (const [link] of __VLS_getVForSourceType((section.links))) {
        __VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
            key: (link.text),
            href: (link.url),
        });
        (link.text);
    }
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "footer-bottom" },
});
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)({});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
    ...{ class: "footer-links" },
});
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    href: "#privacy",
});
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    href: "#terms",
});
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
    href: "#cookies",
});
/** @type {__VLS_StyleScopedClasses['footer']} */ ;
/** @type {__VLS_StyleScopedClasses['container']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-content']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-section']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-brand']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-logo']} */ ;
/** @type {__VLS_StyleScopedClasses['fas']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-chart-line']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-title']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-description']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-social']} */ ;
/** @type {__VLS_StyleScopedClasses['fab']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-github']} */ ;
/** @type {__VLS_StyleScopedClasses['fab']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-twitter']} */ ;
/** @type {__VLS_StyleScopedClasses['fab']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-linkedin']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-section']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-bottom']} */ ;
/** @type {__VLS_StyleScopedClasses['footer-links']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        footerSections: footerSections,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
