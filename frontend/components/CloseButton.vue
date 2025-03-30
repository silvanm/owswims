<template>
  <client-only>
    <div 
      class="close-button"
      @click="click"
    >
      <div 
        class="plus-icon"
        :style="{ transform: `rotate(${collapsed && !isStatic ? 0 : 45}deg)` }"
      ></div>
    </div>
  </client-only>
</template>

<script>
export default {
  name: 'CloseButton',
  // Explicitly declare emitted events (new in Vue 3)
  emits: ['collapse', 'expand'],
  props: {
    isStatic: {
      type: Boolean,
      default: false,
    },
  },
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
.close-button {
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plus-icon {
  position: relative;
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.plus-icon::before,
.plus-icon::after {
  content: '';
  position: absolute;
  background-color: #333;
}

.plus-icon::before {
  width: 100%;
  height: 2px;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
}

.plus-icon::after {
  width: 2px;
  height: 100%;
  left: 50%;
  top: 0;
  transform: translateX(-50%);
}
</style>
