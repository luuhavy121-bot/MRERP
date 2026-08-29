import { expect, test } from '@playwright/test'

test('Staff gửi đơn, Leader duyệt và HR thấy công bị ảnh hưởng', async ({ page }) => {
  const demoPassword = process.env.E2E_DEMO_PASSWORD ?? 'Playwright-Only-1234!'
  const seed = Date.now() + Math.floor(Math.random() * 1_000_000)
  const year = 3000 + (seed % 6000)
  const monthIndex = Math.floor(seed / 6000) % 12
  let monday = 1
  while (new Date(Date.UTC(year, monthIndex, monday)).getUTCDay() !== 1) monday += 1
  const monthNumber = String(monthIndex + 1).padStart(2, '0')
  const startDate = `${year}-${monthNumber}-${String(monday).padStart(2, '0')}`
  const endDate = `${year}-${monthNumber}-${String(monday + 1).padStart(2, '0')}`
  const month = `${year}-${monthNumber}`
  const ticketReason = `E2E Leave ticket ${year}-${monthNumber}-${monday}`
  const updatedReason = `${ticketReason} · đã sửa`
  let scheduledWorkdays = 0
  const daysInMonth = new Date(Date.UTC(year, monthIndex + 1, 0)).getUTCDate()
  for (let day = 1; day <= daysInMonth; day += 1) {
    const weekday = new Date(Date.UTC(year, monthIndex, day)).getUTCDay()
    if (weekday > 0 && weekday < 6) scheduledWorkdays += 1
  }

  await page.goto('/')
  await page.getByLabel('Tài khoản').fill('staff.demo')
  await page.getByLabel('Mật khẩu').fill(demoPassword)
  await page.getByRole('button', { name: 'Đăng nhập MRERP' }).click()
  await page.getByRole('button', { name: 'Nghỉ & Công', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Nghỉ & Công' })).toBeVisible()

  await page.getByLabel('Từ ngày').fill(startDate)
  await page.getByLabel('Đến ngày').fill(endDate)
  await page.getByLabel('Lý do nghỉ').fill(ticketReason)
  await page.getByRole('button', { name: 'Gửi đơn xin nghỉ' }).click()
  const ownTicket = page.locator('.leave-ticket').filter({ hasText: ticketReason })
  await expect(ownTicket).toBeVisible()
  await expect(ownTicket.getByText('Chờ duyệt', { exact: true })).toBeVisible()
  await ownTicket.getByRole('button', { name: 'Sửa đơn' }).click()
  await page.getByLabel('Lý do nghỉ').fill(updatedReason)
  await page.getByRole('button', { name: 'Lưu thay đổi' }).click()
  await expect(page.locator('.leave-ticket').filter({ hasText: updatedReason })).toBeVisible()

  await page.getByLabel('Xem theo vai trò debug').selectOption('leader.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Leader Alpha' })).toBeVisible()
  await page.getByRole('button', { name: 'Nghỉ & Công', exact: true }).click()
  await page.getByRole('button', { name: /Cần duyệt/ }).click()
  const reviewTicket = page.locator('.leave-ticket').filter({ hasText: updatedReason })
  await expect(reviewTicket).toBeVisible()
  await reviewTicket.getByRole('button', { name: 'Duyệt' }).click()
  await expect(page.locator('.leave-ticket').filter({ hasText: updatedReason })).toHaveCount(0)

  await page.getByLabel('Xem theo vai trò debug').selectOption('hr.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của HR Demo' })).toBeVisible()
  await page.getByRole('button', { name: 'Nghỉ & Công', exact: true }).click()
  await page.getByRole('button', { name: 'Bảng công' }).click()
  await page.getByLabel('Tháng bảng công').fill(month)
  const staffRow = page.locator('.attendance-row').filter({ hasText: 'STF01' })
  await expect(staffRow).toContainText('2')
  await expect(staffRow).toContainText(String(scheduledWorkdays - 2))
  await staffRow.getByRole('button', { name: 'Điều chỉnh' }).click()
  await page.getByLabel('Số ngày điều chỉnh').fill('-1')
  await page.getByLabel('Lý do điều chỉnh').fill('Hiệu chỉnh công E2E')
  await page.getByRole('button', { name: 'Lưu', exact: true }).click()
  await expect(staffRow).toContainText(String(scheduledWorkdays - 3))
})
