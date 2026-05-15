/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Composables
import { createApp } from 'vue'

// Plugins
import { registerPlugins } from '@/plugins'
import router from '@/router' // Import the router instance
import VueApexCharts from 'vue3-apexcharts'; // VueApexCharts 임포트

// Components
import App from './App.vue'

// Styles
import 'unfonts.css'
import '@/styles/dashboard.scss' // Import the new dashboard styles
import '@/assets/main.css' // Import the global styles

const app = createApp(App)

registerPlugins(app)
app.use(router) // Use the router instance
app.use(VueApexCharts); // VueApexCharts 등록

app.mount('#app')
