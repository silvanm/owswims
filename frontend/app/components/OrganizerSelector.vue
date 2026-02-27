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
import { useMainStore } from '~/stores/main'

const ALL_ORGANIZERS_QUERY = gql`
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
`

export default {
  name: 'OrganizerSelector',
  setup() {
    const store = useMainStore()
    const router = useRouter()
    const { $apollo } = useNuxtApp()
    return { store, router, $apollo }
  },
  data() {
    return {
      organizerId: null,
      allOrganizers: null,
    }
  },
  computed: {
    selectedOrganizerData() {
      if (this.allOrganizers && this.organizerId) {
        const found = this.allOrganizers.edges.find(
          (o) => o.node.id === this.organizerId
        )
        return found ? found.node : null
      }
      return null
    },
    organizerWithEvents() {
      if (!this.allOrganizers) {
        return []
      }
      return this.allOrganizers.edges.filter((o) => o.node.numberOfEvents > 1)
    },
  },
  watch: {
    selectedOrganizerData(newValue) {
      if (newValue) {
        this.store.organizerData = newValue
        this.router.push({ query: { organizer: newValue.slug } })
      }
    },
  },
  async mounted() {
    if (this.store.organizerData) {
      this.organizerId = this.store.organizerData.id
    }
    try {
      const result = await this.$apollo.query({ query: ALL_ORGANIZERS_QUERY })
      this.allOrganizers = result.data.allOrganizers
    } catch (error) {
      console.error('Error fetching organizers:', error)
    }
  },
}
</script>

<style scoped></style>
