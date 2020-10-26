<template>
  <div class="container">
    <client-only placeholder="Loading...">
      <Map :events="allEvents.edges" />
    </client-only>
    <div>
      <vue-slider
        ref="slider"
        v-model="distanceRange"
        :min="0"
        :max="30"
      ></vue-slider>
      <select v-model="country">
        <option v-for="country in countries" :key="country">
          {{ country }}
        </option>
      </select>
      <table>
        <tbody>
          <tr
            v-for="edge in allEvents.edges"
            :key="edge.node.raceSet.edges[0].node.id"
          >
            <td>{{ edge.node.name }}</td>
            <td>{{ edge.node.location.city }}</td>
            <td>{{ edge.node.location.lat }}</td>
            <td>{{ edge.node.location.lng }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag'
import 'vue-slider-component/theme/antd.css'
export default {
  apollo: {
    allEvents: {
      query: gql`
        query($country: String!, $distanceFrom: Float!, $distanceTo: Float!) {
          allEvents(
            location_Country: $country
            race_Distance_Gte: $distanceFrom
            race_Distance_Lte: $distanceTo
          ) {
            edges {
              node {
                id
                name
                location {
                  city
                  country
                  lat
                  lng
                }
                raceSet {
                  edges {
                    node {
                      id
                      distance
                    }
                  }
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
          distanceFrom: this.distanceRange[0],
          distanceTo: this.distanceRange[1],
        }
      },
    },
  },
  data() {
    return {
      countries: ['CH', 'IT', 'AT'],
      country: 'CH',
      distanceRange: [0, 30],
    }
  },
}
</script>

<style></style>
