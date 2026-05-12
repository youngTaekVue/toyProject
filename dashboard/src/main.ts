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

// Components
import App from './App.vue'

// Styles
import 'unfonts.css'
import '@/styles/dashboard.scss' // Import the new dashboard styles
import '@/assets/main.css' // Import the global styles

const app = createApp(App)

registerPlugins(app)
app.use(router) // Use the router instance

app.mount('#app')
