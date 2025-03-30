// stores/auth.js
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    status: { loggedIn: true },
    user: 'testuser',
  }),

  getters: {
    loggedIn: (state) => state.status.loggedIn || false,
    user: (state) => state.user,
  },

  actions: {
    async login({ username }) {
      // Simplified login for testing
      this.status = { loggedIn: true }
      this.user = username
      console.log('Logged in as:', username)
    },

    async logout() {
      // Simplified logout for testing
      this.status = { loggedIn: false }
      this.user = null
      console.log('Logged out')
    },
  },
})
