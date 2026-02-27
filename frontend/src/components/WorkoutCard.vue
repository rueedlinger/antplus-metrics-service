<template>
  <div class="backdrop-blur-lg bg-white/80 rounded-2xl shadow-xl p-6 text-center space-y-6">
    <h2 class="text-2xl font-semibold text-center text-black">Workout Intervals</h2>

    <!-- No intervals -->
    <div v-if="intervals.length === 0" class="text-gray-500 text-center">No intervals yet.</div>

    <!-- Intervals List -->
    <div
      v-for="(interval, index) in intervals"
      :key="index"
      class="flex items-center gap-2 flex-wrap sm:flex-nowrap"
    >
      <!-- Interval Name -->
      <input
        v-model="interval.name"
        type="text"
        placeholder="Interval Name"
        class="flex-1 rounded-lg px-3 py-2 bg-white/50 border border-white/20 text-black placeholder-black/50 shadow-inner focus:ring-2 focus:ring-purple-400 focus:border-transparent"
        :disabled="loading || isRunning"
      />

      <!-- Time Inputs -->
      <div
        class="flex gap-1 items-center rounded-lg bg-white/50 border border-white/20 shadow-inner px-2 py-1"
      >
        <!-- Hours -->
        <div class="flex flex-col items-center">
          <input
            v-model.number="interval.hours"
            type="number"
            min="0"
            class="w-12 text-center rounded bg-white/50 border border-white/20 shadow-inner text-black"
            :disabled="loading || isRunning"
            @input="updateSeconds(interval)"
          />
          <span class="text-xs text-black/70">HH</span>
        </div>

        <span class="text-black/50">:</span>

        <!-- Minutes -->
        <div class="flex flex-col items-center">
          <input
            v-model.number="interval.minutes"
            type="number"
            min="0"
            max="59"
            class="w-12 text-center rounded bg-white/50 border border-white/20 shadow-inner text-black"
            :disabled="loading || isRunning"
            @input="updateSeconds(interval)"
          />
          <span class="text-xs text-black/70">MM</span>
        </div>

        <span class="text-black/50">:</span>

        <!-- Seconds -->
        <div class="flex flex-col items-center">
          <input
            v-model.number="interval.secondsInput"
            type="number"
            min="0"
            max="59"
            class="w-12 text-center rounded bg-white/50 border border-white/20 shadow-inner text-black"
            :disabled="loading || isRunning"
            @input="updateSeconds(interval)"
          />
          <span class="text-xs text-black/70">SS</span>
        </div>
      </div>

      <!-- Remove Button -->
      <button
        :disabled="loading || isRunning"
        class="bg-gradient-to-r from-purple-500 to-blue-400 text-white px-3 py-1 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
        @click="removeInterval(index)"
      >
        ✕
      </button>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-4 pt-4 flex-wrap justify-center">
      <!-- Add Interval -->
      <button
        :disabled="loading || isRunning"
        class="bg-gradient-to-r from-purple-500 to-blue-400 text-white px-4 py-2 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
        @click="addInterval"
      >
        Add Interval
      </button>

      <!-- Save Workout -->
      <button
        :disabled="loading || isRunning"
        class="bg-gradient-to-r from-purple-500 to-blue-400 text-white px-4 py-2 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 disabled:opacity-50"
        @click="submitWorkout"
      >
        <div
          v-if="loading"
          class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
        ></div>
        <span>{{ loading ? 'Saving...' : 'Save Workout' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { API } from '../config.js';
import { ToastType } from '../constants/toastType.js';
import { useWorkoutStream } from '../composables/useStreams.js';

const emit = defineEmits(['update-workout', 'show-toast']);
const loading = ref(false);

/* ================= STREAM STATE ================= */
const { workout } = useWorkoutStream();
const isRunning = computed(() => !!workout.is_running);

/* ================= STATE ================= */
const intervals = ref([]);

/* ================= HELPERS ================= */
function initInterval(i) {
  const h = Math.floor(i.seconds / 3600);
  const m = Math.floor((i.seconds % 3600) / 60);
  const s = i.seconds % 60;

  return {
    ...i,
    hours: h,
    minutes: m,
    secondsInput: s,
  };
}

function updateSeconds(interval) {
  interval.seconds = interval.hours * 3600 + interval.minutes * 60 + interval.secondsInput;
}

function addInterval() {
  intervals.value.push({
    name: '',
    hours: 0,
    minutes: 0,
    secondsInput: 0,
    seconds: 0,
  });
}

function removeInterval(index) {
  intervals.value.splice(index, 1);
}

function isValid() {
  return intervals.value.every((i) => i.name.trim().length > 0 && i.seconds > 0);
}

/* ================= LOAD ================= */
async function loadWorkout() {
  try {
    const res = await axios.get(API.baseUrl + API.endpoints.getWorkout);

    intervals.value = (Array.isArray(res.data) ? res.data : []).map(initInterval);
  } catch (err) {
    intervals.value = [];

    emit('show-toast', {
      message: err.response?.data?.message || err.message || 'Failed to load workout',
      title: 'Error',
      type: ToastType.ERROR,
    });
  }
}

/* ================= SUBMIT ================= */
async function submitWorkout() {
  if (!isValid()) {
    emit('show-toast', {
      message: 'Each interval must have a name and time > 0',
      title: 'Invalid Input',
      type: ToastType.ERROR,
    });
    return;
  }

  loading.value = true;

  try {
    const payload = intervals.value.map((i) => ({
      name: i.name,
      seconds: i.seconds,
    }));

    const res = await axios.post(API.baseUrl + API.endpoints.setWorkout, payload);

    intervals.value = (Array.isArray(res.data) ? res.data : payload).map(initInterval);

    emit('update-workout', intervals.value);

    emit('show-toast', {
      message: 'Workout saved successfully!',
      title: 'Workout',
      type: ToastType.SUCCESS,
    });
  } catch (err) {
    emit('show-toast', {
      message: err.response?.data?.detail || err.message || 'Failed to save workout',
      title: 'Error',
      type: ToastType.ERROR,
    });
  } finally {
    loading.value = false;
  }
}

/* ================= INIT ================= */
onMounted(loadWorkout);
</script>
