<template>
  <client-only>
    <div class="toggle-container">
      <label :for="name" class="toggle-label"><slot></slot></label>
      <div class="toggle-switch">
        <input
          :id="name"
          :checked="!!isChecked"
          type="checkbox"
          :name="name"
          class="toggle-checkbox"
          @change="(e) => $emit('change', e.target.checked)"
        />
        <label
          :for="name"
          class="toggle-slider"
        ></label>
      </div>
    </div>
  </client-only>
</template>

<script>
export default {
  name: 'ToggleSwitch',
  // Explicitly declare emitted events (new in Vue 3)
  emits: ['change'],
  props: {
    name: {
      type: String,
      required: true,
    },
    isChecked: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<style scoped>
.toggle-container {
  display: inline-flex;
  align-items: center;
}

.toggle-label {
  font-size: 0.875rem;
  font-weight: 600;
  margin-right: 0.5rem;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 24px;
  margin-right: 0.5rem;
  vertical-align: middle;
  user-select: none;
  transition: all 0.2s ease-in;
}

.toggle-checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  border-radius: 24px;
  transition: 0.4s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  border-radius: 50%;
  transition: 0.4s;
}

.toggle-checkbox:checked + .toggle-slider {
  background-color: #4299e1;
}

.toggle-checkbox:checked + .toggle-slider:before {
  transform: translateX(16px);
}
</style>
