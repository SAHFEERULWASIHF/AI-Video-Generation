from playwright.async_api import async_playwright
import os
import asyncio

class InstagramPublisher:
    def __init__(self, username, password, storage_base):
        self.username = username
        self.password = password
        self.storage_base = storage_base

    async def publish_reel(self, video_path: str, caption: str):
        async with async_playwright() as p:
            user_data_dir = os.path.join(self.storage_base, "profiles", "instagram_main")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await browser.new_page()

            try:
                await page.goto("https://www.instagram.com/", wait_until="networkidle")

                # Login if necessary
                if await page.query_selector('input[name="username"]'):
                    await page.fill('input[name="username"]', self.username)
                    await page.fill('input[name="password"]', self.password)
                    await page.click('button[type="submit"]')
                    await page.wait_for_navigation()

                # Create Post
                await page.click('svg[aria-label="New post"]')
                await page.click('span:has-text("Post")')

                # File Upload
                async with page.expect_file_chooser() as fc_info:
                    await page.click('button:has-text("Select from computer")')
                file_chooser = await fc_info.value
                await file_chooser.set_files(video_path)

                # Step through Instagram wizard
                await page.click('div:has-text("Next")')
                await page.click('div:has-text("Next")') # To caption screen

                # Set Caption
                await page.fill('div[aria-label="Write a caption..."]', caption)

                # Share
                await page.click('div:has-text("Share")')
                await page.wait_for_selector('text="Reel shared"')

                return True
            except Exception as e:
                print(f"Instagram publish error: {e}")
                return False
            finally:
                await browser.close()
