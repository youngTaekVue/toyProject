/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Composables
import { createApp } from 'vue'
// Components
import App from './App.vue'

// Plugins
import { registerPlugins } from '@/plugins'
import VueApexCharts from 'vue3-apexcharts';

// Styles
import 'unfonts.css'
import '@/styles/dashboard.scss'
import '@/assets/main.css'
import 'apexcharts/dist/apexcharts.css'; // 이 라인을 추가합니다.

const app = createApp(App)

registerPlugins(app)
app.use(VueApexCharts);

app.mount('#app')