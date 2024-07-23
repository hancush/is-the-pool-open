import unicodedata
from urllib.parse import urlencode

from dateutil.parser import parse as parse_date
import scrapy


BASE_URL = "https://www.chicagoparkdistrict.com"
FACILITIES_URL = f"{BASE_URL}/parks-facilities"


class ChiParksPoolSpider(scrapy.Spider):
    name = "chi_parks_pool_spider"
    allowed_domains = [BASE_URL]
    start_urls = [
        f"{FACILITIES_URL}/?{urlencode({'field_location_type_target_id[]': 148})}"
    ]

    def get_address(self, response):
        address_lines = response.xpath("//p[@class='address']/text()").getall()[:2]
        return ", ".join(line.strip() for line in address_lines)

    def get_phone_number(self, response):
        phone_number = response.xpath(
            "//div[contains(@class, 'phone')]/span[@class='location-header-value']/text()"
        ).get()

        if phone_number:
            return phone_number.replace("\n", "").replace("Office", "").strip()

    def get_alert(self, response):
        alert_elements = response.xpath(
            "//div[@role='alert']/descendant::*/text()"
        ).getall()

        if alert_elements:
            return ", ".join(
                unicodedata.normalize("NFKD", piece) for piece in alert_elements[2:]
            )

    def parse_pool(self, response):
        schedule = response.xpath(
            "//section[@id='block-views-block-loc-sect-seg-location-park-hours']//tr[contains(@class, 'office-hours__item')]/td"
        )

        schedule_obj = {}

        for idx, cell in enumerate(schedule):
            if cell.attrib["class"] == "office-hours__item-label":
                day = cell.xpath("text()").get().rstrip(": ")
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

        pool_location_xpath = "//span[@class='location-header-value' and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{pool_location}')]"

        yield {
            "name": response.xpath("//h1/text()").get(),
            "address": self.get_address(response),
            "phone_number": self.get_phone_number(response),
            "location": {
                "indoor": bool(
                    response.xpath(pool_location_xpath.format(pool_location="indoor"))
                ),
                "outdoor": bool(
                    response.xpath(pool_location_xpath.format(pool_location="outdoor"))
                ),
            },
            "schedule": schedule_obj,
            "schedule_pdf_urls": response.xpath(
                "//a[contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'schedule') and contains(@href, '.pdf')]/@href"
            ).getall(),
            "alert": self.get_alert(response),
            "lat": response.xpath("//meta[@property='latitude']/@content").get(),
            "lon": response.xpath("//meta[@property='longitude']/@content").get(),
            "url": response.url,
        }

    def parse(self, response):
        for pool_detail in response.xpath(
            "//article[@itemprop='location']//h3[@class='thumbnail-object-title']/a/@href"
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
