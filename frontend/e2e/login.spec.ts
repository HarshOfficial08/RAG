import { expect, test, type Page } from "@playwright/test";

const CREDENTIALS = { email: "alice@acme.example", password: "acme-demo-pass" };

async function login(page: Page): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("Email").fill(CREDENTIALS.email);
  await page.getByLabel("Password").fill(CREDENTIALS.password);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/documents/);
}

test("login redirects to the tenant-scoped document library", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });

  await login(page);
  await expect(page.getByText("Acme Corp")).toBeVisible();
  await page.screenshot({ path: "e2e/screenshots/documents-desktop.png" });

  expect(consoleErrors).toEqual([]);
});

test("renders correctly at mobile width (375px)", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await login(page);
  await expect(page.getByText("Acme Corp")).toBeVisible();
  await page.screenshot({ path: "e2e/screenshots/documents-mobile.png" });
});
