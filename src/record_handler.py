import datetime
import dataclasses
from enum import Enum
from src.config import Config
import csv
from typing import List
from config import DATE_FORMAT
from base_converter import CONVERTER
from bisect import bisect_left, bisect_right

ACCEPTED_CURRENCIES = ["EUR", "GBP"]
ALLOWED_TRANSACTIONS = ["expense", "income"]


@dataclasses.dataclass
class Record:

    id: int
    date: datetime.datetime
    category: str
    type: str
    amount: float
    currency: str
    issuer: str = None
    __SPACES: int = 15
    __AMOUNT_SPACES: int = 15

    @property
    def header(self):
        basics = [
            "id",
            "date",
            "category",
            "issuer",
            "amount",
            "currency",
        ]
        return basics

    def to_list(self):
        basics = [
            self.id,
            self.date.strftime("%Y-%m-%d"),
            self.category,
            self.issuer,
            self.amount,
            self.currency,
        ]
        return basics

    def __str__(self) -> str:
        spaces = " " * (self.__SPACES - len(self.category))
        amount = str(self.amount) + " " * (self.__AMOUNT_SPACES - len(str(self.amount)))
        return f"{self.date.strftime("%Y-%m-%d")} | {self.category}{spaces} | {amount} {self.currency} | {self.issuer}"


class RecordHandler:

    def _convert(self, name, data):
        if name == "amount":
            return float(data)
        elif name == "id":
            return int(data)
        elif name == "date":
            return datetime.datetime.strptime(data, DATE_FORMAT)
        else:
            return data

    def _read_from_file(self, file_path: str, record_type: str) -> List[Record]:
        res = []
        with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)  # Skip the header
            for row in reader:
                kwargs = {}
                for i, head in enumerate(header):
                    kwargs[head] = self._convert(head, row[i])
                record: Record = Record(type=record_type, **kwargs)
                res.append(record)
        return res

    def _write_to_file(self, file_path: str, data: List[Record]):
        with open(file_path, "w+", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)

            header = [f for f in data[0].header]
            writer.writerow(header)

            for record in data:
                writer.writerow(record.to_list())

    def add_record(self, conf: Config) -> None:
        print("Do you want to insert a new income or expense?")
        type_ = input("Type (E or i): ")
        file = "expense" if type_ in ["E", "e", "expense"] or not type_ else "income"
        category = input("Category: ")
        amount = input("Amount: ")
        currency = input("Currency: ")

        issuer = input("Issuer: ")

        data = self._read_from_file(conf.source_path + file + "s.csv", file)
        new_record = Record(
            id=len(data),
            date=conf.default_end_date,
            category=category,
            amount=float(amount),
            currency=currency if currency in ACCEPTED_CURRENCIES else conf.currency,
            type="expense" if file == "expense" else "income",
            issuer=issuer,
        )

        data.append(new_record)
        self._write_to_file(conf.source_path + file + "s.csv", data)

    def _binary_search_dates(
        self, transactions: List[Record], start_date: datetime, end_date: datetime
    ) -> List[Record]:
        left = bisect_left(transactions, start_date, key=lambda x: x.date)
        right = bisect_right(transactions, end_date, key=lambda x: x.date)
        return transactions[left:right]

    def report(self, config: Config) -> None:
        if (
            config.report_transaction_type not in ALLOWED_TRANSACTIONS
            and config.report_transaction_type != "all"
        ):
            print("Invalid transaction type")
            return
        if config.report_transaction_type != "expense" and config.report_transaction_type != "all":
            expenses = []
        else:
            expenses = self._read_from_file(config.source_path + "expenses.csv", "income")
            for expense in expenses:
                expense.amount = -expense.amount
        if config.report_transaction_type != "income" and config.report_transaction_type != "all":
            incomes = []
        else:
            incomes = self._read_from_file(config.source_path + "incomes.csv", "income")

        expenses = self._binary_search_dates(
            expenses, config.default_start_date, config.default_end_date
        )
        incomes = self._binary_search_dates(
            incomes, config.default_start_date, config.default_end_date
        )

        transactions = expenses + incomes
        transactions.sort(key=lambda x: x.date)

        # Filter by category if specified
        if config.category:
            transactions = [t for t in transactions if t.category == config.category]

        # Get the total in the desired currency, while printing the transactions
        total = 0
        counter = 0
        for transaction in transactions:
            print(transaction)
            counter += 1
            delta = CONVERTER[f"{transaction.currency}/{config.currency}"] * transaction.amount
            total += delta

        print()
        start_date = config.default_start_date
        end_date = config.default_end_date
        formatted_balance = "{:,.2f}".format(total)
        print(f"In the period {start_date.strftime("%Y-%m-%d")} / {end_date.strftime("%Y-%m-%d")}")
        print(f"\tBalance: {formatted_balance} {config.currency}")
        print(f"\tNumber of transactions: {counter}")
