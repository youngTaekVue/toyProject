/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Composables
import { createVuetify } from 'vuetify'
// Styles
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'light', // Set default theme to 'light' for consistent color application
    themes: {
      light: {
        colors: {
          primary: '#1867C0', // Example primary color, adjust as needed
          secondary: '#5CBBF6', // Example secondary color, adjust as needed
          kpiRed: '#ef5350', // Custom red for KPI
          kpiBlue: '#42a5f5', // Custom blue for KPI
          kpiGreen: '#66bb6a', // Custom green for KPI
          kpiOrange: '#ffa726', // Custom orange for KPI
        },
      },
    },
  },
})