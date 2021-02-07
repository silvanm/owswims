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
import { mapGetters } from 'vuex'

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
  computed: {
    ...mapGetters(['organizerData']),
    selectedOrganizerData() {
      if (this.allOrganizers && this.organizerId) {
        return this.allOrganizers.edges.find(
          (o) => o.node.id === this.organizerId
        ).node
      } else {
        return null
      }
    },
  },
  watch: {
    selectedOrganizerData(newValue, oldValue) {
      this.$store.commit('organizerData', this.selectedOrganizerData)
      const query = { ...this.$router.currentRoute.query }
      query.organizer = this.selectedOrganizerData.slug
      this.$router.push({
        query,
      })
      this.$gtag('event', 'filterOrganizer')
    },
  },
  mounted() {
    if (this.organizerData) {
      this.organizerId = this.organizerData.id
    }
  },
}
</script>

<style scoped></style>
