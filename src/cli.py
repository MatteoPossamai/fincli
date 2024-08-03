import sys

from src.functions import absent_command, invalid_command, help
from src.config import Config
from src.record_handler import RecordHandler

if __name__ == "__main__":
    args = sys.argv
    CONF = Config(args)
    RH = RecordHandler()

    if len(args) < 2:
        absent_command()
        sys.exit(1)
        
    match args[1]:
        case "add":
            print("Adding a transaction...")
            RH.add_record(CONF)
            print("Transaction added")
        case "list":
            RH.get(CONF)            
            print(f"Listing last {CONF.transaction_num} transactions")  
            for record in RH.list_records(CONF.transaction_num):
                print(record)
        case "report":
            print("Generating a report")
            RH.report(CONF)
        case "help":
            help()
            exit(0)
        case _:
            invalid_command(args[1])    
            sys.exit(1)