<template>
  <div>
    <div
      class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
    >
      <input
        :id="name"
        :checked="!!isChecked"
        @change="(e) => $emit('change', e.target.checked)"
        type="checkbox"
        :name="name"
        class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
      />
      <label
        :for="name"
        class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
      ></label>
    </div>
    <label :for="name" class="text-s"><slot></slot></label>
  </div>
</template>
<script>
export default {
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

<style>
/* CHECKBOX TOGGLE SWITCH */
/* @apply rules for documentation, these do not work as inline style */
.toggle-checkbox:checked {
  @apply: right-0 border-blue-500;
  right: 0;
  border-color: #4299e1;
}
.toggle-checkbox:checked + .toggle-label {
  @apply: bg-blue-500;
  background-color: #4299e1;
}
</style>
