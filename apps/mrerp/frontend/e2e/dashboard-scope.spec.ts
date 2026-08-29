import { expect, test } from '@playwright/test'

test('Dashboard tách company và direct notification theo persona', async ({ page }) => {
  const password = process.env.E2E_DEMO_PASSWORD ?? 'Playwright-Only-1234!'
  const marker = `${Date.now()}`
  const companyText = `Company E2E ${marker}`
  const directText = `Direct E2E ${marker}`
  await page.goto('/')
  await page.getByLabel('Tài khoản').fill('leader.demo')
  await page.getByLabel('Mật khẩu').fill(password)
  await page.getByRole('button', { name: 'Đăng nhập MRERP' }).click()
  await page.getByRole('button', { name: 'Bảng tin', exact: true }).click()
  await page.getByPlaceholder(/Thông báo, cập nhật/).fill(companyText)
  await page.getByRole('button', { name: 'Đăng bài' }).click()
  await expect(page.locator('.feed-post-card').filter({ hasText: companyText })).toBeVisible()
  await page.getByPlaceholder(/Thông báo, cập nhật/).fill(directText)
  await page.getByLabel('Toàn công ty').uncheck()
  await page.getByRole('checkbox', { name: /^Staff Alpha\b/ }).check()
  await page.getByRole('button', { name: 'Đăng bài' }).click()
  await expect(page.locator('.feed-post-card').filter({ hasText: directText })).toBeVisible()

  await page.getByLabel('Xem theo vai trò debug').selectOption('other.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Staff Beta' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Tổng quan' })).toBeVisible()
  await expect(page.locator('.dashboard-stream--general')).toContainText(companyText)
  await expect(page.locator('.dashboard-stream--private')).not.toContainText(directText)

  await page.getByLabel('Xem theo vai trò debug').selectOption('staff.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Staff Alpha' })).toBeVisible()
  await expect(page.locator('.dashboard-stream--general')).toContainText(companyText)
  await expect(page.locator('.dashboard-stream--private')).toContainText('Leader Alpha đã chia sẻ với bạn')
  await expect(page.locator('.dashboard-stream--private')).toContainText(directText)

  const notificationButton = page.getByRole('button', { name: /Thông báo, \d+ chưa đọc/ })
  await expect(notificationButton).toBeVisible()
  await notificationButton.click()
  await expect(page.getByRole('dialog', { name: 'Thông báo của tôi' })).toContainText(directText)

  await page.getByRole('button', { name: 'Cài đặt' }).click()
  const themeToggle = page.getByRole('checkbox', { name: 'Nền tối' })
  await page.locator('.theme-toggle').click()
  await expect(themeToggle).toBeChecked()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await page.reload()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await page.getByRole('button', { name: 'Cài đặt' }).click()
  await page.locator('.theme-toggle').click()
  await expect(page.getByRole('checkbox', { name: 'Nền tối' })).not.toBeChecked()
})
