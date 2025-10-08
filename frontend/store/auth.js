import gql from 'graphql-tag'

const user = localStorage.getItem('user')
const initialState = user
  ? { status: { loggedIn: true }, user }
  : { status: {}, user: null }

export default {
  namespaced: true,
  state: () => {
    return initialState
  },
  actions: {
    login({ dispatch, commit }, { username, password }) {
      commit('loginRequest', { username })

      const client = this.app.apolloProvider.defaultClient
      client
        .mutate({
          mutation: gql`
            mutation ($username: String!, $password: String!) {
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
          // Parameters
          variables: {
            username,
            password,
          },
        })
        .then((result) => {
          this.$apolloHelpers.onLogin(result.data.tokenAuth.token)
          if (result.data.tokenAuth.success) {
            commit('loginSuccess', result.data.tokenAuth.user.username)
            localStorage.setItem('user', result.data.tokenAuth.user.username)
            this.$toast.success('Successfully authenticated')
          } else {
            const message =
              result.data.tokenAuth.errors.nonFieldErrors[0].message
            commit('loginFailure')
            this.$toast.error(message)
          }
        })
    },
    logout({ commit }) {
      this.$apolloHelpers.onLogout()
      localStorage.removeItem('user')
      commit('logout')
    },
  },
  mutations: {
    loginRequest(state, user) {
      state.status = { loggingIn: true }
      state.user = user
    },
    loginSuccess(state, user) {
      state.status = { loggedIn: true }
      state.user = user
    },
    loginFailure(state, message) {
      state.status = {}
      state.user = null
    },
    logout(state) {
      state.status = {}
      state.user = null
    },
  },
  getters: {
    loggedIn(s) {
      return s.status.loggedIn
    },
    user(s) {
      return s.user
    },
  },
}
