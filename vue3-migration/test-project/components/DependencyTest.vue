<template>
  <div class="dependency-test">
    <h1>Vue 3 Dependency Test</h1>
    
    <section class="section">
      <h2>Pinia Store Test</h2>
      <p>{{ counterStore.formattedCount }}</p>
      <p>Double count: {{ counterStore.doubleCount }}</p>
      <div class="button-group">
        <button @click="counterStore.increment">Increment</button>
        <button @click="counterStore.decrement">Decrement</button>
        <button @click="counterStore.reset">Reset</button>
      </div>
    </section>
    
    <section class="section">
      <h2>@vueform/slider Test</h2>
      <p>Current value: {{ sliderValue }}</p>
      <Slider v-model="sliderValue" :min="0" :max="100" />
    </section>
    
    <section class="section">
      <h2>@vuepic/vue-datepicker Test</h2>
      <p>Selected date: {{ selectedDate ? selectedDate.toLocaleDateString() : 'None' }}</p>
      <DatePicker v-model="selectedDate" />
    </section>
    
    <!-- Removed floating-vue test due to SSR issues -->
    
    <section class="section">
      <h2>Apollo GraphQL Test (Simulated)</h2>
      <p>{{ graphqlData ? 'Data loaded!' : 'Loading data...' }}</p>
      <pre v-if="graphqlData">{{ JSON.stringify(graphqlData, null, 2) }}</pre>
      <button @click="loadGraphQLData">Load Data</button>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCounterStore } from '~/stores/counter'
import Slider from '@vueform/slider'
import DatePicker from '@vuepic/vue-datepicker'

// Import styles
import '@vueform/slider/themes/default.css'
import '@vuepic/vue-datepicker/dist/main.css'

// Pinia store
const counterStore = useCounterStore()

// Slider state
const sliderValue = ref(50)

// DatePicker state
const selectedDate = ref(new Date())

// Apollo GraphQL simulation
const graphqlData = ref(null)

const loadGraphQLData = () => {
  // Simulate GraphQL query
  setTimeout(() => {
    graphqlData.value = {
      user: {
        id: 1,
        name: 'John Doe',
        email: 'john@example.com',
        posts: [
          { id: 1, title: 'First Post' },
          { id: 2, title: 'Second Post' }
        ]
      }
    }
  }, 1000)
}
</script>

<style scoped>
.dependency-test {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

h2 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
}
</style>
