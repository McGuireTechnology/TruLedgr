import { defineStore } from 'pinia';
import { ref } from 'vue';
export const useUIStore = defineStore('ui', () => {
    const isMobileMenuOpen = ref(false);
    const theme = ref('light');
    const sidebarCollapsed = ref(false);
    const toggleMobileMenu = () => {
        isMobileMenuOpen.value = !isMobileMenuOpen.value;
    };
    const closeMobileMenu = () => {
        isMobileMenuOpen.value = false;
    };
    const openMobileMenu = () => {
        isMobileMenuOpen.value = true;
    };
    const toggleTheme = () => {
        theme.value = theme.value === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', theme.value);
    };
    const toggleSidebar = () => {
        sidebarCollapsed.value = !sidebarCollapsed.value;
        localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed.value));
    };
    const initializeTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            theme.value = savedTheme;
        }
    };
    const initializeSidebar = () => {
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState) {
            sidebarCollapsed.value = savedState === 'true';
        }
    };
    return {
        isMobileMenuOpen,
        theme,
        sidebarCollapsed,
        toggleMobileMenu,
        closeMobileMenu,
        openMobileMenu,
        toggleTheme,
        toggleSidebar,
        initializeTheme,
        initializeSidebar
    };
});
