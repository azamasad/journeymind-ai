import { test, expect } from '@playwright/test'

const API = 'http://localhost:8000'

test.describe('Backend API', () => {
  test('health endpoint returns ok', async ({ request }) => {
    const res = await request.get(`${API}/`)
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.status).toBe('ok')
  })

  test('dashboard returns orchestration fields', async ({ request }) => {
    const res = await request.get(`${API}/dashboard`)
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body).toHaveProperty('decision_timeline')
    expect(body).toHaveProperty('journey_summary')
    expect(body).toHaveProperty('business_impact')
    expect(body).toHaveProperty('explainability')
    expect(body.current_journey).toHaveProperty('flight_number')
    expect(body.current_journey).toHaveProperty('status')
  })

  test('recommendations returns alternatives with reasoning', async ({ request }) => {
    const res = await request.get(`${API}/recommendations`)
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.alternatives.length).toBeGreaterThan(0)
    expect(body.alternatives[0]).toHaveProperty('decision_factors')
    expect(body.recommendations[0]).toHaveProperty('confidence')
  })

  test('rebook updates the journey', async ({ request }) => {
    const recs = await request.get(`${API}/recommendations`)
    const { alternatives } = await recs.json()
    const id = alternatives[0].id
    const res = await request.post(`${API}/rebook`, { data: { option_id: id } })
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.success).toBe(true)
    expect(body.current_journey.status).toBe('Confirmed')
  })

  test('chat returns context-aware response', async ({ request }) => {
    const res = await request.post(`${API}/chat`, { data: { message: 'What are my options?' } })
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.reply.length).toBeGreaterThan(0)
    expect(body).toHaveProperty('source')
  })

  test('alerts and mockdata endpoints work', async ({ request }) => {
    const alerts = await request.get(`${API}/alerts`)
    expect(alerts.ok()).toBeTruthy()
    const data = await request.get(`${API}/mockdata`)
    expect(data.ok()).toBeTruthy()
  })
})

test.describe('Frontend UI', () => {
  test('dashboard loads and shows decision timeline', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('AI Decision Timeline')).toBeVisible()
    await expect(page.getByText('Business Impact')).toBeVisible()
    await expect(page.getByText('Journey Summary')).toBeVisible()
    await expect(page.getByText('Accept AI Recommendation')).toBeVisible()
  })

  test('rebooking updates the journey', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: /Accept AI Recommendation/i }).click()
    await expect(page.getByText('Itinerary updated')).toBeVisible()
    await expect(page.getByText('Journey optimized', { exact: true })).toBeVisible({ timeout: 5000 })
  })

  test('explainability modal opens', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: /Why this recommendation?/i }).click()
    await expect(page.getByText('Decision Inputs')).toBeVisible()
    await expect(page.getByText('Decision Process')).toBeVisible()
  })

  test('architecture modal opens', async ({ page }) => {
    await page.goto('/')
    if ((page.viewportSize()?.width || 0) < 640) {
      test.skip()
    }
    await page.getByRole('button', { name: /How it works/i }).click()
    await expect(page.getByText('How JourneyMind Works')).toBeVisible()
    await expect(page.getByText('AI Orchestrator')).toBeVisible()
  })

  test('copilot responds with journey context', async ({ page }) => {
    await page.goto('/')
    await page.getByText('What are my options?').click()
    await expect(page.getByText(/evaluated/i)).toBeVisible({ timeout: 5000 })
  })
})
