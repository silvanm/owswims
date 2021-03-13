import { format, formatDistance } from 'date-fns'
import { localeMap } from '../constants'

export default {
  methods: {
    /**
     * Returns the boolean properties along with its labels to use
     * in the badges
     * @param event
     * @returns {{}[]}
     */
    getBooleanProps(event) {
      const propNames = [
        {
          field: 'soldOut',
          labelTrue: this.$t('soldOut'),
          importanceTrue: 'high',
        },
        {
          field: 'cancelled',
          labelTrue: this.$t('cancelled'),
          importanceTrue: 'high',
        },
        {
          field: 'needsMedicalCertificate',
          labelTrue: this.$t('needsMedical'),
          labelFalse: this.$t('noMedical'),
          importanceTrue: 'medium',
          importanceFalse: 'low',
          infoTrue: this.$t('needsMedicalInfo'),
        },
        {
          field: 'needsLicense',
          labelTrue: this.$t('needsLicense'),
          importanceTrue: 'medium',
        },
        {
          field: 'withRanking',
          labelFalse: this.$t('noRanking'),
          importanceFalse: 'low',
        },
      ]

      return propNames
        .map((o) => {
          const r = {}
          r.id = o.field
          r.state = event[o.field]
          if (r.state === true) {
            r.label = o.labelTrue
            r.importance = o.importanceTrue
            r.info = o.infoTrue ?? false
          }
          if (r.state === false) {
            r.label = o.labelFalse
            r.importance = o.importanceFalse
            r.info = o.infoFalse ?? false
          }
          return r
        })
        .filter((o) => o.label)
    },
    formatEventDate(dt, short, custom = null) {
      const capitalize = (s) => {
        if (typeof s !== 'string') return ''
        return s.charAt(0).toUpperCase() + s.slice(1)
      }

      let fmt
      if (custom) {
        fmt = custom
      } else if (short) {
        fmt = 'E d. MMM.'
      } else {
        fmt = 'EEEE, d. MMMM yyyy'
      }

      return capitalize(
        format(new Date(dt), fmt, { locale: localeMap[this.$i18n.locale] })
      )
    },
    formatRaceTime(tm) {
      if (tm) {
        return ''
      } else {
        return format(new Date('2020-01-01 ' + tm), 'kk:mm')
      }
    },
    humanizeDistance(d) {
      if (d <= 1.5) {
        return (d * 1000).toFixed(0) + this.$t('abbreviationMeter')
      } else {
        return d.toFixed(1) + this.$t('abbreviationKilometer')
      }
    },
    getFormattedTravelDistance(location, travelMode) {
      const k = `${location.lat},${location.lng}`
      if (
        k in this.$store.getters.travelTimes &&
        this.$store.getters.travelTimes[k] !== null &&
        this.$store.getters.travelTimes[k].duration
      ) {
        const formatDuration = (s) => formatDistance(0, s * 1000)

        return `${formatDuration(this.$store.getters.travelTimes[k].duration, {
          locale: localeMap[this.$i18n.locale],
        })} (${(this.$store.getters.travelTimes[k].distance / 1000).toFixed(
          0
        )}km)`
      } else {
        return '?'
      }
    },
    getDirectionsUrl(location, travelMode) {
      const origin = `${this.$store.getters.mylocation.latlng.lat},${this.$store.getters.mylocation.latlng.lng}`
      const destination = `${location.lat},${location.lng}`
      return `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}`
    },
  },
}
