<template>
  <tr :class="inactive ? 'bg-gray-100 text-gray-400' : ''">
    <td class="border border-gray-200 px-4 py-2">{{ label }}</td>
    <td class="border border-gray-200 px-4 py-2">
      <div
        v-if="zoneColor"
        class="w-4 h-4 inline-block rounded-full mr-2"
        :style="{ backgroundColor: zoneColor }"
      ></div>
      <span>{{ formattedValue }}</span>
    </td>
    <td class="border border-gray-200 px-4 py-2">
      <div
        v-if="maZoneColor"
        class="w-4 h-4 inline-block rounded-full mr-2"
        :style="{ backgroundColor: maZoneColor }"
      ></div>
      <span v-if="movingAverage !== null">{{ formatValue(movingAverage) }}</span>
      <span v-else>—</span>
    </td>
  </tr>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  label: { type: String, default: '' },
  value: { type: [String, Number, Boolean], default: '' },
  movingAverage: { type: [String, Number, Boolean, null], default: null },
  inactive: { type: Boolean, default: false },
});

// Map of zones to colors
const zoneColors = {
  RESTING: '#E0E0E0',
  ZONE_1: '#A0A0A0',
  ZONE_2: '#ADD8E6',
  ZONE_3: '#2CA02C',
  ZONE_4: '#FFD700',
  ZONE_5: '#D62728',
};

// Format value
const formatValue = (val) => {
  if (val === null || val === undefined) return '—';
  if (typeof val === 'boolean') return val ? 'Yes' : 'No';
  if (typeof val === 'number') return val.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return val;
};

const formattedValue = computed(() => formatValue(props.value));

const zoneColor = computed(() => {
  if (!props.value) return null;
  return zoneColors[props.value] || null;
});

const maZoneColor = computed(() => {
  if (!props.movingAverage) return null;
  return zoneColors[props.movingAverage] || null;
});
</script>
