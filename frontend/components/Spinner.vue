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
    <div style="">
      <vue-loading
        type="spin"
        color="#fff"
        :size="{ width: '50px', height: '50px' }"
      ></vue-loading>
    </div>
  </div>
</template>

<script>
import { VueLoading } from 'vue-loading-template'

export default {
  name: 'Spinner',
  components: { VueLoading },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<style scoped></style>
