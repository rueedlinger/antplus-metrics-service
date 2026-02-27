<template>
  <div
    class="backdrop-blur-lg bg-white/20 border border-white/20 rounded-2xl p-6 shadow-xl space-y-4"
  >
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-black">Live Metrics</h1>
      <div class="text-xs text-gray-500">
        {{ lastUpdated ? lastUpdated.toLocaleTimeString() : '—' }}
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-300">
      <nav class="-mb-px flex space-x-6">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'py-2 px-3 border-b-2 text-sm font-medium transition',
            activeTab === tab.id
              ? 'border-purple-500 text-purple-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div v-if="connected">
      <!-- METRICS TABLE -->
      <div v-if="activeTab === 'metrics'">
        <div class="overflow-x-auto rounded-lg shadow-inner">
          <table class="table-auto w-full text-sm border-separate border-spacing-0 bg-white/30">
            <thead>
              <tr class="bg-gradient-to-r from-purple-500 to-blue-400 text-white">
                <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Metric</th>
                <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Current</th>
                <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Average</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(value, key) in normalMetrics"
                :key="key"
                class="hover:bg-gray-50 transition"
              >
                <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
                  {{ friendlyLabels[key] ?? key }}
                  <span v-if="getMetricUnit(key)" class="text-gray-500 text-xs"
                    >({{ getMetricUnit(key) }})</span
                  >
                </td>
                <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
                  <span v-if="typeof value === 'number'">{{ Math.round(value) }}</span>
                  <span v-else>{{ value ?? '—' }}</span>
                  {{ getMetricUnit(key) }}
                </td>
                <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
                  <span v-if="typeof getMovingAverage(key) === 'number'">{{
                    Math.round(getMovingAverage(key))
                  }}</span>
                  <span v-else>{{ getMovingAverage(key) ?? '—' }}</span>
                  {{ getMetricUnit(key) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Footer -->
        <div class="mt-1 text-xs text-gray-500 space-x-2">
          <span v-for="key in footerKeys" :key="key"> {{ key }}: {{ footerValues[key] }} </span>
        </div>
      </div>

      <!-- CHART TAB -->
      <div v-else-if="activeTab === 'chart'">
        <div class="overflow-x-auto rounded-lg shadow-inner">
          <table
            class="table-auto text-sm border-separate border-spacing-0 bg-white/30 ml-0 mr-auto"
          >
            <tbody>
              <tr class="hover:bg-gray-50 transition">
                <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
                  Distance (m):
                </td>
                <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
                  {{ metrics.ma_distance ?? '—' }}
                </td>

                <td class="px-2 py-1 text-left border-b border-dashed border-black/30">Zone:</td>
                <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
                  {{ metrics.ma_zone_name ?? '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="group in chartGroups"
            :key="group.id"
            class="border rounded-lg bg-white/50 p-3 shadow-md"
          >
            <div
              class="flex justify-between items-center cursor-pointer"
              @click="toggleChart(group.id)"
            >
              <h2 class="text-gray-700 font-semibold capitalize">{{ group.label }}</h2>
              <span class="text-gray-500">{{ isChartOpen(group.id) ? '▼' : '►' }}</span>
            </div>
            <div v-show="isChartOpen(group.id)" class="h-64 mt-3">
              <Line :data="getChartDataForGroup(group)" :options="chartOptions" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Show warning when NOT connected -->
    <div v-else class="p-4 bg-red-100 text-red-600 rounded-lg">Not connected</div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
} from 'chart.js';
import { useMetricsStream } from '../composables/useStreams.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, CategoryScale);

// ---------------- STREAM ----------------
const { metrics, lastUpdated, connected } = useMetricsStream();

// ---------------- Tabs ----------------
const activeTab = ref('metrics');
const tabs = [
  { id: 'metrics', label: 'Metrics' },
  { id: 'chart', label: 'Chart' },
];

// ---------------- Units & Labels ----------------
const metricUnits = {
  power: 'W',
  speed: 'km/h',
  cadence: 'RPM',
  heart_rate: 'bpm',
  heart_rate_percent: '%',
  distance: 'm',
};
const friendlyLabels = {
  power: 'Power',
  speed: 'Speed',
  cadence: 'Cadence',
  heart_rate: 'Heart Rate',
  heart_rate_percent: 'Heart Rate',
  distance: 'Distance',
  zone_name: 'Zone',
  zone_description: 'Zone Description',
};
function getMetricUnit(metric) {
  return metricUnits[metric] ?? '';
}

// ---------------- Table Logic ----------------
const footerKeys = ['is_running', 'last_sensor_name', 'last_sensor_update'];
const normalMetrics = computed(() => {
  const data = metrics || {};
  const result = {};
  Object.keys(friendlyLabels).forEach((key) => {
    result[key] = key in data ? data[key] : null;
  });
  return result;
});
function getMovingAverage(key) {
  return metrics?.[`ma_${key}`] ?? null;
}

const footerValues = computed(() => {
  const m = metrics || {};
  return {
    is_running: m.is_running != null ? (m.is_running ? 'Yes' : 'No') : '—',
    last_sensor_name: m.last_sensor_name || '—',
    last_sensor_update: m.last_sensor_update
      ? new Date(m.last_sensor_update).toLocaleTimeString()
      : '—',
  };
});

// ---------------- Chart ----------------
const MAX_POINTS = 60;
const metricKeys = ['power', 'speed', 'cadence', 'heart_rate', 'heart_rate_percent'];
const chartGroups = [
  { id: 'power', label: 'Power', metrics: ['power'] },
  { id: 'speed', label: 'Speed', metrics: ['speed'] },
  { id: 'cadence', label: 'Cadence', metrics: ['cadence'] },
  { id: 'heart_rate', label: 'Heart Rate', metrics: ['heart_rate', 'heart_rate_percent'] },
];

const history = ref([]);
const openCharts = ref(chartGroups.reduce((acc, g) => ({ ...acc, [g.id]: true }), {}));

function toggleChart(id) {
  openCharts.value[id] = !openCharts.value[id];
}
function isChartOpen(id) {
  return openCharts.value[id];
}

watch(
  metrics,
  (newMetrics) => {
    if (!newMetrics) return;
    const snapshot = {};
    metricKeys.forEach((key) => {
      snapshot[key] = newMetrics[key] ?? null;
      snapshot[`ma_${key}`] = newMetrics[`ma_${key}`] ?? null;
    });
    history.value.push(snapshot);
    if (history.value.length > MAX_POINTS) history.value.shift();
  },
  { deep: true }
);

function getChartDataForGroup(group) {
  const labels = history.value.map((_, i) => i + 1);
  const datasets = [];
  // eslint-disable-next-line no-unused-vars
  group.metrics.forEach((key, idx) => {
    datasets.push({
      label: `${friendlyLabels[key] ?? key} (${getMetricUnit(key)})`,
      data: history.value.map((h) => (h[key] != null ? Math.round(h[key]) : null)),
      borderColor: '#7c3aed',
      tension: 0.3,
    });
    datasets.push({
      label: `MA ${friendlyLabels[key] ?? key} (${getMetricUnit(key)})`,
      data: history.value.map((h) => (h[`ma_${key}`] != null ? Math.round(h[`ma_${key}`]) : null)),
      borderColor: '#EC4899',
      tension: 0.3,
    });
  });
  return { labels, datasets };
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  interaction: { mode: 'index', intersect: false },
  plugins: { legend: { display: true, position: 'top' } },
  scales: { x: { display: false } },
};
</script>
