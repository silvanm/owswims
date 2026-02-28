<template>
  <div class="inline">
    <label :for="name" class="text-s font-semibold mr-2"><slot></slot></label>
    <div
      class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
    >
      <input
        :id="name"
        :checked="!!modelValue"
        type="checkbox"
        :name="name"
        class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
        @change="(e) => $emit('update:modelValue', e.target.checked)"
      />
      <label
        :for="name"
        class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
      ></label>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Toggle',
  props: {
    name: {
      type: String,
      required: true,
    },
    modelValue: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:modelValue'],
}
</script>

<style>
.toggle-checkbox:checked {
  right: 0;
  border-color: #4299e1;
}
.toggle-checkbox:checked + .toggle-label {
  background-color: #4299e1;
}
</style>
