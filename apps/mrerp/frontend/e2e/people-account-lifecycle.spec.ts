import { expect, test } from '@playwright/test'

test('HR cấp account và quản lý employment; CEO xem access bundle', async ({ page }) => {
  const demoPassword = process.env.E2E_DEMO_PASSWORD ?? 'Playwright-Only-1234!'
  const suffix = Date.now()
  const employeeCode = `ACC-${suffix}`
  const username = `account.${suffix}`

  await page.goto('/')
  await page.getByLabel('Tài khoản').fill('hr.demo')
  await page.getByLabel('Mật khẩu').fill(demoPassword)
  await page.getByRole('button', { name: 'Đăng nhập MRERP' }).click()

  await page.getByRole('button', { name: 'Hồ sơ của tôi', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Hồ sơ của tôi' })).toBeVisible()
  await expect(page.getByText('Tài khoản & bảo mật', { exact: false })).toBeVisible()

  await page.getByRole('button', { name: 'Nhân sự', exact: true }).click()
  await page.getByRole('button', { name: /Thêm nhân sự/ }).click()
  await page.getByLabel('Mã nhân sự').fill(employeeCode)
  await page.getByRole('checkbox').uncheck()
  await page.getByRole('button', { name: 'Tạo Employee' }).click()

  const drawer = page.getByLabel('Hồ sơ nhân sự')
  await drawer.getByLabel('Username cấp mới').fill(username)
  await drawer.getByRole('button', { name: 'Cấp account' }).click()
  await expect(drawer.getByText('Mật khẩu tạm — chỉ hiển thị lần này')).toBeVisible()

  await drawer.getByLabel('Ghi chú thay đổi employment').fill('Kiểm tra khóa account khi tạm nghỉ')
  await drawer.getByRole('button', { name: 'Tạm nghỉ' }).click()
  await expect(drawer.locator('.profile-meta').getByText('Tạm nghỉ', { exact: true })).toBeVisible()
  await drawer.getByLabel('Ghi chú thay đổi employment').fill('Kích hoạt lại sau kiểm tra')
  await drawer.getByRole('button', { name: 'Kích hoạt lại' }).click()
  await expect(drawer.locator('.profile-meta').getByText('Thử việc', { exact: true })).toBeVisible()
  await drawer.getByLabel('Ghi chú thay đổi employment').fill('Kết thúc hồ sơ kiểm thử')
  page.once('dialog', (dialog) => dialog.accept())
  await drawer.getByRole('button', { name: 'Cho nghỉ việc' }).click()
  await expect(drawer.locator('.profile-meta').getByText('Nghỉ việc', { exact: true })).toBeVisible()

  await drawer.getByRole('button', { name: 'Đóng hồ sơ' }).click()
  await page.getByLabel('Xem theo vai trò debug').selectOption('ceo.demo')
  await page.getByRole('button', { name: 'Admin Panel', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Admin Panel' })).toBeVisible()
  await expect(page.getByText(employeeCode, { exact: true }).last()).toBeVisible()
})
