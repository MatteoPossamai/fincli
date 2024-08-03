import datetime

DATE_FORMAT = "%Y-%m-%d"


class Config:

    source_path: str = "/home/matteopossamai/Dropbox/personal_data/"
    files: dict[str, str] = {"expense": "expenses.json", "earnings": "earnings.json"}
    transaction_num: int = 10
    default_start_date: datetime.date = datetime.date.today() - datetime.timedelta(days=365)
    default_end_date: datetime.date = datetime.date.today()
    custom_date: datetime.datetime = datetime.date.today()
    currency: str = "GBP"
    add_attributes: list[str] = []
    category: str = ""
    report_transaction_type: str = "all"

    def __init__(self, args: list[str]) -> None:
        for i in range(2, len(args)):
            arg = args[i]
            if arg.startswith("--") and i + 1 >= len(args):
                print(f"Invalid format for argument {arg}")
                exit(1)
            elif arg.startswith("--") and i + 1 < len(args) and args[i + 1].startswith("--"):
                print(arg)
                print(args[i + 1])
                print(f"Cannot end with argument {args[i + 1]}")
                exit(1)
            elif arg == "--transaction-num":
                self.transaction_num = int(args[i + 1])
                i += 1
            elif arg == "--start-date":
                self.default_start_date = datetime.datetime.strptime(args[i + 1], DATE_FORMAT).date()
                i += 1
            elif arg == "--end-date":
                self.default_end_date = datetime.datetime.strptime(args[i + 1], DATE_FORMAT).date()
                i += 1
            elif arg == "--date":
                self.custom_date = datetime.datetime.strptime(args[i + 1], DATE_FORMAT).date()
                i += 1
            elif arg == "--currency":
                self.currency = args[i + 1]
                i += 1
            elif arg == "--category":
                self.category = args[i + 1]
                i += 1
            elif arg == "--tt":
                self.report_transaction_type = args[i + 1]
                i += 1
            elif arg == "--files":
                idx = i + 1
                while idx < len(args) - 1 and not args[idx + 1].startswith("-"):
                    try:
                        self.files[args[idx]] = args[idx + 1]
                        idx += 2
                    except:
                        print("Invalid number of arguments. Expected a pair of key-value")
                if len(self.files) == 0:
                    print("File not provided")
                    exit(1)
            elif arg == "--source-path":
                self.source_path = args[i + 1]
                i += 1
            else:
                self.add_attributes.append(arg)
