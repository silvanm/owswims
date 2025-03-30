<template>
  <client-only>
    <div
      v-if="show"
      class="spinner-overlay"
    >
      <div class="spinner-container">
        <div class="spinner"></div>
      </div>
    </div>
  </client-only>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<style scoped>
.spinner-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.3);
}

.spinner-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
