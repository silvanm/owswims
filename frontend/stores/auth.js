// stores/auth.js
import { defineStore } from 'pinia'
import gql from 'graphql-tag'
import { useNuxtApp } from '#app'

// Get user from localStorage if available
const getUserFromStorage = () => {
  if (typeof localStorage !== 'undefined') {
    return localStorage.getItem('user')
  }
  return null
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    const user = getUserFromStorage()
    return user
      ? { status: { loggedIn: true }, user }
      : { status: {}, user: null }
  },

  getters: {
    loggedIn: (state) => state.status.loggedIn || false,
    user: (state) => state.user,
  },

  actions: {
    async login({ username, password }) {
      this.status = { loggingIn: true }
      this.user = username

      try {
        const nuxtApp = useNuxtApp()
        const client = nuxtApp.apolloProvider.defaultClient
        const result = await client.mutate({
          mutation: gql`
            mutation($username: String!, $password: String!) {
              tokenAuth(username: $username, password: $password) {
                success
                errors
                unarchiving
                token
                refreshToken
                unarchiving
                user {
                  id
                  username
                }
              }
            }
          `,
          variables: {
            username,
            password,
          },
        })

        // Handle Apollo helpers for token management
        const apolloHelpers = nuxtApp.$apolloHelpers
        await apolloHelpers.onLogin(result.data.tokenAuth.token)

        if (result.data.tokenAuth.success) {
          this.status = { loggedIn: true }
          this.user = result.data.tokenAuth.user.username
          localStorage.setItem('user', result.data.tokenAuth.user.username)
          nuxtApp.$toast.success('Successfully authenticated')
        } else {
          const message = result.data.tokenAuth.errors.nonFieldErrors[0].message
          this.status = {}
          this.user = null
          nuxtApp.$toast.error(message)
        }
      } catch (error) {
        this.status = {}
        this.user = null
        useNuxtApp().$toast.error('Authentication failed')
        console.error('Login error:', error)
      }
    },

    async logout() {
      try {
        const nuxtApp = useNuxtApp()
        await nuxtApp.$apolloHelpers.onLogout()
        localStorage.removeItem('user')
        this.status = {}
        this.user = null
      } catch (error) {
        console.error('Logout error:', error)
      }
    },
  },
})
