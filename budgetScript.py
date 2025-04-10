import pandas as pd
import os

downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
bankDF = pd.read_csv(os.path.join(downloads_path, 'bank.csv'), skiprows=3)
bankDF = bankDF[['Date', 'Description', 'Memo', 'Amount Debit', 'Amount Credit']]

bankDebits = bankDF.dropna(subset=['Amount Debit'], how='all')[['Date', 'Description',  'Amount Debit', 'Memo']]
bankDebits['Amount Debit'] = bankDebits['Amount Debit'] * -1
bankDebits['Description'] = bankDebits['Description'].str.replace('POS ', '', regex=False)
bankDebits.drop(bankDebits[bankDebits['Description'].str.contains('VENMO', na=False)].index, inplace=True)
bankDebits.rename(columns={'Amount Debit': 'Amount', 'Description': 'Company', 'Memo': 'Notes'}, inplace=True)

bankCredits = bankDF.dropna(subset=['Amount Credit'], how='all')[['Date', 'Description', 'Amount Credit', 'Memo']]
bankCredits.rename(columns={'Amount Credit': 'Amount', 'Description': 'Company', 'Memo': 'Notes'}, inplace=True)
bankCredits['Date'] = pd.to_datetime(bankCredits['Date']).dt.date
bankCredits.sort_values(by='Date', ascending=True, inplace=True)

venmoDF = pd.read_csv(os.path.join(downloads_path, 'venmo.csv'), skiprows=2)
venmoDF.drop([0, len(venmoDF)-1], axis=0, inplace=True)
venmoDF = venmoDF[['Datetime', 'Note', 'To', 'Amount (total)', 'Funding Source', 'Destination']]
venmoPayments = venmoDF.dropna(subset=['Funding Source'], how='all')[['Datetime', 'Note', 'To', 'Amount (total)']]
venmoPayments['Amount (total)'] = venmoPayments['Amount (total)'].str.replace('$', '', regex=False).str.replace('-', '', regex=False)
venmoPayments['Amount (total)'] = pd.to_numeric(venmoPayments['Amount (total)'])
venmoPayments['Datetime'] = venmoPayments['Datetime'].str.split('T').str[0]
venmoPayments['Company'] = 'Venmo'
venmoPayments['Date'] = pd.to_datetime(venmoPayments['Datetime']).dt.date
venmoPayments.rename(columns={'Amount (total)': 'Amount'}, inplace=True)
venmoPayments['Notes'] = venmoPayments['Note'] + ' - ' + venmoPayments['To']
venmoPayments = venmoPayments[['Date', 'Company', 'Amount', 'Notes']]


print("Bank Debits:", bankDebits)
print("Bank Credits:", bankCredits)
print("Venmo Payments:", venmoPayments)

combinedDF = pd.concat([bankDebits, venmoPayments])
combinedDF['Date'] = pd.to_datetime(combinedDF['Date'])
combinedDF.sort_values(by='Date', ascending=True, inplace=True)
combinedDF.reset_index(drop=True, inplace=True)
combinedDF['Notes'] = combinedDF['Notes'].str.encode('ascii', 'ignore').str.decode('ascii')
combinedDF['Notes'] = combinedDF['Notes'].str.replace('-', '', regex=False)

combinedDF.to_csv(os.path.join(downloads_path, 'bank_debits.csv'), index=False)
bankCredits.to_csv(os.path.join(downloads_path, 'bank_credits.csv'), index=False)