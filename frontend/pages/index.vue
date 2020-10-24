<template>
  <div class="container">
    <div>
      <select v-model="country">
        <option v-for="country in countries" :key="country">
          {{ country }}
        </option>
      </select>
      <table>
        <tr v-for="edge in allEvents.edges" :key="edge.node.id">
          <td>{{ edge.node.name }}</td>
          <td>{{ edge.node.location.city }}</td>
        </tr>
      </table>
      <div class="links">
        <a
          href="https://nuxtjs.org/"
          target="_blank"
          rel="noopener noreferrer"
          class="button--green"
        >
          Documentation
        </a>
        <a
          href="https://github.com/nuxt/nuxt.js"
          target="_blank"
          rel="noopener noreferrer"
          class="button--grey"
        >
          GitHub
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag'

export default {
  apollo: {
    // Simple query that will update the 'hello' vue property
    allEvents: {
      query: gql`
        query($country: String!) {
          allEvents(location_Country: $country) {
            edges {
              node {
                id
                name
                location {
                  city
                  country
                }
              }
            }
          }
        }
      `,
      variables() {
        // Use vue reactive properties here
        return {
          country: this.country,
        }
      },
    },
  },
  data() {
    return {
      countries: ['CH', 'IT', 'AT'],
      country: 'CH',
    }
  },
}
</script>

<style></style>
