# Fincli

Simple Python CLI utility to automatize the query and creation of expenses and income record in local file for reference. An example of record that can handle is the following (expense):
```json
{
  "id": 2,
  "date": "2023-10-07",
  "category": "grocery",
  "to": "ALDI",
  "amount": 7.88,
  "currency": "EUR"
}
```
## Commands
- `list`: List of last n transaction. 10 by default, with flag `--transaction-num` can be customized
- `add`: adds an expense or an income, checking the type to understand the file to write into
- `report`: gives all the last year transactions, with balance and number of transaction. Date and currency can be customized
