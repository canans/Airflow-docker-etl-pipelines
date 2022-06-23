

test=  [{'STX_ID': 2345706, 'STORE_NAME': None, 'PAID_PRICE': "nan", 'TRX_STATUS': 0, 'STORE_STATUS': "nan", 'STORE_LIVE_DATE': None, 'SALES_CREATE_DATE': None}]
for record in test:
    for key, value in record.items():
        # do something with value
        if value == "None" or value == "nan" or  value is None:
            record[key] = "NULL"

    print(test)