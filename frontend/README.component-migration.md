# Vue 3 Component Migration Guide

This document outlines the approach for migrating Vue 2 components to Vue 3 as part of the OWSwims frontend migration.

## Migration Strategy

The component migration will follow these steps:

1. Start with shared UI components (smaller, reusable components)
2. Move to page components and more complex components
3. Special focus on the Map component due to its complexity and importance

## Component Changes Required

When migrating components from Vue 2 to Vue 3, the following changes need to be considered:

### Template Changes

- **Multiple Root Elements**: Vue 3 supports multiple root elements in templates (fragments)
- **v-model Changes**: Update v-model usage (property and event names have changed)
  - Vue 2: `v-model` uses `value` prop and `input` event
  - Vue 3: `v-model` uses `modelValue` prop and `update:modelValue` event
- **v-bind Order**: `v-bind="object"` now spreads properties in a different order
- **v-on:event.native Removal**: The `.native` modifier has been removed

### Script Changes

- **Composition API**: Consider using the Composition API for more complex components
- **Lifecycle Hooks**: Update lifecycle hook names
  - `beforeDestroy` → `beforeUnmount`
  - `destroyed` → `unmounted`
- **Emits Option**: Add explicit `emits` option to declare emitted events
- **Functional Components**: Update functional components to use a plain function

## Migration Approaches

### Option 1: Options API with Vue 3 Updates

For simpler components, we can keep using the Options API but update it for Vue 3 compatibility:

```vue
<template>
  <!-- Template with Vue 3 syntax -->
</template>

<script>
export default {
  name: 'ComponentName',
  // New in Vue 3: explicitly declare emitted events
  emits: ['change', 'update'],
  props: {
    // Props
  },
  data() {
    return {
      // Data
    }
  },
  methods: {
    // Methods
  }
}
</script>
```

### Option 2: Composition API with `setup()` Function

For more complex components, we can use the Composition API with the `setup()` function:

```vue
<template>
  <!-- Template with Vue 3 syntax -->
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ComponentName',
  props: {
    // Props
  },
  emits: ['change', 'update'],
  setup(props, { emit }) {
    // State
    const count = ref(0)
    
    // Computed properties
    const doubleCount = computed(() => count.value * 2)
    
    // Methods
    function increment() {
      count.value++
      emit('change', count.value)
    }
    
    // Lifecycle hooks
    onMounted(() => {
      console.log('Component mounted')
    })
    
    // Expose to template
    return {
      count,
      doubleCount,
      increment
    }
  }
}
</script>
```

### Option 3: Composition API with `<script setup>` (Recommended for New Components)

For the most concise syntax, we can use the `<script setup>` syntax:

```vue
<template>
  <!-- Template with Vue 3 syntax -->
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  initialValue: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['change', 'update'])

// State
const count = ref(props.initialValue)

// Computed properties
const doubleCount = computed(() => count.value * 2)

// Methods
function increment() {
  count.value++
  emit('change', count.value)
}

// Lifecycle hooks
onMounted(() => {
  console.log('Component mounted')
})

// No need to return anything - all variables are automatically exposed to the template
</script>
```

## Component Migration Examples

### Example 1: CloseButton.vue

#### Vue 2 Version:
```vue
<template>
  <font-awesome-icon
    class="cursor-pointer"
    icon="plus"
    size="lg"
    :transform="{ rotate: collapsed && !isStatic ? 0 : 45 }"
    @click="click"
  ></font-awesome-icon>
</template>

<script>
export default {
  name: 'CloseButton',
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
```

#### Vue 3 Version (Options API):
```vue
<template>
  <font-awesome-icon
    class="cursor-pointer"
    icon="plus"
    size="lg"
    :transform="{ rotate: collapsed && !isStatic ? 0 : 45 }"
    @click="click"
  ></font-awesome-icon>
</template>

<script>
export default {
  name: 'CloseButton',
  // Explicitly declare emitted events
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
```

#### Vue 3 Version (Composition API with `<script setup>`):
```vue
<template>
  <font-awesome-icon
    class="cursor-pointer"
    icon="plus"
    size="lg"
    :transform="{ rotate: collapsed && !isStatic ? 0 : 45 }"
    @click="click"
  ></font-awesome-icon>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  isStatic: {
    type: Boolean,
    default: false,
  },
})

// Emits
const emit = defineEmits(['collapse', 'expand'])

// State
const collapsed = ref(false)

// Methods
function collapse() {
  emit('collapse')
  collapsed.value = true
}

function expand() {
  emit('expand')
  collapsed.value = false
}

function click() {
  if (collapsed.value) {
    expand()
  } else {
    collapse()
  }
}
</script>
```

### Example 2: Toggle.vue

#### Vue 2 Version:
```vue
<template>
  <div class="inline">
    <label :for="name" class="text-s font-semibold mr-2"><slot></slot></label>
    <div
      class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
    >
      <input
        :id="name"
        :checked="!!isChecked"
        type="checkbox"
        :name="name"
        class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
        @change="(e) => $emit('change', e.target.checked)"
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
```

#### Vue 3 Version (Options API):
```vue
<template>
  <div class="inline">
    <label :for="name" class="text-s font-semibold mr-2"><slot></slot></label>
    <div
      class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
    >
      <input
        :id="name"
        :checked="!!isChecked"
        type="checkbox"
        :name="name"
        class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
        @change="(e) => $emit('change', e.target.checked)"
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
  // Explicitly declare emitted events
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
```

#### Vue 3 Version (Composition API with `<script setup>`):
```vue
<template>
  <div class="inline">
    <label :for="name" class="text-s font-semibold mr-2"><slot></slot></label>
    <div
      class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in"
    >
      <input
        :id="name"
        :checked="!!isChecked"
        type="checkbox"
        :name="name"
        class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
        @change="(e) => emit('change', e.target.checked)"
      />
      <label
        :for="name"
        class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
      ></label>
    </div>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  isChecked: {
    type: Boolean,
    default: false,
  },
})

// Emits
const emit = defineEmits(['change'])
</script>
```

## Component Migration Checklist

For each component, follow this checklist:

1. **Template Updates**
   - [ ] Check for multiple root elements (fragments)
   - [ ] Update v-model usage
   - [ ] Remove v-on:event.native modifiers

2. **Script Updates**
   - [ ] Add explicit emits option
   - [ ] Update lifecycle hook names
   - [ ] Consider using Composition API for complex components
   - [ ] Update any Vue 2 specific APIs
   - [ ] No need to worry about SSR compatibility (SSR has been disabled)

3. **Dependencies**
   - [ ] Check for Vue 2 specific dependencies
   - [ ] Replace with Vue 3 compatible alternatives

4. **Testing**
   - [ ] Test the component in isolation
   - [ ] Test the component in the context of the application
   - [ ] Verify all functionality works as expected

## Migration Progress

| Component | Status | Approach | Notes |
|-----------|--------|----------|-------|
| CloseButton.vue | Not Started | Options API | Simple component, good candidate for first migration |
| Spinner.vue | Not Started | Options API | Depends on vue-loading-template, need to check compatibility |
| Toggle.vue | Not Started | Options API | Simple component, good candidate for early migration |
| Ribbon.vue | Not Started | TBD | Need to analyze complexity |
| OrganizerLogo.vue | Not Started | TBD | Need to analyze complexity |

## Resources

- [Vue 3 Migration Guide](https://v3-migration.vuejs.org/)
- [Vue 3 Composition API Documentation](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Script Setup Documentation](https://vuejs.org/api/sfc-script-setup.html)
