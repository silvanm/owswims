<template>
  <div>
    <!-- WelcomeBox component would go here if migrated -->
    <ReviewBox
      v-if="mainStore.reviewBoxShown"
      @hide="mainStore.setReviewBoxShown(false)"
    />
    
    <!-- OrganizerLogo component would go here if migrated -->
    
    <LoginBox
      v-if="loginboxShown && !authStore.loggedIn"
      @hide="doHideLogin"
    />
    
    <div class="xl:m-4">
      <Map
        v-if="locationsFiltered"
        ref="map"
        :locations="locationsFiltered"
        :lat="mainStore.lat"
        :lng="mainStore.lng"
        :distance-from="mainStore.distanceRange[0]"
        :distance-to="mainStore.distanceRange[1]"
        :date-range="mainStore.dateRange"
        @locationPicked="locationPicked()"
      />
      
      <Spinner :show="mainStore.isLoading" />
      
      <div style="max-height: 100vh">
        <FilterBox
          v-if="!mainStore.isEmbedded"
          ref="filterboxRef"
          @showLogin="doShowLogin"
        />
        
        <div v-if="mainStore.pickedLocationId">
          <EventPane />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMainStore } from '../stores/main'
import { useAuthStore } from '../stores/auth'
import { useDeviceDetector } from '../composables/useDeviceDetector'

// Import migrated components
import ReviewBox from '../components/ReviewBox.vue'
import LoginBox from '../components/LoginBox.vue'
import Map from '../components/Map.vue'
import Spinner from '../components/Spinner.vue'
import FilterBox from '../components/FilterBox.vue'
import EventPane from '../components/EventPane.vue'

// Setup stores
const mainStore = useMainStore()
const authStore = useAuthStore()
const device = useDeviceDetector()

// Component state
const loginboxShown = ref(false)
const welcomeboxShown = ref(false)

// Mock data for locations (in a real app, this would come from an API)
const locationsFiltered = ref([
  { 
    id: 'TG9jYXRpb246MQ==', 
    country: 'Switzerland', 
    city: 'Zurich', 
    lat: 47.3769, 
    lng: 8.5417, 
    averageRating: 4.5 
  },
  { 
    id: 'TG9jYXRpb246Mg==', 
    country: 'Switzerland', 
    city: 'Geneva', 
    lat: 46.2044, 
    lng: 6.1432, 
    averageRating: 4.2 
  },
  { 
    id: 'TG9jYXRpb246Mw==', 
    country: 'Switzerland', 
    city: 'Lucerne', 
    lat: 47.0502, 
    lng: 8.3093, 
    averageRating: 4.8 
  }
])

// Component refs
const filterboxRef = ref(null)

// Methods
const locationPicked = () => {
  if (filterboxRef.value) {
    filterboxRef.value.collapse()
  }
}

const doShowLogin = () => {
  loginboxShown.value = true
}

const doHideLogin = () => {
  loginboxShown.value = false
}

// Lifecycle hooks
onMounted(() => {
  // In a real app, we would fetch the user's location here
  // For now, we'll use the mock data in the store
  
  // Check if welcome box should be shown
  if (typeof localStorage !== 'undefined') {
    if (!device.isMobile.value && !localStorage.getItem('welcomeBoxHidden')) {
      welcomeboxShown.value = true
    }
  }
  
  // Set justMounted to false after 5 seconds
  setTimeout(() => {
    mainStore.$patch({ justMounted: false })
  }, 5000)
})
</script>

<style lang="scss">
body {
  position: fixed;
}

::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 7px;
}

::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.5);
  -webkit-box-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}

a {
  @apply text-blue-600;
}

a:hover {
  @apply underline;
}
</style>
