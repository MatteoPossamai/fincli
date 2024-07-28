import datetime
import dataclasses
from enum import Enum
from src.config import Config
import json
from typing import Optional
from config import DATE_FORMAT
from base_converter import CONVERTER

ACCEPTED_CURRENCIES = ["EUR", "USD", "GBP"]
ALLOWED_TRANSACTIONS = ["expense", "income"]


class TransactionType(Enum):
    EXPENSE = "expense"
    INCOME = "income"


@dataclasses.dataclass
class Record:

    id: int
    date: datetime.datetime
    category: str
    type: TransactionType
    amount: float
    currency: str
    to: Optional[str] = None
    issuer: Optional[str] = None
    __SPACES: int = 15
    __AMOUNT_SPACES: int = 15

    def __str__(self) -> str:
        sign = "+" if self.type == TransactionType.INCOME else "-"
        spaces = " " * (self.__SPACES - len(self.category))
        amount = str(self.amount) +  " " * (self.__AMOUNT_SPACES - len(str(self.amount)))
        return f"{self.date} | {self.category}{spaces} | {sign} {amount} {self.currency} | {self.to if self.to else self.issuer}"


class RecordHandler:

    records: list[Record] = []

    def get(self, config: Config) -> None:

        self.records = []

        for local_file in config.files.values():
            with open(config.source_path + local_file, "r") as file:
                string_content = file.read()

            json_content = json.loads(string_content)
            for line in json_content["records"]:
                self.records.append(
                    Record(**line, type=TransactionType.EXPENSE if "to" in line else TransactionType.INCOME)
                )

        self.records.sort(key=lambda x: x.date)

    def list_records(self, num: int) -> list[Record]:
        return self.records[:num].copy()

    def add_record(self, conf: Config) -> None:
        file = conf.files[conf.add_attributes[0]]
        data = conf.add_attributes
        
        json_content = {}
        with open(conf.source_path + file, "r") as f:
            content = f.read()
            json_content = json.loads(content)

        with open(conf.source_path + file, "w") as f:
            new_record = {
                "id": len(json_content["records"]),
                "date": conf.custom_date.date().isoformat(),
                "category": data[1],
                "amount": float(data[3]),
                "currency": data[4] if len(data) > 4 and data[4] in ACCEPTED_CURRENCIES else conf.currency,
            }
            if data[0] == "expense":
                new_record["to"] = data[2]
            else:
                new_record["issuer"] = data[2]
            json_content["records"].append(new_record)
            json.dump(json_content, f, indent=4)

    def report(self, config: Config) -> None:
        if len(self.records) == 0:
            self.get(config)
            
        start_date = config.default_start_date
        end_date = config.default_end_date
        start, end = 0, len(self.records)
        
        # Binary search to find first record after start date
        while start <= end:
            mid = start + (end - start) // 2
            current_date = datetime.datetime.strptime(self.records[mid].date, DATE_FORMAT).date()
            if current_date < start_date:
                start = mid + 1
            else:
                end = mid - 1
        record_start = mid        
        
        start, end = 0, len(self.records)
        # Binary search to find last record before end date
        while start < end:
            mid = start + (end - start) // 2
            if datetime.datetime.strptime(self.records[mid].date, DATE_FORMAT).date() <= end_date:
                start = mid + 1
            else:
                end = mid - 1
        record_end = mid
        
        # Print all the records
        balance = 0
        for record in self.records[record_start:record_end]:
            print(record)
            if config.currency != record.currency:
                current_amount = CONVERTER[f"{record.currency}/{config.currency}"] * record.amount
            else:
                current_amount = record.amount

            balance += current_amount if record.type == TransactionType.INCOME else -current_amount
            
        print()
        formatted_balance = "{:,.2f}".format(balance) 
        print(f"In the period {start_date} - {end_date}")
        print(f"\tBalance: {formatted_balance} {config.currency}")
        print(f"\tNumber of transactions: {record_end - record_start}")