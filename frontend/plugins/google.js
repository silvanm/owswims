import { Loader } from 'google-maps'

export default ({ app }, inject) => {
  inject('google', async (msg) => {
    if (window.google) {
      return window.google
    } else {
      const loader = new Loader(process.env.googleMapsKey, { version: 'beta' })
      window.google = await loader.load()
    }
  })
}
