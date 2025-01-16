import csv

from api.models import TriangleData
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date


class Command(BaseCommand):
    help = "Load CSV data into TriangleData table"

    def add_arguments(self, parser):
        parser.add_argument("csv_filepath", type=str, help="The path to the CSV file.")

    def handle(self, *args, **kwargs):
        csv_filepath = kwargs["csv_filepath"]

        try:
            with open(csv_filepath, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    period_start = parse_date(row["period_start"])
                    period_end = parse_date(row["period_end"])
                    evaluation_date = parse_date(row["evaluation_date"])

                    data = TriangleData(
                        period_start=period_start,
                        period_end=period_end,
                        evaluation_date=evaluation_date,
                        earned_premium=row["earned_premium"],
                        reported_loss=row["reported_loss"],
                        paid_loss=row["paid_loss"],
                        program=row["program"],
                        dev_lag=int(row["dev_lag"]),
                    )
                    data.save()
        except FileNotFoundError:
            raise CommandError(f"File '{csv_filepath}' does not exist")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")

        self.stdout.write(self.style.SUCCESS("CSV file loaded successfully."))
