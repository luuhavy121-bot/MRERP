import { expect, test } from '@playwright/test'

function localInput(value: Date) {
  return new Date(value.getTime() - value.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}

test('Leader tạo Goal và recurring Task, Staff submit, Leader accept', async ({ page }) => {
  const password = process.env.E2E_DEMO_PASSWORD ?? 'Playwright-Only-1234!'
  const marker = `${Date.now()}`
  const goalTitle = `Goal E2E ${marker}`
  const taskTitle = `Recurring E2E ${marker}`
  const today = new Date()
  const end = new Date(today.getTime() + 7 * 86400000)
  await page.goto('/')
  await page.getByLabel('Tài khoản').fill('leader.demo')
  await page.getByLabel('Mật khẩu').fill(password)
  await page.getByRole('button', { name: 'Đăng nhập MRERP' }).click()
  await page.getByRole('button', { name: 'Công việc', exact: true }).click()

  await page.locator('.work-overview__actions').getByRole('button', { name: 'Mục tiêu' }).click()
  const goalPanel = page.locator('.creation-panel')
  await goalPanel.getByLabel('Tiêu đề').fill(goalTitle)
  await goalPanel.getByRole('combobox', { name: 'Team', exact: true }).selectOption({ label: 'Alpha' })
  await goalPanel.getByLabel('Bắt đầu').fill(today.toISOString().slice(0, 10))
  await goalPanel.getByLabel('Kết thúc').fill(end.toISOString().slice(0, 10))
  await goalPanel.getByRole('button', { name: 'Thiết lập mục tiêu' }).click()
  await expect(goalPanel).toHaveCount(0)

  await page.locator('.work-overview__actions').getByRole('button', { name: 'Lịch lặp' }).click()
  const recurrencePanel = page.locator('.creation-panel')
  await recurrencePanel.getByLabel('Tiêu đề').fill(taskTitle)
  await recurrencePanel.getByRole('combobox', { name: 'Người thực hiện' }).selectOption({ label: 'Staff Alpha · Alpha' })
  await recurrencePanel.getByLabel('Kỳ đầu tiên').fill(localInput(new Date(Date.now() - 60000)))
  await recurrencePanel.getByLabel('Mục tiêu liên kết').selectOption({ label: goalTitle })
  await recurrencePanel.getByLabel('Ngày dừng').fill(end.toISOString().slice(0, 10))
  await recurrencePanel.getByRole('button', { name: 'Tạo lịch lặp' }).click()

  const leaderTask = page.locator('.work-task').filter({ hasText: taskTitle })
  await expect(leaderTask).toBeVisible()
  await leaderTask.locator('input[type=file]').first().setInputFiles({ name: 'brief.txt', mimeType: 'text/plain', buffer: Buffer.from('Brief E2E') })
  await expect(leaderTask.getByText('brief.txt', { exact: true })).toBeVisible()

  await page.getByLabel('Xem theo vai trò debug').selectOption('staff.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Staff Alpha' })).toBeVisible()
  await page.getByRole('button', { name: 'Công việc', exact: true }).click()
  const staffTask = page.locator('.work-task').filter({ hasText: taskTitle })
  await expect(staffTask).toBeVisible()
  await staffTask.getByRole('slider').fill('100')
  await staffTask.getByRole('button', { name: 'Lưu tiến độ' }).click()
  await staffTask.locator('input[type=file]').last().setInputFiles({ name: 'result.txt', mimeType: 'text/plain', buffer: Buffer.from('Result E2E') })
  await expect(staffTask.getByText('result.txt', { exact: true })).toBeVisible()
  await staffTask.getByRole('button', { name: 'Gửi xác nhận' }).click()

  await page.getByLabel('Xem theo vai trò debug').selectOption('leader.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Leader Alpha' })).toBeVisible()
  await page.getByRole('button', { name: 'Công việc', exact: true }).click()
  const reviewTask = page.locator('.work-task').filter({ hasText: taskTitle })
  await expect(reviewTask.getByText('Chờ xác nhận')).toBeVisible()
  await reviewTask.getByRole('button', { name: 'Xác nhận hoàn thành' }).click()
  await expect(reviewTask.getByText('Đã hoàn thành', { exact: true })).toBeVisible()
  await page.locator('.work-tabs').getByRole('button', { name: 'Mục tiêu', exact: true }).click()
  await expect(page.locator('.goal-card').filter({ hasText: goalTitle }).first()).toContainText('100%')
})
