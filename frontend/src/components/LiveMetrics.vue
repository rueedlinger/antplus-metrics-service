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

    <div v-if="connected">
      <!-- ================= METRICS TAB ================= -->
      <div v-if="activeTab === 'metrics'">
        <div class="overflow-x-auto rounded-lg shadow-inner">
          <table class="table-auto w-full text-sm border-separate border-spacing-0 bg-white/30">
            <thead>
              <tr class="bg-gradient-to-r from-purple-500 to-blue-400 text-white">
                <th class="px-2 py-1 text-left">Metric</th>
                <th class="px-2 py-1 text-left">Current</th>
                <th class="px-2 py-1 text-left">Average</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(value, key) in normalMetrics" :key="key">
                <td class="px-2 py-1">
                  {{ friendlyLabels[key] ?? key }}
                  <span v-if="getMetricUnit(key)" class="text-xs text-gray-500">
                    ({{ getMetricUnit(key) }})
                  </span>
                </td>
                <td class="px-2 py-1">
                  {{ typeof value === 'number' ? Math.round(value) : value ?? '—' }}
                </td>
                <td class="px-2 py-1">
                  {{
                    typeof getMovingAverage(key) === 'number'
                      ? Math.round(getMovingAverage(key))
                      : getMovingAverage(key) ?? '—'
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ================= CHART TAB ================= -->
      <div v-else-if="activeTab === 'chart'">
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
              <h2 class="font-semibold">{{ group.label }}</h2>
              <span>{{ isChartOpen(group.id) ? '▼' : '►' }}</span>
            </div>

            <div v-show="isChartOpen(group.id)" class="h-64 mt-3">
              <Line :data="getChartDataForGroup(group)" :options="chartOptions" />
            </div>
          </div>
        </div>
      </div>

      <!-- ================= GOAL TAB ================= -->
      <div v-else-if="activeTab === 'goal'">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(bounds, key) in goalBounds"
            :key="key"
            class="border rounded-lg bg-white/50 p-4 shadow-md"
          >
            <h2 class="font-semibold mb-2">
              {{ friendlyLabels[key] ?? key }}
              <span v-if="getMetricUnit(key)" class="text-xs text-gray-500">
                ({{ getMetricUnit(key) }})
              </span>
            </h2>

            <div class="flex gap-2">
              <input
                type="number"
                placeholder="Lower"
                class="w-full border rounded px-2 py-1 text-sm"
                :value="bounds.lower"
                @input="updateGoal(key, 'lower', $event.target.value)"
              />
              <input
                type="number"
                placeholder="Upper"
                class="w-full border rounded px-2 py-1 text-sm"
                :value="bounds.upper"
                @input="updateGoal(key, 'upper', $event.target.value)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="p-4 bg-red-100 text-red-600 rounded-lg">
      Not connected
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
} from 'chart.js'
import { useMetricsStream } from '../composables/useStreams.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, CategoryScale)

const { metrics, lastUpdated, connected } = useMetricsStream()

// ================= TABS =================
const activeTab = ref('metrics')
const tabs = [
  { id: 'metrics', label: 'Metrics' },
  { id: 'chart', label: 'Chart' },
  { id: 'goal', label: 'Goal' },
]

// ================= LABELS & UNITS =================
const metricUnits = {
  power: 'W',
  speed: 'km/h',
  cadence: 'RPM',
  heart_rate: 'bpm',
  heart_rate_percent: '%',
  distance: 'm',
}

const friendlyLabels = {
  power: 'Power',
  speed: 'Speed',
  cadence: 'Cadence',
  heart_rate: 'Heart Rate',
  heart_rate_percent: 'Heart Rate %',
  distance: 'Distance',
  zone_name: 'Zone',
}

function getMetricUnit(metric) {
  return metricUnits[metric] ?? ''
}

// ================= GOALS =================
const goalBounds = ref({
  power: { lower: null, upper: null },
  speed: { lower: null, upper: null },
  cadence: { lower: null, upper: null },
  heart_rate: { lower: null, upper: null },
  heart_rate_percent: { lower: null, upper: null },
  distance: { lower: null, upper: null },
  zone_name: { lower: null, upper: null },
})

function updateGoal(metric, type, value) {
  goalBounds.value[metric][type] =
    value === '' || value === null ? null : Number(value)
}

// ================= TABLE =================
const normalMetrics = computed(() => {
  const data = metrics || {}
  const result = {}
  Object.keys(friendlyLabels).forEach((key) => {
    result[key] = key in data ? data[key] : null
  })
  return result
})

function getMovingAverage(key) {
  return metrics?.[`ma_${key}`] ?? null
}

// ================= CHART =================
const MAX_POINTS = 60
const metricKeys = [
  'power',
  'speed',
  'cadence',
  'heart_rate',
  'heart_rate_percent',
  'distance',
  'zone_name',
]

const chartGroups = [
  { id: 'power', label: 'Power', metrics: ['power'], onlyMA: false },
  { id: 'speed', label: 'Speed', metrics: ['speed'], onlyMA: false },
  { id: 'cadence', label: 'Cadence', metrics: ['cadence'], onlyMA: false },
  { id: 'heart_rate', label: 'Heart Rate', metrics: ['heart_rate', 'heart_rate_percent'], onlyMA: false },
  { id: 'distance', label: 'Distance', metrics: ['distance'], onlyMA: true },
  { id: 'zone', label: 'Zone', metrics: ['zone_name'], onlyMA: false },
]

const history = ref([])
const openCharts = ref(chartGroups.reduce((a, g) => ({ ...a, [g.id]: true }), {}))

function toggleChart(id) {
  openCharts.value[id] = !openCharts.value[id]
}
function isChartOpen(id) {
  return openCharts.value[id]
}

watch(metrics, (newMetrics) => {
  if (!newMetrics) return
  const snapshot = {}
  metricKeys.forEach((key) => {
    snapshot[key] = newMetrics[key] ?? null
    snapshot[`ma_${key}`] = newMetrics[`ma_${key}`] ?? null
  })
  history.value.push(snapshot)
  if (history.value.length > MAX_POINTS) history.value.shift()
}, { deep: true })

function getChartDataForGroup(group) {
  const labels = history.value.map((_, i) => i + 1)
  const datasets = []

  group.metrics.forEach((key) => {
    if (!group.onlyMA) {
      datasets.push({
        label: friendlyLabels[key],
        data: history.value.map(h => h[key]),
        borderColor: '#7c3aed',
        tension: 0.3,
      })
    }

    datasets.push({
      label: `MA ${friendlyLabels[key]}`,
      data: history.value.map(h => h[`ma_${key}`]),
      borderColor: '#EC4899',
      tension: 0.3,
    })

    // LOWER
    const lower = goalBounds.value[key]?.lower
    if (lower != null) {
      datasets.push({
        label: `Lower ${friendlyLabels[key]}`,
        data: history.value.map(() => lower),
        borderColor: '#22c55e',
        borderDash: [6,6],
        pointRadius: 0,
      })
    }

    // UPPER
    const upper = goalBounds.value[key]?.upper
    if (upper != null) {
      datasets.push({
        label: `Upper ${friendlyLabels[key]}`,
        data: history.value.map(() => upper),
        borderColor: '#ef4444',
        borderDash: [6,6],
        pointRadius: 0,
      })
    }
  })

  return { labels, datasets }
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  interaction: { mode: 'index', intersect: false },
  plugins: { legend: { position: 'top' } },
  scales: { x: { display: false } },
}
</script>