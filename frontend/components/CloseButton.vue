<template>
  <div class="inline">
    <svg
      v-if="collapsed"
      class="collapse-icon"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      @click="expand"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
      />
    </svg>
    <svg
      v-if="!collapsed"
      class="collapse-icon"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      @click="collapse"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  </div>
</template>

<script>
export default {
  name: 'CloseButton',
  data() {
    return {
      collapsed: false,
    }
  },
  methods: {
    collapse() {
      this.$emit('collapse')
      this.collapsed = true
    },
    expand() {
      this.$emit('expand')
      this.collapsed = false
    },
  },
}
</script>

<style scoped>
.collapse-icon {
  @apply h-6 w-6 float-right mt-1 cursor-pointer;
}
</style>
