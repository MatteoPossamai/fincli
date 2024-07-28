def absent_command():
    print("No command given")
    print("Usage: fincli <command> [options]")

def invalid_command(command:str):
    print(f"Called unkonwn command: {command}")

def help():
    print("Usage: fincli <command> [options]")
    print("Options:")
    print("--transaction-num <num>: sets the number of transactions to show")
    print("--start-date <date>: sets the default start date for the report")
    print("--end-date <date>: sets the default end date for the report")
    print("--date <date>: sets a custom date for the report")
    print("--currency <currency>: sets the currency for the report")
    print("--source-path <path>: sets the source path for the data")
    print("--files <key> <value> ...: sets the files for the data")
    print("--help: shows this help message")
    exit(0)