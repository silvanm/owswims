<template>
  <div class="component-test">
    <h1>Migrated Components Test Page</h1>
    <p class="description">This page displays all components that have been migrated to Vue 3.</p>
    
    <div class="navigation">
      <NuxtLink to="/">Back to Home</NuxtLink>
    </div>
    
    <section class="component-section">
      <h2>CloseButton Component</h2>
      <div class="component-demo">
        <div class="component-container">
          <CloseButton :is-static="isStaticCloseButton" />
        </div>
        <div class="component-controls">
          <label>
            <input type="checkbox" v-model="isStaticCloseButton" />
            Is Static
          </label>
          <div class="events-log">
            <h4>Events:</h4>
            <div v-if="closeButtonEvents.length === 0" class="no-events">No events yet</div>
            <ul v-else>
              <li v-for="(event, index) in closeButtonEvents" :key="index">{{ event }}</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>Toggle Component</h2>
      <div class="component-demo">
        <div class="component-container">
          <Toggle name="test-toggle" :is-checked="isToggleChecked" @change="onToggleChange">
            Toggle Switch
          </Toggle>
        </div>
        <div class="component-controls">
          <div>Current value: {{ isToggleChecked ? 'On' : 'Off' }}</div>
          <button @click="isToggleChecked = !isToggleChecked">Toggle Programmatically</button>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>Spinner Component</h2>
      <div class="component-demo">
        <div class="component-container spinner-container">
          <Spinner :show="showSpinner" />
          <div v-if="!showSpinner" class="spinner-placeholder">
            Spinner will appear here
          </div>
        </div>
        <div class="component-controls">
          <button @click="showSpinner = !showSpinner">
            {{ showSpinner ? 'Hide' : 'Show' }} Spinner
          </button>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>DaterangeSlider Component</h2>
      <div class="component-demo">
        <div class="component-container daterange-container">
          <DaterangeSlider 
            :show-calendar="showCalendar" 
            @change="onDateRangeChange"
          />
        </div>
        <div class="component-controls">
          <button @click="showCalendar = !showCalendar">
            {{ showCalendar ? 'Show Slider' : 'Show Calendar' }}
          </button>
          <div class="date-display">
            <div><strong>Start Date:</strong> {{ formatDate(dateRange[0]) }}</div>
            <div><strong>End Date:</strong> {{ formatDate(dateRange[1]) }}</div>
          </div>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>EventPane Component</h2>
      <div class="component-demo">
        <div class="component-container eventpane-container">
          <EventPane v-if="showEventPane" />
          <div v-else class="eventpane-placeholder">
            EventPane will appear here
          </div>
        </div>
        <div class="component-controls">
          <button @click="showEventPane = !showEventPane">
            {{ showEventPane ? 'Hide' : 'Show' }} EventPane
          </button>
          <div class="note">
            <p><strong>Note:</strong> This is a simplified test of the EventPane component.</p>
            <p>The component requires complex data structures and store integration.</p>
          </div>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>FilterBox Component</h2>
      <div class="component-demo">
        <div class="component-container filterbox-container">
          <FilterBox v-if="showFilterBox" @showLogin="onShowLogin" />
          <div v-else class="filterbox-placeholder">
            FilterBox will appear here
          </div>
        </div>
        <div class="component-controls">
          <button @click="showFilterBox = !showFilterBox">
            {{ showFilterBox ? 'Hide' : 'Show' }} FilterBox
          </button>
          <div class="note">
            <p><strong>Note:</strong> This is a simplified test of the FilterBox component.</p>
            <p>The component requires store integration for full functionality.</p>
          </div>
          <div v-if="loginRequested" class="login-notification">
            Login requested!
          </div>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>Map Component</h2>
      <div class="component-demo">
        <div class="component-container map-container">
          <MapComponent 
            v-if="showMap" 
            :locations="mapLocations"
            @locationPicked="onLocationPicked"
          />
          <div v-else class="map-placeholder">
            Map will appear here
          </div>
        </div>
        <div class="component-controls">
          <button @click="showMap = !showMap">
            {{ showMap ? 'Hide' : 'Show' }} Map
          </button>
          <div class="note">
            <p><strong>Note:</strong> This is a simplified test of the Map component.</p>
            <p>The component requires Google Maps API integration and store integration for full functionality.</p>
          </div>
          <div v-if="locationPicked" class="location-notification">
            Location picked!
          </div>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>ReviewBox Component</h2>
      <div class="component-demo">
        <div class="component-container reviewbox-container">
          <ReviewBox v-if="showReviewBox" @hide="onHideReviewBox" />
          <div v-else class="reviewbox-placeholder">
            ReviewBox will appear here
          </div>
        </div>
        <div class="component-controls">
          <button @click="showReviewBox = !showReviewBox">
            {{ showReviewBox ? 'Hide' : 'Show' }} ReviewBox
          </button>
          <div class="note">
            <p><strong>Note:</strong> This is a simplified test of the ReviewBox component.</p>
            <p>The component requires store integration and GraphQL for full functionality.</p>
          </div>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>LoginBox Component</h2>
      <div class="component-demo">
        <div class="component-container loginbox-container">
          <LoginBox v-if="showLoginBox" @hide="onHideLoginBox" />
          <div v-else class="loginbox-placeholder">
            LoginBox will appear here
          </div>
        </div>
        <div class="component-controls">
          <button @click="showLoginBox = !showLoginBox">
            {{ showLoginBox ? 'Hide' : 'Show' }} LoginBox
          </button>
          <div class="note">
            <p><strong>Note:</strong> This is a simplified test of the LoginBox component.</p>
            <p>The component requires store integration for full functionality.</p>
          </div>
        </div>
      </div>
    </section>
    
    <section class="component-section">
      <h2>TranslatableText Component</h2>
      <div class="component-demo">
        <div class="component-container translatable-container">
          <TranslatableText v-if="showTranslatable">
            {{ textToTranslate }}
          </TranslatableText>
          <div v-else class="translatable-placeholder">
            TranslatableText will appear here
          </div>
        </div>
        <div class="component-controls">
          <button @click="showTranslatable = !showTranslatable">
            {{ showTranslatable ? 'Hide' : 'Show' }} TranslatableText
          </button>
          <div class="text-input">
            <label for="text-to-translate">Text to translate:</label>
            <input 
              id="text-to-translate" 
              v-model="textToTranslate" 
              type="text" 
              placeholder="Enter text to translate"
              :disabled="!showTranslatable"
            />
          </div>
          <div class="note">
            <p><strong>Note:</strong> This is a simplified test of the TranslatableText component.</p>
            <p>The component uses a mock translation API in the test environment.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { format } from 'date-fns'

