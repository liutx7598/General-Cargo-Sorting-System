<template>
  <v-app>
    <router-view />
    <v-snackbar
      v-model="ui.snackbar.visible"
      :color="ui.snackbar.color"
      :timeout="ui.snackbar.timeout"
      location="top"
    >
      {{ ui.snackbar.text }}
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { useUiStore } from '@/store/ui';

const ui = useUiStore();
</script>
