<template>
  <div class="bg-white p-4 md:p-6 mt-4 relative">
    Picked Location Id: {{ pickedLocationId }}

    <div v-if="location">
      {{ location.city }}
      {{ location.country }}

      <input v-model="location.city" type="text" />
      <button @click="save">Save</button>
    </div>

    <!--
    <h2>Paris, France</h2>

    <div>
      <h3>Sat 18. Jul. 2020</h3>
      <p>Open Swim Stars Paris</p>
      <p>10.0km, 5.0km, 2.0km, 1.0km</p>
    </div>

    <div>
      <h3>Sun 13. Sep. 2020</h3>
      <p>EDF Aqua Challenge Paris</p>
      <p>5.0km, 2.5km, 1.3km</p>
    </div>
    <h1 class="text-xl font-semibold">
          {{ pickedLocation.city }}, {{ pickedLocation.country }}
        </h1>
        <span v-if="mylocation.lat">
          Travel time:
          {{ formattedTravelDistance }}
        </span>
        <div v-for="event in allEvents.edges" :key="event.node.id">
          <div style="margin-top: 10px">
            {{ formatEventDate(event.node.dateStart) }}<br />
            <a :href="event.node.website" class="font-semibold">{{
              event.node.name
            }}</a
            ><br />
            {{ formatRaceDistances(event.node.races) }}
          </div>
        </div> -->
  </div>
</template>
<script>
import { mapGetters } from 'vuex'
import gql from 'graphql-tag'

export default {
  apollo: {
    location: {
      query: gql`
        query($locationId: ID!) {
          location(id: $locationId) {
            country
            city
          }
        }
      `,
      variables() {
        return {
          locationId: this.pickedLocationId,
        }
      },
      watchLoading(isLoading, countModifier) {
        this.isLoading = isLoading
      },
    },
  },
  date() {
    return {}
  },
  computed: {
    ...mapGetters(['pickedLocationId']),
  },
  methods: {
    save() {

    }
  }
}
</script>
