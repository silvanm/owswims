<template>
  <div>
    <select
      v-if="allOrganizers"
      v-model="organizerId"
      class="form-select w-full"
    >
      <option value="">All</option>
      <option
        v-for="node in allOrganizers.edges"
        :key="node.node.id"
        :value="node.node.id"
      >
        {{ node.node.name }}
      </option>
    </select>
  </div>
</template>

<script>
import gql from 'graphql-tag'

export default {
  name: 'OrganizerSelector',
  apollo: {
    allOrganizers: {
      query: gql`
        query {
          allOrganizers {
            edges {
              node {
                name
                id
                logo
                slug
              }
            }
          }
        }
      `,
    },
  },
  data() {
    return {
      organizerId: null,
    }
  },
  watch: {
    organizerId(newValue, oldValue) {
      this.$store.commit('organizerId', newValue)
      this.$gtag('event', 'filterOrganizer')
    },
  },
}
</script>

<style scoped></style>
