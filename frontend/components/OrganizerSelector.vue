<template>
  <div>
    <select
      v-if="organizerWithEvents"
      v-model="organizerId"
      class="form-select w-full"
    >
      <option value="">All</option>
      <option
        v-for="node in organizerWithEvents"
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
          allOrganizers(numberOfEventsGt: 1) {
            edges {
              node {
                name
                id
                logo
                slug
                numberOfEvents
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
    organizerWithEvents() {
      if (!this.allOrganizers) {
        return []
      } else {
        return this.allOrganizers.edges.filter((o) => o.node.numberOfEvents > 1)
      }
    },
  },
  watch: {
    selectedOrganizerData(newValue, oldValue) {
      this.$store.commit('organizerData', this.selectedOrganizerData)
      const query = { organizer: this.selectedOrganizerData.slug }
      this.$urlHistory.push(query, null)
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
