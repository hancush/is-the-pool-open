from dateutil.parser import parse as parse_date

import scrapy

BASE_URL = "www.chicagoparkdistrict.com"


class ChiParksPoolSpider(scrapy.Spider):
    name = "chi_parks_pool_spider"
    allowed_domains = [BASE_URL]
    start_urls = [f"https://{BASE_URL}/facilities/swimming-pools"]
    def get_address(self, response):
        address_lines = response.xpath("//p[@class='address']/span/text()").getall()[:2]
        return ", ".join(line.strip() for line in address_lines)

    def get_phone_number(self, response):
        phone_number = response.xpath(
            "//div[contains(@class, 'paragraph--type--phone-number')]/text()"
        ).get()

        if phone_number:
            return (
                phone_number.replace("\n", "")
                .replace("Tel: ", "")
                .replace("|", "")
                .strip()
            )

    def get_alert(self, response):
        return

    def parse_pool(self, response):

        schedule_pdf_urls = response.xpath(
            "//a[contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'schedule') and contains(@href, '.pdf')]/@href"
        ).getall()

        schedule_obj = {}

        if schedule_pdf_urls:
            schedule = response.xpath(
                "//div[contains(@class, 'office-hours')]//div[contains(@class, 'office-hours__item')]/span"
            )

            for idx, cell in enumerate(schedule):
                if cell.attrib.get("class") == "office-hours__item-label":
                    day = cell.xpath("text()").get().rstrip(": ")
                    
                    # Skip general hours
                    if day == " |":
                        continue

                    hours = schedule[idx + 1].xpath("text()").get()

                    try:
                        open, close = hours.split("-")
                    except (ValueError, AttributeError):
                        schedule_obj[day] = {}
                    else:
                        schedule_obj[day] = {
                            "open": parse_date(open).time(),
                            "close": parse_date(close).time(),
                        }
                        
        additional_details = "".join(
            response.xpath(
                "//div[@class='facility-extra-details']/div[contains(@class, 'field--label-above')]/text()"
            ).getall()
        ).lower()

        yield {
            "name": response.xpath(
                "//span[contains(@class, 'field--name-title')]/text()"
            ).get(),
            "address": self.get_address(response),
            "phone_number": self.get_phone_number(response),
            "location": {
                "indoor": "indoor" in additional_details,
                "outdoor": "outdoor" in additional_details,
            },
            "schedule": schedule_obj,
            "schedule_pdf_urls": schedule_pdf_urls,
            "alert": self.get_alert(response),
            "lat": response.xpath("//meta[@property='latitude']/@content").get(),
            "lon": response.xpath("//meta[@property='longitude']/@content").get(),
            "url": response.url,
        }

    def parse(self, response):

        for pool_detail in response.xpath(
            "//h3[contains(@class, 'facility--title')]/a/@href"
        ).getall():
            yield scrapy.Request(
                response.urljoin(pool_detail),
                callback=self.parse_pool,
                dont_filter=True,
            )

        next_page = response.xpath(
            "//li[contains(@class, 'pager__item--next')]/a/@href"
        ).get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)
