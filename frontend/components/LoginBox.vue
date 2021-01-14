<template>
  <div
    class="absolute flex items-center justify-center h-screen w-screen"
    style="z-index: 5"
  >
    <div class="rounded border-blue-600 border-2 p-4 bg-white">
      <h1 class="font-bold text-xl">Login</h1>
      <div>
        <label for="username">Username</label>
        <input id="username" v-model="username" />
      </div>

      <div>
        <label>Password</label>
        <input id="password" type="password" v-model="password" />
      </div>
      <button type="submit" @click="login">Login</button>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      result: '',
    }
  },
  methods: {
    async login() {
      await this.$store.dispatch('auth/login', {
        username: this.username,
        password: this.password,
      })
      this.$emit('hide')
    },
  },
}
</script>
<style lang="scss" scoped>
div {
  input {
    @apply border m-2 p-2;
  }

  button {
    @apply bg-blue-600 rounded p-2 text-white font-bold;
  }
}
</style>
