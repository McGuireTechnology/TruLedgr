import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
// @ts-ignore - package.json is not typed
import packageJson from '../package.json'

const app = createApp(App)

// Provide app version globally
app.provide('appVersion', packageJson.version)

app.use(createPinia())
app.use(router)

app.mount('#app')
