import { test, expect } from '@playwright/test'
import { getTestTarget, type TestTarget } from './test-target'

let testTarget: TestTarget

test.beforeAll(async () => {
  testTarget = await getTestTarget()
})

test.describe('Key app flows', () => {
  test('1. App loads', async ({ page }) => {
    await page.goto('/en')
    await expect(page.locator('#map')).toBeVisible({ timeout: 15_000 })
  })

  test('2. Markers are visible', async ({ page }) => {
    const [_, response] = await Promise.all([
      page.goto('/en'),
      page.waitForResponse(
        (res) =>
          res.url().includes('graphql') &&
          res.status() === 200 &&
          (res.request().postData()?.includes('locationsFiltered') ?? false),
        { timeout: 20_000 }
      ),
    ])
    const body = await response.json()
    const locations = body?.data?.locationsFiltered
    expect(Array.isArray(locations) && locations.length >= 1).toBeTruthy()
    await expect(page.locator('#map')).toBeVisible()
    // Wait for Google Maps to render (it injects a child div into #map)
    await expect(page.locator('#map >> div')).toBeVisible({ timeout: 15_000 })
  })

  test('3. Open event via URL shows event detail pane', async ({ page }) => {
    await page.goto(`/en?location=${encodeURIComponent(testTarget.locationId)}`)
    await expect(page.locator('#event-pane-container')).toBeVisible({
      timeout: 15_000,
    })
    await expect(page.locator('#event-pane-header')).toBeVisible()
  })

  test('4. URL updates when event is opened', async ({ page }) => {
    await page.goto(`/en?location=${encodeURIComponent(testTarget.locationId)}`)
    await expect(page.locator('#event-pane-container')).toBeVisible({
      timeout: 15_000,
    })
    await expect(page).toHaveURL(/\/en\/event\/.+/)
  })

  test('5. Direct event URL shows same event', async ({ page }) => {
    await page.goto(`/en/event/${testTarget.eventSlug}`)
    await expect(page.locator('#event-pane-container')).toBeVisible({
      timeout: 15_000,
    })
    await expect(page.locator('#event-pane-header')).toBeVisible()
  })

  test('6. Reload at event URL shows same event', async ({ page }) => {
    await page.goto(`/en/event/${testTarget.eventSlug}`)
    await expect(page.locator('#event-pane-container')).toBeVisible({
      timeout: 15_000,
    })
    const headerBefore = await page.locator('#event-pane-header').textContent()
    await page.reload()
    await expect(page.locator('#event-pane-container')).toBeVisible({
      timeout: 15_000,
    })
    const headerAfter = await page.locator('#event-pane-header').textContent()
    expect(headerAfter).toBe(headerBefore)
  })
})
