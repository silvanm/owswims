import { format, formatDistance } from 'date-fns'
import { localeMap } from '../constants'
import { useMainStore } from '../stores/main'
import { useI18n } from '../composables/useI18n.js'

export function useEventPresentation() {
  const mainStore = useMainStore()
  const { t, locale } = useI18n()

  /**
   * Returns the boolean properties along with its labels to use
   * in the badges
   * @param event
   * @returns {{}[]}
   */
  function getBooleanProps(event) {
    const propNames = [
      {
        field: 'soldOut',
        labelTrue: t('soldOut'),
        importanceTrue: 'high',
      },
      {
        field: 'cancelled',
        labelTrue: t('cancelled'),
        importanceTrue: 'high',
      },
      {
        field: 'needsMedicalCertificate',
        labelTrue: t('needsMedical'),
        labelFalse: t('noMedical'),
        importanceTrue: 'medium',
        importanceFalse: 'low',
        infoTrue: t('needsMedicalInfo'),
      },
      {
        field: 'needsLicense',
        labelTrue: t('needsLicense'),
        importanceTrue: 'medium',
      },
      {
        field: 'withRanking',
        labelFalse: t('noRanking'),
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
  }

  function formatEventDate(dt, short, custom = null) {
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
      format(new Date(dt), fmt, { locale: localeMap[locale.value] })
    )
  }

  function formatRaceTime(tm) {
    if (!tm) {
      return ''
    } else {
      return format(new Date('2020-01-01 ' + tm), 'kk:mm')
    }
  }

  function humanizeDistance(d) {
    if (d <= 1.5) {
      return (d * 1000).toFixed(0) + t('abbreviationMeter')
    } else {
      return d.toFixed(1) + t('abbreviationKilometer')
    }
  }

  function getFormattedTravelDistance(location) {
    const k = `${location.lat},${location.lng}`
    if (
      k in mainStore.travelTimes &&
      mainStore.travelTimes[k] !== null &&
      mainStore.travelTimes[k].duration
    ) {
      const formatDuration = (s) => formatDistance(0, s * 1000)

      return `${formatDuration(mainStore.travelTimes[k].duration, {
        locale: localeMap[locale.value],
      })} (${(mainStore.travelTimes[k].distance / 1000).toFixed(0)}km)`
    } else {
      return '?'
    }
  }

  function getDirectionsUrl(location) {
    const origin = `${mainStore.mylocation.latlng.lat},${mainStore.mylocation.latlng.lng}`
    const destination = `${location.lat},${location.lng}`
    return `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}`
  }

  return {
    getBooleanProps,
    formatEventDate,
    formatRaceTime,
    humanizeDistance,
    getFormattedTravelDistance,
    getDirectionsUrl,
  }
}
