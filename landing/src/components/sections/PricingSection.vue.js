/// <reference types="../../../node_modules/.vue-global-types/vue_3.5_0.d.ts" />
const pricingPlans = [
    {
        id: 1,
        name: "Starter",
        price: 0,
        features: [
            "Up to 100 transactions",
            "Basic reporting",
            "Mobile apps",
            "Email support"
        ],
        link: "https://dash.truledgr.app/signup?plan=starter",
        buttonText: "Get Started",
        buttonClass: "btn btn-outline"
    },
    {
        id: 2,
        name: "Professional",
        price: 29,
        features: [
            "Unlimited transactions",
            "Advanced analytics",
            "API access",
            "Priority support",
            "Custom integrations"
        ],
        link: "https://dash.truledgr.app/signup?plan=pro",
        buttonText: "Start Free Trial",
        buttonClass: "btn btn-primary",
        featured: true,
        badge: "Most Popular"
    },
    {
        id: 3,
        name: "Enterprise",
        price: 99,
        features: [
            "Everything in Pro",
            "White-label options",
            "Dedicated support",
            "Custom development",
            "SLA guarantee"
        ],
        link: "mailto:sales@truledgr.app",
        buttonText: "Contact Sales",
        buttonClass: "btn btn-outline"
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
    id: "pricing",
    ...{ class: "pricing" },
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
    ...{ class: "pricing-grid" },
});
for (const [plan] of __VLS_getVForSourceType((__VLS_ctx.pricingPlans))) {
    // @ts-ignore
    [pricingPlans,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        key: (plan.id),
        ...{ class: "pricing-card" },
        ...{ class: ({ featured: plan.featured }) },
    });
    if (plan.badge) {
        __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
            ...{ class: "pricing-badge" },
        });
        (plan.badge);
    }
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "pricing-header" },
    });
    __VLS_asFunctionalElement(__VLS_elements.h3, __VLS_elements.h3)({});
    (plan.name);
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({
        ...{ class: "price" },
    });
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "currency" },
    });
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "amount" },
    });
    (plan.price);
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)({
        ...{ class: "period" },
    });
    __VLS_asFunctionalElement(__VLS_elements.ul, __VLS_elements.ul)({
        ...{ class: "pricing-features" },
    });
    for (const [feature] of __VLS_getVForSourceType((plan.features))) {
        __VLS_asFunctionalElement(__VLS_elements.li, __VLS_elements.li)({
            key: (feature),
        });
        __VLS_asFunctionalElement(__VLS_elements.i, __VLS_elements.i)({
            ...{ class: "fas fa-check" },
        });
        (feature);
    }
    __VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)({
        href: (plan.link),
        ...{ class: (plan.buttonClass) },
    });
    (plan.buttonText);
}
/** @type {__VLS_StyleScopedClasses['pricing']} */ ;
/** @type {__VLS_StyleScopedClasses['container']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['pricing-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['pricing-card']} */ ;
/** @type {__VLS_StyleScopedClasses['featured']} */ ;
/** @type {__VLS_StyleScopedClasses['pricing-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['pricing-header']} */ ;
/** @type {__VLS_StyleScopedClasses['price']} */ ;
/** @type {__VLS_StyleScopedClasses['currency']} */ ;
/** @type {__VLS_StyleScopedClasses['amount']} */ ;
/** @type {__VLS_StyleScopedClasses['period']} */ ;
/** @type {__VLS_StyleScopedClasses['pricing-features']} */ ;
/** @type {__VLS_StyleScopedClasses['fas']} */ ;
/** @type {__VLS_StyleScopedClasses['fa-check']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup: () => ({
        pricingPlans: pricingPlans,
    }),
});
export default (await import('vue')).defineComponent({});
; /* PartiallyEnd: #4569/main.vue */
