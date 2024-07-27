from collections import UserDict
import io
import json
import logging
import re
import sys

from dateutil import parser as date_parser
import pdfplumber
import requests


logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)


class SchedulePdf(object):
    def __init__(self, pdf_location):
        self.pdf_location = pdf_location

        logger.info(pdf_location)
        response = requests.get(pdf_location, stream=True)

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            self.schedule_page = pdf.pages[0]

    def deserialize(self):
        start_date, end_date = self.schedule_interval
        return {
            "url": self.pdf_location,
            "start_date": start_date,
            "end_date": end_date,
            "schedule": self.schedule,
        }

    def parse_date(self, date_str):
        try:
            return date_parser.parse(date_str).isoformat()
        except:
            return date_str

    def parse_schedule_blocks(self, time_column):
        processed_blocks = []
        skip_indices = []

        for idx, value in enumerate(time_column):
            if idx in skip_indices:
                logger.info(f"Skipping {value}")
                continue

            if idx == (len(time_column) - 1):
                logger.info(f"{value} is final value")
                processed_blocks.append(value)

            elif value.endswith("-") or value.endswith("–"):
                logger.info(
                    f"{value} ends with dash, combining with next value {time_column[idx+1]}"
                )
                processed_blocks.append(f"{value}{time_column[idx+1]}")
                skip_indices.append(idx + 1)

            elif not re.search(r"[-–]", value):
                logger.info(
                    f"{value} does not contain dash, combining with next value {time_column[idx+1]}"
                )
                processed_blocks.append(f"{value}{time_column[idx+1]}")
                skip_indices.append(idx + 1)

            else:
                logger.info(f"{value} is fine as is")
                processed_blocks.append(value)

        return processed_blocks

    @property
    def schedule_table(self):
        if not hasattr(self, "_schedule_table"):
            self._schedule_table = self.schedule_page.extract_table()
        return self._schedule_table

    @property
    def schedule_interval(self):
        if not hasattr(self, "_schedule_interval"):
            schedule_interval = (
                self.schedule_page.extract_text().splitlines()[0].split("|")[-1]
            )

            try:
                start_date, end_date = re.split(r"[-–]", schedule_interval)

            except ValueError:
                logger.info(f"Could not parse {schedule_interval}")
                self._schedule_interval = (None, None)

            else:
                self._schedule_interval = (
                    self.parse_date(start_date),
                    self.parse_date(end_date),
                )

        return self._schedule_interval

    @property
    def schedule(self):
        if not hasattr(self, "_schedule"):
            schedule = {}
            schedule_blocks = []

            for column in (
                [el for el in col if el is not None]
                for col in zip(*self.schedule_table)
            ):
                try:
                    header, *values = column

                except ValueError:
                    logger.info(f"Not enough values in: {column}")
                    continue

                if any(v.lower() == "time" for v in values):
                    values = [v for v in values if v and v.lower() != "time"]

                    if not values:
                        logger.info(f"No values in time column")
                        continue

                    schedule_blocks = self.parse_schedule_blocks(values)

                elif header:
                    schedule[header] = {
                        block: value.replace("\n", " ")
                        for block, value in zip(schedule_blocks, values)
                        if value
                    }

            self._schedule = schedule

        return self._schedule


if __name__ == "__main__":
    _, pool_data = sys.argv

    schedules = []

    with open(pool_data, "r") as f:
        pools = json.load(f)

        for pool in pools:
            schedules.append(
                {
                    "name": pool["name"],
                    "pdf_schedules": {
                        schedule_url: SchedulePdf(schedule_url).deserialize()
                        for schedule_url in pool["schedule_pdf_urls"]
                    },
                }
            )

    sys.stdout.write(json.dumps(schedules, indent=4))
