<template>
  <client-only>
    <div class="daterange-slider">
      <div v-if="!calendarMode" class="slider-container">
        <div class="slider-track">
          <div class="slider-range" :style="sliderRangeStyle"></div>
          <div class="slider-handle start" :style="startHandleStyle" @mousedown="startDrag('start')"></div>
          <div class="slider-handle end" :style="endHandleStyle" @mousedown="startDrag('end')"></div>
        </div>
        <div class="slider-labels">
          <div class="slider-label" v-for="month in 13" :key="month" :style="{ left: `${(month - 1) * 8.33}%` }">
            {{ formatMonth(month - 2) }}
          </div>
        </div>
      </div>
      <div v-else class="calendar-container">
        <div class="calendar-placeholder">
          Calendar view (simplified for testing)
        </div>
        <div class="date-display">
          <div>Start: {{ formatDate(dateRange[0]) }}</div>
          <div>End: {{ formatDate(dateRange[1]) }}</div>
        </div>
      </div>
      <button @click="toggleView" class="toggle-button">
        {{ calendarMode ? 'Show Slider' : 'Show Calendar' }}
      </button>
    </div>
  </client-only>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'DateRangeSlider',
  props: {
    showCalendar: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['change'],
  setup(props, { emit }) {
    const isCalendarView = ref(props.showCalendar)
    const startValue = ref(0)
    const endValue = ref(10)
    const dragging = ref(null)
    const dateRange = ref([new Date(), new Date()])

    const sliderRangeStyle = computed(() => {
      return {
        left: `${startValue.value * 8.33}%`,
        width: `${(endValue.value - startValue.value) * 8.33}%`,
      }
    })

    const startHandleStyle = computed(() => {
      return {
        left: `${startValue.value * 8.33}%`,
      }
    })

    const endHandleStyle = computed(() => {
      return {
        left: `${endValue.value * 8.33}%`,
      }
    })

    const formatMonth = (monthOffset) => {
      const date = new Date()
      date.setMonth(date.getMonth() + monthOffset)
      return date.toLocaleString('default', { month: 'short' })
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return date.toLocaleDateString()
    }

    const updateDateRange = () => {
      const today = new Date()
      const start = new Date(today)
      start.setMonth(today.getMonth() + startValue.value)
      start.setDate(1)
      
      const end = new Date(today)
      end.setMonth(today.getMonth() + endValue.value)
      end.setDate(1)
      
      dateRange.value = [start, end]
      emit('change', dateRange.value)
    }

    const startDrag = (handle) => {
      dragging.value = handle
      document.addEventListener('mousemove', onDrag)
      document.addEventListener('mouseup', stopDrag)
    }

    const onDrag = (e) => {
      if (!dragging.value) return
      
      const sliderTrack = document.querySelector('.slider-track')
      if (!sliderTrack) return
      
      const rect = sliderTrack.getBoundingClientRect()
      const percentage = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
      const value = Math.round(percentage * 12)
      
      if (dragging.value === 'start') {
        startValue.value = Math.min(value, endValue.value - 1)
      } else {
        endValue.value = Math.max(value, startValue.value + 1)
      }
      
      updateDateRange()
    }

    const stopDrag = () => {
      dragging.value = null
      document.removeEventListener('mousemove', onDrag)
      document.removeEventListener('mouseup', stopDrag)
    }

    const toggleView = () => {
      isCalendarView.value = !isCalendarView.value
    }

    onMounted(() => {
      updateDateRange()
    })

    onUnmounted(() => {
      document.removeEventListener('mousemove', onDrag)
      document.removeEventListener('mouseup', stopDrag)
    })

    return {
      startValue,
      endValue,
      sliderRangeStyle,
      startHandleStyle,
      endHandleStyle,
      formatMonth,
      formatDate,
      startDrag,
      dateRange,
      calendarMode: isCalendarView,
      toggleView,
    }
  },
}
</script>

<style scoped>
.daterange-slider {
  width: 100%;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.slider-container {
  margin-bottom: 40px;
}

.slider-track {
  position: relative;
  height: 6px;
  background-color: #e0e0e0;
  border-radius: 3px;
  margin: 30px 0;
}

.slider-range {
  position: absolute;
  height: 100%;
  background-color: #4CAF50;
  border-radius: 3px;
}

.slider-handle {
  position: absolute;
  width: 20px;
  height: 20px;
  background-color: #fff;
  border: 2px solid #4CAF50;
  border-radius: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  position: relative;
  margin-top: 10px;
}

.slider-label {
  position: absolute;
  transform: translateX(-50%);
  font-size: 12px;
  color: #666;
}

.calendar-container {
  margin-bottom: 20px;
}

.calendar-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  font-style: italic;
}

.date-display {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.toggle-button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.toggle-button:hover {
  background-color: #45a049;
}
</style>
