import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import gql from 'graphql-tag'

const LOGIN_MUTATION = gql`
  mutation ($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      success
      errors
      unarchiving
      token
      refreshToken
      user {
        id
        username
      }
    }
  }
`

export const useAuthStore = defineStore('auth', () => {
  // Initialize from localStorage
  const storedUser = import.meta.client ? localStorage.getItem('user') : null
  const user = ref(storedUser || null)
  const loggingIn = ref(false)

  // Getters
  const loggedIn = computed(() => !!user.value)

  // Actions
  async function login(username, password) {
    loggingIn.value = true
    try {
      const { $apollo } = useNuxtApp()
      const result = await $apollo.mutate({
        mutation: LOGIN_MUTATION,
        variables: { username, password },
      })

      if (result.data.tokenAuth.success) {
        const token = result.data.tokenAuth.token
        user.value = result.data.tokenAuth.user.username
        localStorage.setItem('user', user.value)
        localStorage.setItem('apollo-token', token)
        return { success: true }
      } else {
        const message =
          result.data.tokenAuth.errors.nonFieldErrors[0].message
        user.value = null
        return { success: false, message }
      }
    } catch (error) {
      user.value = null
      return { success: false, message: error.message }
    } finally {
      loggingIn.value = false
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('apollo-token')
  }

  return {
    user,
    loggingIn,
    loggedIn,
    login,
    logout,
  }
})
