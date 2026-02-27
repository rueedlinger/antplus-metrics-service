<template>
  <div class="backdrop-blur-lg bg-white/80 rounded-2xl shadow-xl p-6 text-center space-y-6">
    <h1 class="text-2xl font-bold text-gray-800">Main</h1>

    <!-- ================= FULL WORKOUT TABLE ================= -->
    <div class="overflow-x-auto rounded-lg shadow-inner">
      <table class="table-auto w-full text-sm border-separate border-spacing-0 bg-white/30">
        <thead>
          <tr class="bg-gradient-to-r from-purple-500 to-blue-400 text-white">
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Sensor Metrics Status
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Workout Status
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Current Interval
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Time Remaining Interval
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Time Spent Interval
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">
              Total Time Spent
            </th>
            <th class="px-2 py-1 text-left border-b border-dashed border-black/30">Round</th>
          </tr>
        </thead>
        <tbody>
          <tr class="hover:bg-gray-50 transition">
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              <span
                :class="
                  metrics.is_running ? 'text-blue-500 font-semibold' : 'text-pink-500 font-semibold'
                "
              >
                {{ metrics.is_running ? 'Running' : 'Stopped' }}
              </span>
            </td>
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              <span
                :class="
                  workout.is_running ? 'text-blue-500 font-semibold' : 'text-pink-500 font-semibold'
                "
              >
                {{ workout.is_running ? 'Running' : 'Stopped' }}
              </span>
            </td>
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30 font-semibold">
              {{ workout.interval?.name ?? '-' }} ({{ workout.interval?.seconds ?? '-' }} s)
            </td>
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              {{ formatTime(workout.time_remaining) }}
            </td>
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              {{ formatTime(workout.time_spent) }}
            </td>
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              {{ formatTime(workout.total_time_spent) }}
            </td>
            <td class="px-2 py-1 text-left border-b border-dashed border-black/30">
              {{ workout.round_number ?? '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ================= BUTTONS ================= -->
    <div class="flex justify-center gap-4 flex-wrap">
      <!-- Metrics Toggle -->
      <button
        :disabled="loadingMetrics"
        @click="toggleMetrics"
        :class="[
          baseBtnClass,
          isRunningMetrics
            ? 'bg-gradient-to-r from-red-500 to-pink-500'
            : 'bg-gradient-to-r from-purple-500 to-blue-400',
        ]"
      >
        <div
          v-if="loadingMetrics"
          class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
        ></div>
        <span>{{ isRunningMetrics ? 'Stop' : 'Start' }} Sensor Scanning...</span>
      </button>

      <!-- Workout Toggle -->
      <button
        :disabled="loadingWorkout"
        @click="toggleWorkout"
        :class="[
          baseBtnClass,
          isRunningWorkout
            ? 'bg-gradient-to-r from-red-500 to-pink-500'
            : 'bg-gradient-to-r from-purple-500 to-blue-400',
        ]"
      >
        <div
          v-if="loadingWorkout"
          class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
        ></div>
        <span>{{ isRunningWorkout ? 'Stop' : 'Start' }} Workout</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { API } from '../config.js';
import { ToastType } from '../constants/toastType.js';
import { useMetricsStream, useWorkoutStream } from '../composables/useStreams.js';

const emit = defineEmits(['show-toast']);

/* ================= COMMON BUTTON STYLE ================= */
const baseBtnClass =
  'px-6 py-3 rounded-2xl font-semibold text-white shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center justify-center space-x-2 transition-all duration-300';

/* ================= METRICS ================= */
const { metrics } = useMetricsStream();
const isRunningMetrics = computed(() => !!metrics.is_running);
const loadingMetrics = ref(false);

async function toggleMetrics() {
  if (loadingMetrics.value) return;
  loadingMetrics.value = true;

  try {
    const endpoint = isRunningMetrics.value
      ? API.endpoints.stopMetrics
      : API.endpoints.startMetrics;

    const { data } = await axios.post(API.baseUrl + endpoint);

    emit('show-toast', {
      message: data.message || (isRunningMetrics.value ? 'Metrics stopped' : 'Metrics started'),
      title: isRunningMetrics.value ? 'Stopped' : 'Started',
      type: ToastType.SUCCESS,
    });
  } catch (err) {
    emit('show-toast', {
      message: err.response?.data?.detail || err.message || 'Network error',
      title: 'Error',
      type: ToastType.ERROR,
    });
  } finally {
    loadingMetrics.value = false;
  }
}

/* ================= WORKOUT ================= */
const { workout } = useWorkoutStream();
const isRunningWorkout = computed(() => !!workout.is_running);
const loadingWorkout = ref(false);

/* ===== AUDIO CONTEXT ===== */
let audioCtx = null;

function initAudio() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
}

function playBeep(duration = 0.2) {
  if (!audioCtx) return;

  const oscillator = audioCtx.createOscillator();
  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(1000, audioCtx.currentTime);
  oscillator.connect(audioCtx.destination);
  oscillator.start();
  oscillator.stop(audioCtx.currentTime + duration);
}

async function toggleWorkout() {
  if (loadingWorkout.value) return;

  initAudio();
  if (audioCtx.state === 'suspended') await audioCtx.resume();

  loadingWorkout.value = true;

  try {
    const endpoint = isRunningWorkout.value
      ? API.endpoints.stopWorkout
      : API.endpoints.startWorkout;

    const { data } = await axios.post(API.baseUrl + endpoint);

    emit('show-toast', {
      message: data.message || (isRunningWorkout.value ? 'Workout stopped' : 'Workout started'),
      title: isRunningWorkout.value ? 'Stopped' : 'Started',
      type: ToastType.SUCCESS,
    });
  } catch (err) {
    emit('show-toast', {
      message: err.response?.data?.detail || err.message || 'Network error',
      title: 'Error',
      type: ToastType.ERROR,
    });
  } finally {
    loadingWorkout.value = false;
  }
}

/* ================= FORMATTER ================= */
function formatTime(value) {
  if (value == null) return '-';

  const totalSeconds = Math.round(Number(value));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

/* ================= WATCH LAST 5 SECONDS ================= */
let lastBeepSecond = null;
let numberOfBeeps = 3

watch(
  () => workout.time_remaining,
  async (newVal) => {
    if (newVal == null) return;

    const seconds = Math.round(newVal);

    // beep for last 5 seconds
    if (seconds > 0 && seconds <= numberOfBeeps && seconds !== lastBeepSecond) {
      initAudio();
      if (audioCtx.state === 'suspended') await audioCtx.resume();

      if (seconds == 1) {
        playBeep(1);
      } else {
        playBeep(0.25);
      }
      lastBeepSecond = seconds;
    }

    // reset for next interval
    if (seconds > 5) lastBeepSecond = null;
  },
  { immediate: true }
);

onMounted(() => {
  initAudio();
});

onBeforeUnmount(() => {
  lastBeepSecond = null;
});
</script>
