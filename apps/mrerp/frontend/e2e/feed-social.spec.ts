import { expect, test } from '@playwright/test'

test('Staff đăng file, người khác tương tác/share và HR moderation', async ({ page }) => {
  const password = process.env.E2E_DEMO_PASSWORD ?? 'Playwright-Only-1234!'
  const marker = `E2E Feed ${Date.now()}`
  await page.goto('/')
  await page.getByLabel('Tài khoản').fill('staff.demo')
  await page.getByLabel('Mật khẩu').fill(password)
  await page.getByRole('button', { name: 'Đăng nhập MRERP' }).click()
  await page.getByRole('button', { name: 'Bảng tin', exact: true }).click()
  await page.getByPlaceholder(/Thông báo, cập nhật/).fill(marker)
  await page.locator('.feed-composer input[type=file]').setInputFiles({
    name: 'evidence.png',
    mimeType: 'image/png',
    buffer: Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x70, 0x77]),
  })
  await page.getByRole('button', { name: 'Đăng bài' }).click()
  await expect(page.locator('.feed-post-card').filter({ hasText: marker })).toBeVisible()

  await page.getByLabel('Xem theo vai trò debug').selectOption('other.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Staff Beta' })).toBeVisible()
  await page.getByRole('button', { name: 'Bảng tin', exact: true }).click()
  const post = page.locator('.feed-post-card').filter({ hasText: marker })
  await post.getByPlaceholder('Viết bình luận…').fill('Đã nhận thông tin')
  await post.getByRole('button', { name: 'Gửi', exact: true }).click()
  await expect(post.getByText('Đã nhận thông tin', { exact: true })).toBeVisible()
  await post.locator('.post-actions').getByRole('button', { name: 'Thích', exact: true }).click()
  await expect(post).toContainText('1 cảm xúc')
  await post.locator('.post-actions').getByRole('button', { name: 'Chia sẻ', exact: true }).click()
  await post.getByRole('button', { name: 'Chia sẻ an toàn' }).click()
  await expect(page.locator('.feed-post-card').filter({ hasText: marker })).toHaveCount(2)

  await page.getByLabel('Xem theo vai trò debug').selectOption('hr.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của HR Demo' })).toBeVisible()
  await page.getByRole('button', { name: 'Bảng tin', exact: true }).click()
  await expect(page.locator('.feed-post-card').filter({ hasText: marker })).toHaveCount(2)
  const original = page.locator('.feed-post-card').filter({ hasText: marker }).last()
  await original.getByRole('button', { name: 'Xóa bài viết' }).click()
  await expect(page.getByText('Nội dung gốc không còn khả dụng').first()).toBeVisible()
})
