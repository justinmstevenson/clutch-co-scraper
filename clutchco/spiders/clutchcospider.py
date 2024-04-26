import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from ..items import BusinessItem
from itemloaders.processors import TakeFirst
from scrapy_playwright.page import PageMethod

class ClutchCoSpider(scrapy.Spider):
    name = 'clutch_co_spider'
    allowed_domains = ['clutch.co']

    custom_settings = {
        # Your custom settings
    }

    def start_requests(self):
        yield scrapy.Request(
            "https://clutch.co/sitemap",
            meta={
                'playwright': True,
                'playwright_include_page': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', '.sitemap-button.collapsed')
                ]
            }
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.screenshot(path=f'link_screenshot_{href}.png')
        buttons = await page.query_selector_all('.sitemap-button.collapsed')
        for button in buttons:
            print("-----Clicking button")
            await button.click()
            await page.wait_for_timeout(300)  # Wait for 0.3 seconds

        # Take a screenshot after clicking the buttons
        await page.screenshot(path='button_click_screenshot.png')

        sitemap_links = await page.query_selector_all('div > div.sitemap-data__wrap > a')
        hrefs = [await link.get_attribute('href') for link in sitemap_links]
        for href in hrefs:
            print(f"------Navigating to {href}")
            yield scrapy.Request(url=href, callback=self.parse_business)

            # Take a screenshot after navigating to each link
            await page.screenshot(path=f'link_screenshot_{href}.png')

    async def parse_business(self, response):
        # Extract business listings
        business_listings = response.css('li.provider-row')
        for listing in business_listings:
            loader = ItemLoader(item=BusinessItem(), selector=listing)
            loader.default_output_processor = TakeFirst()
            loader.add_css('id', '::attr(id)')
            loader.add_css('data_type', '::attr(data-type)')
            loader.add_css('data_title', '::attr(data-title)')
            loader.add_css('data_is_paid', '::attr(data-is-paid)')
            loader.add_css('profile_link', 'a[href*="/profile"]::attr(href)')
            loader.add_css('rating', 'span.rating.sg-rating__number::text')
            loader.add_css('reviews', 'a.reviews-link.sg-rating__reviews::text')
            loader.add_css('min_project_size', 'div[data-content*="Min. project size"] span::text')
            loader.add_css('avg_hourly_rate', 'div[data-content*="Avg. hourly rate"] span::text')
            loader.add_css('employees', 'div[data-content*="Employees"] span::text')
            loader.add_css('location', 'div[data-content*="Location"] .locality::text')
            loader.add_css('service_focus', 'div.chartAreaContainer.spm-bar-chart div.grid::text')
            loader.add_css('summary', 'div.provider-info__description blockquote::text')
            loader.add_css('website', 'div.provider-detail.col-md-2 a::attr(href)')
            yield loader.load_item()

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(ClutchCoSpider)
    process.start()