<template>
  <v-text-field
    :label="label"
    :model-value="displayValue"
    type="number"
    :min="min"
    :max="max"
    :step="step"
    :suffix="suffix"
    :disabled="disabled"
    @update:model-value="handleUpdate"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  modelValue: number;
  label: string;
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: number];
}>();

const displayValue = computed(() => Number.isFinite(props.modelValue) ? props.modelValue : 0);

function handleUpdate(value: string | number | null) {
  if (value === null || value === '') {
    emit('update:modelValue', 0);
    return;
  }
  emit('update:modelValue', Number(value));
}
</script>
