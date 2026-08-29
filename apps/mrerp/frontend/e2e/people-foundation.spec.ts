import { expect, test } from '@playwright/test'

test('HR tạo hồ sơ, Leader gán Team và chuyển lên Chính thức', async ({ page }) => {
  const demoPassword = process.env.E2E_DEMO_PASSWORD ?? 'Playwright-Only-1234!'
  const employeeCode = `E2E-${Date.now()}`

  await page.goto('/')
  await page.getByLabel('Tài khoản').fill('hr.demo')
  await page.getByLabel('Mật khẩu').fill(demoPassword)
  await page.getByRole('button', { name: 'Đăng nhập MRERP' }).click()
  await page.getByRole('button', { name: 'Nhân sự', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Nhân sự' })).toBeVisible()

  await page.getByRole('button', { name: /Thêm nhân sự/ }).click()
  await page.getByLabel('Mã nhân sự').fill(employeeCode)
  await page.getByRole('checkbox').uncheck()
  await page.getByRole('button', { name: 'Tạo Employee' }).click()

  const drawer = page.getByLabel('Hồ sơ nhân sự')
  await expect(drawer.getByText(employeeCode)).toBeVisible()
  await drawer.getByLabel('Họ và tên').fill('Nhân sự E2E')
  await drawer.getByLabel('Vị trí').fill('QA nội bộ')
  await drawer.getByRole('button', { name: 'Lưu hồ sơ chi tiết' }).click()
  await expect(drawer.getByRole('heading', { name: 'Nhân sự E2E' })).toBeVisible()
  await drawer.getByRole('button', { name: 'Đóng hồ sơ' }).click()

  await page.getByLabel('Xem theo vai trò debug').selectOption('leader.demo')
  await expect(page.getByRole('button', { name: 'Mở hồ sơ của Leader Alpha' })).toBeVisible()
  await page.getByRole('button', { name: 'Nhân sự', exact: true }).click()
  await page.getByLabel('Tìm nhân sự').fill(employeeCode)
  await page.getByRole('button', { name: new RegExp(employeeCode) }).click()

  await drawer.getByLabel('Team hiện tại').selectOption({ label: 'Alpha' })
  await drawer.getByRole('button', { name: 'Cập nhật Team' }).click()
  await expect(drawer.getByText('Alpha', { exact: true }).first()).toBeVisible()
  await drawer.getByLabel('Ghi chú xác nhận chính thức').fill('Đạt yêu cầu E2E')
  await drawer.getByRole('button', { name: /Chuyển lên Chính thức/ }).click()
  await expect(drawer.getByText('Chính thức', { exact: true })).toBeVisible()

  await page.reload()
  await page.getByRole('button', { name: 'Nhân sự', exact: true }).click()
  await page.getByLabel('Tìm nhân sự').fill(employeeCode)
  await page.getByRole('button', { name: new RegExp(employeeCode) }).click()
  await expect(drawer.getByText('Chính thức', { exact: true })).toBeVisible()
})
