import { expect, test } from '@playwright/test'

const demoPassword = process.env.E2E_DEMO_PASSWORD ?? 'Playwright-Only-1234!'

async function login(page: import('@playwright/test').Page, username: string) {
  await page.goto('/')
  await page.getByLabel('Tài khoản').fill(username)
  await page.getByLabel('Mật khẩu').fill(demoPassword)
  await page.getByRole('button', { name: 'Đăng nhập MRERP' }).click()
  await expect(page.getByRole('button', { name: /Mở hồ sơ của/ })).toBeVisible()
}

test('HR chạy pipeline tuyển dụng và chuyển ứng viên thành Employee thử việc', async ({ page }) => {
  const marker = Date.now().toString()
  const position = `QA Phase 3 ${marker}`
  const candidate = `Ứng viên ${marker}`
  await login(page, 'hr.demo')
  await expect(page.getByRole('link', { name: 'Mở ASSETCONTROL trong tab mới' })).toHaveCount(0)
  await page.getByRole('button', { name: 'Tuyển dụng', exact: true }).click()
  await page.getByRole('tab', { name: /Yêu cầu tuyển/ }).click()
  await page.getByLabel('Team').selectOption({ label: 'Alpha' })
  await page.getByLabel('Vị trí').fill(position)
  await page.getByLabel('Số lượng').fill('1')
  await page.getByLabel('Lý do').fill('Nhu cầu E2E Phase 3')
  await page.getByRole('button', { name: 'Gửi yêu cầu' }).click()
  await expect(page.locator('.recruitment-request-row').filter({ hasText: position })).toContainText('Đã duyệt')

  await page.getByRole('tab', { name: 'Pipeline ứng viên' }).click()
  await page.getByLabel('Vị trí tuyển').selectOption({ label: `${position} · Alpha` })
  await page.getByLabel('Họ tên ứng viên').fill(candidate)
  await page.getByLabel('Email ứng viên').fill(`candidate-${marker}@example.test`)
  await page.getByRole('button', { name: 'Thêm', exact: true }).click()
  await page.locator('.candidate-card').filter({ hasText: candidate }).click()
  for (const stage of ['Sàng lọc', 'Phỏng vấn', 'Đề nghị', 'Đã tuyển']) {
    await page.getByRole('button', { name: stage, exact: true }).click()
  }
  await page.getByPlaceholder('Mã nhân sự').fill(`P3-${marker}`)
  await page.getByRole('button', { name: 'Tạo nhân sự thử việc' }).click()
  await expect(page.locator('.candidate-inspector').getByRole('heading', { name: candidate })).toBeVisible()
})

test('Leader phát hành tài liệu Team và Staff trong Team đọc được', async ({ page }) => {
  const marker = Date.now().toString()
  const title = `Hướng dẫn Alpha ${marker}`
  await login(page, 'leader.demo')
  await expect(page.getByRole('link', { name: 'Mở ASSETCONTROL trong tab mới' })).toBeVisible()
  await page.getByRole('button', { name: 'Tài liệu', exact: true }).click()
  await page.getByRole('button', { name: 'Tạo tài liệu' }).click()
  const composer = page.locator('.document-composer')
  await composer.getByLabel('Tiêu đề').fill(title)
  await composer.getByLabel('Phân loại').fill('E2E')
  await composer.locator('select[multiple]').selectOption({ label: 'Alpha' })
  await composer.getByLabel('Mô tả').fill('Tài liệu kiểm thử ACL Team')
  await composer.getByLabel('File').setInputFiles({ name: 'phase3.txt', mimeType: 'text/plain', buffer: Buffer.from('MRERP Phase 3') })
  await composer.getByRole('button', { name: 'Phát hành version 1' }).click()
  await expect(page.locator('.document-row').filter({ hasText: title })).toBeVisible()

  await page.getByLabel('Xem theo vai trò debug').selectOption('staff.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Staff Alpha' })).toBeVisible()
  await page.getByRole('button', { name: 'Tài liệu', exact: true }).click()
  await expect(page.locator('.document-row').filter({ hasText: title })).toBeVisible()
})

test('Recognition tách khỏi sao, Staff thấy ledger và lưu notification preference', async ({ page }) => {
  const marker = Date.now().toString()
  const message = `Hợp tác tốt ${marker}`
  const reason = `Hoàn thành mục tiêu ${marker}`
  await login(page, 'leader.demo')
  await page.getByRole('button', { name: 'Ghi nhận & Sao', exact: true }).click()
  await page.getByLabel('Người nhận').selectOption({ label: 'Staff Alpha · Alpha' })
  await page.getByLabel('Chủ đề').fill('Hợp tác')
  await page.getByLabel('Lời nhắn').fill(message)
  await page.getByRole('button', { name: 'Gửi ghi nhận' }).click()
  await expect(page.locator('.recognition-entry').filter({ hasText: message })).toBeVisible()

  await page.locator('.star-grant-form select').selectOption({ label: 'Staff Alpha · Alpha' })
  await page.getByLabel('Số sao').fill('7')
  await page.getByLabel('Lý do').fill(reason)
  const grantResponse = page.waitForResponse((response) => response.url().includes('/api/v1/rewards/stars/grant/') && response.request().method() === 'POST')
  await page.getByRole('button', { name: 'Ghi vào ledger' }).click()
  expect((await grantResponse).status()).toBe(201)

  await page.getByLabel('Xem theo vai trò debug').selectOption('staff.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Staff Alpha' })).toBeVisible()
  await page.getByRole('button', { name: 'Ghi nhận & Sao', exact: true }).click()
  await page.getByRole('tab', { name: 'Ledger của tôi' }).click()
  await expect(page.getByText(reason, { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Cài đặt' }).click()
  await page.getByRole('button', { name: /Cài đặt cá nhân/ }).click()
  const preference = page.getByLabel('Nhận thông báo xã hội')
  if (!(await preference.isChecked())) {
    const enableResponse = page.waitForResponse((response) => response.url().includes('/api/v1/settings/me/') && response.request().method() === 'PATCH')
    await preference.check()
    expect((await enableResponse).status()).toBe(200)
  }
  const disableResponse = page.waitForResponse((response) => response.url().includes('/api/v1/settings/me/') && response.request().method() === 'PATCH')
  await preference.uncheck()
  expect((await disableResponse).status()).toBe(200)
  await expect(page.getByRole('status')).toContainText('Đã lưu')
  await page.reload()
  await page.getByRole('button', { name: 'Cài đặt' }).click()
  await page.getByRole('button', { name: /Cài đặt cá nhân/ }).click()
  await expect(page.getByLabel('Nhận thông báo xã hội')).not.toBeChecked()
  const restoreResponse = page.waitForResponse((response) => response.url().includes('/api/v1/settings/me/') && response.request().method() === 'PATCH')
  await page.getByLabel('Nhận thông báo xã hội').check()
  expect((await restoreResponse).status()).toBe(200)
})