// Import migrated components
import ReviewBox from '../components/ReviewBox.vue'
import CloseButton from '../components/CloseButton.vue'
import Toggle from '../components/Toggle.vue'
import Spinner from '../components/Spinner.vue'
import DaterangeSlider from '../components/DaterangeSlider.vue'
import EventPane from '../components/EventPane.vue'
import FilterBox from '../components/FilterBox.vue'
import MapComponent from '../components/Map.vue'
import LoginBox from '../components/LoginBox.vue'
import TranslatableText from '../components/Translatable.vue'

// CloseButton state
const isStaticCloseButton = ref(false)
const closeButtonEvents = ref([])

// Toggle state
const isToggleChecked = ref(false)

// Spinner state
const showSpinner = ref(false)

// DaterangeSlider state
const showCalendar = ref(false)
const dateRange = ref([new Date(), new Date()])

// EventPane state
const showEventPane = ref(false)

// FilterBox state
const showFilterBox = ref(false)
const loginRequested = ref(false)

// Map state
const showMap = ref(false)
const mapLocations = ref([
  { id: 'loc1', lat: 47.3474476, lng: 8.6733976, city: 'Zurich', country: 'Switzerland', averageRating: 4 },
  { id: 'loc2', lat: 46.2043907, lng: 6.1431577, city: 'Geneva', country: 'Switzerland', averageRating: 5 }
])
const locationPicked = ref(false)

// ReviewBox state
const showReviewBox = ref(false)

// LoginBox state
const showLoginBox = ref(false)

// TranslatableText state
const showTranslatable = ref(false)
const textToTranslate = ref('This is a sample text that can be translated.')

// Event handlers
const onToggleChange = (value) => {
  isToggleChecked.value = value
}

const onDateRangeChange = (range) => {
  dateRange.value = range
}

// Helper functions
const formatDate = (date) => {
  if (!date) return 'N/A'
  return format(date, 'MMM dd, yyyy')
}

const onShowLogin = () => {
  loginRequested.value = true
  setTimeout(() => {
    loginRequested.value = false
  }, 3000)
}

const onLocationPicked = () => {
  locationPicked.value = true
  setTimeout(() => {
    locationPicked.value = false
  }, 3000)
}

const onHideReviewBox = () => {
  showReviewBox.value = false
}

const onHideLoginBox = () => {
  showLoginBox.value = false
}
</script>

<style scoped>
.component-test {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  margin-bottom: 10px;
}

.description {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.navigation {
  margin-bottom: 30px;
  text-align: center;
}

.navigation a {
  display: inline-block;
  padding: 8px 16px;
  background-color: #f0f0f0;
  color: #333;
  text-decoration: none;
  border-radius: 4px;
}

.navigation a:hover {
  background-color: #e0e0e0;
}

.component-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.component-demo {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.component-container {
  flex: 1;
  min-width: 300px;
  padding: 20px;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.component-controls {
  flex: 1;
  min-width: 300px;
  padding: 20px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 10px;
}

button:hover {
  background-color: #45a049;
}

.events-log {
  margin-top: 15px;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: 150px;
  overflow-y: auto;
}

.events-log h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.no-events {
  color: #999;
  font-style: italic;
}

.spinner-container {
  position: relative;
  height: 200px;
}

.spinner-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.daterange-container {
  width: 100%;
  min-height: 300px;
}

.date-display {
  margin-top: 15px;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.eventpane-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.eventpane-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.note {
  margin-top: 15px;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
}

.filterbox-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.filterbox-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.login-notification {
  margin-top: 15px;
  padding: 10px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  color: #155724;
  font-weight: bold;
}

.map-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.map-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.location-notification {
  margin-top: 15px;
  padding: 10px;
  background-color: #cce5ff;
  border: 1px solid #b8daff;
  border-radius: 4px;
  color: #004085;
  font-weight: bold;
}

.reviewbox-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.reviewbox-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.loginbox-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.loginbox-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.translatable-container {
  width: 100%;
  min-height: 200px;
  position: relative;
}

.translatable-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.text-input {
  margin-top: 15px;
  margin-bottom: 15px;
}

.text-input label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.text-input input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
