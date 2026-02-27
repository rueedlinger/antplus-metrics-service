<template>
  <div
    role="alert"
    class="w-80 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-xl bg-white/20 border border-white/25 transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl"
  >
    <!-- Header -->
    <div
      :class="headerClass"
      class="flex justify-between items-center px-4 py-2 font-semibold rounded-t-2xl text-white text-sm sm:text-base"
    >
      <span class="truncate">{{ title }}</span>
      <button
        class="ml-4 font-bold hover:text-white/70 transition-colors text-lg"
        @click="$emit('close')"
        aria-label="Close toast"
      >
        &times;
      </button>
    </div>

    <!-- Body -->
    <div :class="bodyClass" class="px-4 py-3 text-sm sm:text-base rounded-b-2xl leading-relaxed">
      <p class="break-words">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { ToastType } from '../constants/toastType.js';

const props = defineProps({
  type: { type: String, default: ToastType.SUCCESS },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
});

defineEmits(['close']);

/* Gradient headers based on toast type */
const headerClass = computed(() => {
  switch (props.type) {
    case ToastType.SUCCESS:
      return 'bg-gradient-to-r from-purple-500 to-blue-400';
    case ToastType.ERROR:
      return 'bg-gradient-to-r from-red-500 to-red-700';
    case ToastType.INFO:
      return 'bg-gradient-to-r from-yellow-400 to-yellow-500';
    default:
      return 'bg-gray-600';
  }
});

/* Glassy semi-transparent body with readable text */
const bodyClass = computed(() => {
  switch (props.type) {
    case ToastType.SUCCESS:
      return 'bg-white/25 text-purple-800';
    case ToastType.ERROR:
      return 'bg-white/25 text-red-800';
    case ToastType.INFO:
      return 'bg-white/25 text-yellow-900';
    default:
      return 'bg-white/25 text-gray-900';
  }
});
</script>
