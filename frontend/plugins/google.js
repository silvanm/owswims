import { Loader } from 'google-maps'

export default ({ app }, inject) => {
  let google = null

  inject('google', async (msg) => {
    const loader = new Loader(process.env.googleMapsKey, { version: 'beta' })
    if (google) {
      return google
    } else {
      google = await loader.load()
    }
  })
}
