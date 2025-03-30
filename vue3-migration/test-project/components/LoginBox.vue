<template>
  <div
    class="absolute flex items-center justify-center h-screen w-screen"
    style="z-index: 5"
  >
    <div class="p-4 bg-white shadow-xl">
      <div class="float-right">
        <CloseButton
          ref="closebutton"
          :is-static="true"
          @collapse="emit('hide')"
        ></CloseButton>
      </div>
      <h1 class="font-bold text-xl">Login</h1>
      <form>
        <div class="my-2">
          <label for="username" class="block">Username</label>
          <input
            id="username"
            v-model="username"
            class="block"
            autocomplete="username"
          />
        </div>

        <div class="my-2">
          <label class="block">Password</label>
          <input
            id="password"
            v-model="password"
            class="block"
            type="password"
            autocomplete="current-password"
          />
        </div>
        <button type="button" @click="login">Login</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import CloseButton from './CloseButton.vue'

// Define emits
const emit = defineEmits(['hide'])

// Setup store
const authStore = useAuthStore()

// Reactive state
const username = ref('')
const password = ref('')

// Methods
const login = async () => {
  try {
    await authStore.login({
      username: username.value,
      password: password.value,
    })
  } catch (e) {
    console.error('Login error:', e)
  }
}
</script>

<style lang="scss" scoped>
div {
  input {
    @apply border p-2;
    width: 300px;
  }

  button {
    @apply bg-blue-600 rounded p-2 text-white font-bold;
  }
}
</style>
