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
          @collapse="$emit('hide')"
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
        <div v-if="errorMessage" class="my-2 text-red-600">
          {{ errorMessage }}
        </div>
        <button type="button" @click="login">Login</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

const emit = defineEmits(['hide'])

const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')

async function login() {
  errorMessage.value = ''
  const result = await authStore.login(username.value, password.value)
  if (result.success) {
    emit('hide')
  } else {
    errorMessage.value = result.message || 'Login failed'
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
