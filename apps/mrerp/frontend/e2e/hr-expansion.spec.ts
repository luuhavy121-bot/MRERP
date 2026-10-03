import { expect, test } from "@playwright/test";
import fs from "node:fs";
const password = process.env.E2E_DEMO_PASSWORD ?? "Playwright-Only-1234!";
async function login(page: import("@playwright/test").Page, name: string) {
  await page.goto("/");
  await page.getByLabel("Tài khoản", { exact: true }).fill(name);
  await page.getByLabel("Mật khẩu", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Đăng nhập MRERP" }).click();
  await expect(page.getByLabel("Xem theo vai trò debug")).toBeVisible();
}
async function persona(page: import("@playwright/test").Page, name: string) {
  await page.getByLabel("Xem theo vai trò debug").selectOption(name);
  await expect(page.getByLabel("Xem theo vai trò debug")).toHaveValue(name);
}
const screenshots = "../../../.impeccable/review";
test("Leader gửi tuyển → HR duyệt → ứng viên public → pipeline Team", async ({
  page,
  browser,
}) => {
  const title = `Public QA ${Date.now()}`;
  await login(page, "leader.demo");
  await page.getByRole("button", { name: "Tuyển dụng", exact: true }).click();
  await page.getByRole("tab", { name: /Yêu cầu tuyển/ }).click();
  await page
    .getByRole("button", { name: "Tạo yêu cầu tuyển", exact: true })
    .click();
  await page.getByLabel("Vị trí", { exact: true }).fill(title);
  await page.getByLabel("Lý do nội bộ").fill("Lý do nội bộ bí mật");
  await page.getByLabel("Kế hoạch sử dụng nhân sự (nội bộ)", {exact:true}).fill("Phụ trách kiểm thử nội bộ cho Team Alpha.");
  await page.getByLabel("Địa điểm").fill("Hà Nội");
  await page.getByLabel("Hình thức làm việc").fill("Toàn thời gian");
  await page
    .getByLabel("Mô tả công việc")
    .fill("Kiểm thử sản phẩm và phối hợp với đội phát triển.");
  await page
    .getByLabel("Yêu cầu ứng viên")
    .fill("Có kinh nghiệm kiểm thử ứng dụng web.");
  await page.getByLabel("Quyền lợi").fill("Trao đổi trong buổi phỏng vấn.");
  await page.getByLabel("Hạn nhận hồ sơ").fill("2030-12-31");
  await page.getByRole('button', {name:'Xem trước tin tuyển'}).click();
  await expect(page.getByRole('region', {name:'Xem trước tin tuyển'})).toBeVisible();
  await expect(page.locator('.hiring-preview')).toContainText(title);
  await expect(page.locator('.hiring-preview')).not.toContainText('Lý do nội bộ bí mật');
  await expect(page.locator('.hiring-preview')).not.toContainText('Phụ trách kiểm thử nội bộ');
  await page.getByRole("button", { name: "Gửi duyệt", exact: true }).click();
  await expect(
    page.locator(".recruitment-request-row").filter({ hasText: title }),
  ).toContainText("Chờ duyệt");
  await persona(page, "hr.demo");
  await page.getByRole("button", { name: "Tuyển dụng", exact: true }).click();
  await page.getByRole("tab", { name: /Yêu cầu tuyển/ }).click();
  await page
    .locator(".recruitment-request-row")
    .filter({ hasText: title })
    .getByRole("button", { name: "Duyệt", exact: true })
    .click();
  await page.getByRole("tab", { name: "Tin đang tuyển" }).click();
  const href = await page
    .locator(".recruitment-request-row")
    .filter({ hasText: title })
    .getByRole("link", { name: "Xem tin công khai" })
    .getAttribute("href");
  const context = await browser.newContext({
    baseURL: test.info().project.use.baseURL,
    viewport: { width: 1440, height: 1000 },
  });
  const publicPage = await context.newPage();
  await publicPage.goto(href!);
  await expect(publicPage.getByRole("heading", { name: title })).toBeVisible();
  await expect(publicPage.getByText("Lý do nội bộ bí mật")).toHaveCount(0);
  await expect(publicPage.getByText("Phụ trách kiểm thử nội bộ cho Team Alpha.")).toHaveCount(0);
  fs.mkdirSync(screenshots, { recursive: true });
  await publicPage.screenshot({
    path: `${screenshots}/careers-desktop.png`,
    fullPage: true,
  });
  await publicPage.setViewportSize({ width: 390, height: 844 });
  await publicPage.screenshot({
    path: `${screenshots}/careers-mobile.png`,
    fullPage: true,
  });
  await publicPage
    .getByLabel("Họ tên", { exact: true })
    .fill("Ứng viên public E2E");
  await publicPage
    .getByLabel("Email", { exact: true })
    .fill("e2e@example.test");
  await publicPage
    .getByLabel(/CV \(PDF/)
    .setInputFiles({
      name: "cv.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.4 synthetic CV"),
    });
  await publicPage.getByRole("checkbox").check();
  await publicPage
    .getByRole("button", { name: "Gửi hồ sơ", exact: true })
    .click();
  await expect(
    publicPage.getByRole("heading", { name: "Đã nhận hồ sơ" }),
  ).toBeVisible();
  await context.close();
  await persona(page, "leader.demo");
  await page.getByRole("button", { name: "Tuyển dụng", exact: true }).click();
  await page.locator(".candidate-card").filter({ hasText: title }).click();
  await expect(
    page.getByText("e2e@example.test", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sàng lọc", exact: true }).click();
  await expect(page.locator(".candidate-inspector")).toContainText("Sàng lọc");
  await page.getByRole("button", {name:"Phỏng vấn", exact:true}).click();
  await expect(page.locator(".candidate-inspector")).toContainText("Phỏng vấn");
  await expect(page.getByRole("button", {name:"Đề nghị", exact:true})).toHaveCount(0);
  await page.getByRole("button", {name:"Đã tuyển", exact:true}).click();
  await expect(page.locator(".candidate-inspector")).toContainText("Đã tuyển");
});
test("KPI tháng → chốt → nhân sự xác nhận → HR mở lại", async ({ page }) => {
  await login(page, "leader.demo");
  await page
    .getByRole("button", { name: "Đánh giá nhân sự", exact: true })
    .click();
  const month = `${2100 + (Math.floor(Date.now() / 1000) % 7000)}-10`;
  await page.getByLabel("Tháng đánh giá").fill(month);
  await page.getByRole("button", { name: /Staff Alpha.*Chưa đánh giá/ }).click();
  await expect(page.getByLabel("Tên KPI 1", { exact: true })).toBeVisible();
  fs.mkdirSync(screenshots, { recursive: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${screenshots}/performance-entry-desktop.png`, fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${screenshots}/performance-entry-mobile.png`, fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page
    .getByLabel("Tên KPI 1", { exact: true })
    .fill("Chất lượng nội dung");
  await page.getByLabel("Hoàn thành KPI 1", { exact: true }).fill("85");
  await page
    .getByLabel("Nhận xét tổng kết", { exact: true })
    .fill("Đáp ứng mục tiêu tháng.");
  await page
    .getByRole("button", { name: "Chốt đánh giá", exact: true })
    .click();
  await expect(
    page.locator(".review-row").filter({ hasText: "Staff Alpha" }),
  ).toContainText("85.00/100");
  fs.mkdirSync(screenshots, { recursive: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: `${screenshots}/performance-desktop.png`,
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: `${screenshots}/performance-mobile.png`,
    fullPage: true,
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await persona(page, "staff.demo");
  await page
    .getByRole("button", { name: "Đánh giá nhân sự", exact: true })
    .click();
  await page.getByLabel("Tháng đánh giá").fill(month);
  await page.locator(".review-row").filter({ hasText: "Staff Alpha" }).click();
  await page.getByLabel("Phản hồi của tôi").fill("Đã đọc và ghi nhận.");
  await page.getByRole("button", { name: "Xác nhận đã đọc" }).click();
  await expect(page.locator(".review-row")).toContainText("Đã xác nhận");
  await persona(page, "hr.demo");
  await page
    .getByRole("button", { name: "Đánh giá nhân sự", exact: true })
    .click();
  await page.getByLabel("Tháng đánh giá").fill(month);
  await page.locator(".review-row").filter({ hasText: "Staff Alpha" }).click();
  await page.getByLabel("Lý do mở lại").fill("Rà soát lại mức hoàn thành");
  await page.getByRole("button", { name: "Mở lại phiếu" }).click();
  await expect(page.locator(".review-row")).toContainText("Bản nháp");
  await page.getByText(/Lịch sử chốt và mở lại/).click();
  await expect(page.locator(".review-revision").last()).toContainText(
    "Đã đọc và ghi nhận.",
  );
});
