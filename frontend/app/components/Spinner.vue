<template>
  <div
    v-if="show"
    style="
      position: absolute;
      width: 100%;
      height: 100%;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: center;
    "
  >
    <div class="spinner"></div>
  </div>
</template>

<script>
export default {
  name: 'Spinner',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<style scoped>
.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
