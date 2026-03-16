import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';

import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

export const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'stowageTheme',
    themes: {
      stowageTheme: {
        dark: false,
        colors: {
          primary: '#0f5c73',
          secondary: '#4f6d7a',
          accent: '#c57b14',
          success: '#2e7d32',
          warning: '#d17b0f',
          error: '#b3261e',
          info: '#4c6faf',
          surface: '#ffffff',
          background: '#f2f5f8',
        },
      },
    },
  },
  defaults: {
    VCard: {
      rounded: 'xl',
      elevation: 2,
    },
    VBtn: {
      rounded: 'lg',
      variant: 'flat',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      hideDetails: 'auto',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
      hideDetails: 'auto',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      hideDetails: 'auto',
    },
    VAutocomplete: {
      variant: 'outlined',
      density: 'comfortable',
      hideDetails: 'auto',
    },
    VSwitch: {
      color: 'primary',
      hideDetails: 'auto',
    },
    VCheckbox: {
      color: 'primary',
      hideDetails: 'auto',
    },
  },
});
