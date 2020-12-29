<template>
  <font-awesome-icon
    class="cursor-pointer"
    icon="plus"
    size="lg"
    :transform="{ rotate: collapsed ? 0 : 45 }"
    @click="click"
  ></font-awesome-icon>
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
    click() {
      if (this.collapsed) {
        this.expand()
      } else {
        this.collapse()
      }
    },
  },
}
</script>

<style scoped>
.collapse-icon {
  @apply h-6 w-6 float-right mt-1 cursor-pointer;
}
</style>
