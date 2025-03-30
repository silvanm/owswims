<template>
  <div class="apollo-test">
    <h2>Apollo Client 3.x Test</h2>
    
    <div v-if="loading" class="loading">
      Loading...
    </div>
    
    <div v-else-if="error" class="error">
      Error: {{ error.message }}
    </div>
    
    <div v-else-if="data" class="data">
      <h3>Location Data</h3>
      <pre>{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
    
    <button @click="fetchData" class="fetch-button">
      Fetch Data
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useNuxtApp } from '#app'

// State
const loading = ref(false)
const error = ref(null)
const data = ref(null)

// Get the queries from the Nuxt app
const nuxtApp = useNuxtApp()
const queries = nuxtApp.$queries

// Function to fetch data
const fetchData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Example query parameters
    const locationId = '1' // Replace with an actual location ID
    const keyword = ''
    const dateRange = [new Date(), new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)] // Today to 30 days from now
    
    // Execute the query
    const result = await queries.location(locationId, keyword, dateRange)
    data.value = result.data
  } catch (err) {
    error.value = err
    console.error('Apollo query error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.apollo-test {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 20px 0;
}

h2 {
  margin-top: 0;
  color: #333;
}

.loading, .error {
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
}

.loading {
  background-color: #f8f9fa;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
}

.data {
  margin: 10px 0;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
  max-height: 300px;
}

.fetch-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.fetch-button:hover {
  background-color: #45a049;
}
</style>
