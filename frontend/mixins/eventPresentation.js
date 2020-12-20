import { format } from 'date-fns'

export default {
  methods: {
    formatEventDate(dt, short) {
      let fmt
      if (short) {
        fmt = 'E dd. MMM.'
      } else {
        fmt = 'E dd. MMM. yyyy'
      }
      return format(new Date(dt), fmt)
    },
    humanizeDistance(d) {
      if (d <= 1.5) {
        return (d * 1000).toFixed(0) + 'm'
      } else {
        return d.toFixed(0) + 'km'
      }
    },
  },
}
