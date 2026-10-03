import {test,expect} from '@playwright/test'
import type {BrowserContext} from '@playwright/test'

async function identity(context:BrowserContext,authenticated=true,assetcontrol=false){
 const session={authenticated:true,username:'crm.fixture',display_name:'Leader minh họa',employee_code:'DEMO-LDR',capabilities:[],product_entitlements:assetcontrol?['assetcontrol']:[]}
 await context.route('**/api/**',async route=>{
  const path=new URL(route.request().url()).pathname
  if(path.endsWith('/auth/session/'))return route.fulfill({json:authenticated?session:{authenticated:false}})
  if(path.endsWith('/auth/login/')){authenticated=true;return route.fulfill({json:session})}
  if(path.endsWith('/auth/logout/')){authenticated=false;return route.fulfill({status:204})}
  return route.fulfill({status:403,json:{detail:'Not provided by this UI fixture'}})
 })
}
test('ERP shortcut opens independent CRM, preserving entitlement and route history',async({page,context})=>{
 await identity(context,true,true);await page.goto('/')
 await expect(page.getByRole('link',{name:'Mở ASSETCONTROL trong tab mới'})).toBeVisible()
 const popup=context.waitForEvent('page');await page.getByRole('link',{name:'MRECRM',exact:true}).first().click();const crm=await popup
 await expect(crm).toHaveURL(/\/crm\/orders$/);await expect(page).not.toHaveURL(/\/crm/)
 expect(await crm.evaluate(()=>window.opener===null)).toBe(true)
 await expect(crm.locator('.product-switcher')).toHaveCount(0);await expect(crm.locator('.crm-app .sidebar')).toContainText('Quản lý đơn hàng');await expect(crm.locator('.ledger-summary')).toContainText('60 đơn')
 await crm.getByRole('link',{name:'Thống kê',exact:true}).click();await expect(crm.locator('.metric').first()).toContainText('60');await expect(crm.locator('.metric').nth(7)).toContainText('72')
 await crm.reload();await expect(crm.getByRole('heading',{name:'Thống kê',exact:true})).toBeVisible();await crm.goBack();await expect(crm).toHaveURL(/\/crm\/orders$/);await crm.goForward();await expect(crm).toHaveURL(/\/crm\/reports$/)
 await crm.getByRole('link',{name:'Về MRERP'}).click();await expect(crm.locator('.product-switcher')).toBeVisible()
})
test('direct CRM requires login, retains requested route, theme and logout',async({page,context})=>{
 await identity(context,false);await page.goto('/crm/reports');await expect(page.getByRole('button',{name:'Đăng nhập MRERP'})).toBeVisible();await expect(page.locator('.crm-app')).toHaveCount(0)
 await page.getByLabel('Mật khẩu',{exact:true}).fill('fixture-only');await page.getByRole('button',{name:'Đăng nhập MRERP'}).click();await expect(page).toHaveURL(/\/crm\/reports$/)
 await page.getByRole('button',{name:'Cài đặt',exact:true}).click();await page.locator('.theme-toggle').click();await expect(page.locator('html')).toHaveAttribute('data-theme','dark');await page.locator('.theme-toggle').click();await page.getByRole('button',{name:'Đăng xuất',exact:false}).click();await expect(page.locator('.crm-app')).toHaveCount(0);await expect(page.getByRole('button',{name:'Đăng nhập MRERP'})).toBeVisible()
})
test('orders and reports share filters; detail and mobile keyboard work',async({page,context})=>{
 await identity(context);await page.goto('/crm/orders');await page.getByRole('button',{name:'Xem chi tiết DEMO-0001'}).click();await expect(page.locator('.detail')).toContainText('Bản ghi nguồn (2)');await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'Xem chi tiết DEMO-0001'})).toBeFocused()
 await page.getByLabel('Tìm đơn',{exact:true}).fill('nonexistent');await expect(page.locator('.empty')).toBeVisible();await page.getByRole('button',{name:'Đặt lại bộ lọc'}).click();await page.getByLabel('Nguồn dữ liệu',{exact:true}).selectOption('POS');await expect(page.locator('.ledger-summary')).toContainText('24 đơn');await page.getByRole('link',{name:'Thống kê',exact:true}).click();await expect(page.locator('.metric').first()).toContainText('24');await expect(page.locator('.metric').nth(1)).toContainText('13.596.000')
 await page.getByLabel('Từ ngày',{exact:true}).fill('2026-11-01');await expect(page.locator('.metric').nth(3)).toContainText('—');await expect(page.locator('.metric').nth(4)).toContainText('—');await page.getByRole('button',{name:'Đặt lại',exact:true}).click()
 for(const [slug,title] of [['ads','Chi phí & hiệu quả quảng cáo'],['accounting','Kế toán'],['review','Nội dung cần duyệt']]){await page.goto(`/crm/${slug}`);await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible()}
 await page.goto('/crm/unknown');await expect(page.getByRole('heading',{name:'Không tìm thấy trang CRM'})).toBeVisible()
 await page.goto('/crm/orders');await page.setViewportSize({width:390,height:844});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.getByRole('button',{name:'Xem chi tiết DEMO-0001'}).click();await page.keyboard.press('Tab');await expect(page.getByRole('button',{name:'Đóng chi tiết đơn'})).toBeFocused();await page.keyboard.press('Escape');await expect(page.locator('.detail')).toHaveCount(0)
})
