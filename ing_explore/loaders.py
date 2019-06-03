"""DataFrame loaders from different sources for the AccountStatements init."""

import pandas as pd
import openpyxl as excel

def _prepare_df(transactions_df):
	"""Cast the string columns into the right type
	Parameters
	----------
	transactions_df : DataFrame
		The DataFrame where doing the casting

	Returns
	---------
	DataFrame

	"""
	# Converte le date in datetime
	transactions_df['Data valuta'] = pd.to_datetime(transactions_df['Data valuta'],format='%d/%m/%Y')
	transactions_df['Data contabile'] = pd.to_datetime(transactions_df['Data contabile'],format='%d/%m/%Y')

	# Converte l'importo in numero
	importo_series = transactions_df['Importo'].str.replace('.','')
	importo_series = importo_series.str.extract('([-]*\d+,\d+)')[0]
	importo_series = importo_series.str.replace(',','.')
	transactions_df['Importo'] = pd.to_numeric(importo_series)    
	
	return transactions_df

def read_csv(filename, *args, **kwargs):
	"""Load from CSV file a Pandas DataFrame with the columns:
	- 'Data contabile' [datetime]
	- 'Data valuta' [datetime]
	- 'Causale' [string]
	- 'Descrizione operazione', [string]
	- 'Importo', [float]

	Parameters
	----------
	filename : str
		The path of the csv file.

	*args, **kwargs
		passed to pd.read_csv

	Returns
	-------
	DataFrame		
	"""
	movimenti = pd.read_csv(filename, parse_dates=True, **kwargs)     
	
	return _prepare_df(movimenti)

def read_xlsx(filename):
	"""Load from XLSX file

	Parameters
	-----------
	filename : str
		The path of the XLSX file.

	Returns
	-------
	DataFrame	
	"""
	
	workbook = excel.load_workbook(filename)
	sheet = workbook.active

	# get all the transactions, no header, no footer
	rows = [[cell.value for cell in row] for row in sheet.rows if row[0].value and "/" in row[0].value and row[1].value]

	movimenti = pd.DataFrame(rows, columns=['Data contabile', 'Data valuta', 'Causale', 'Descrizione operazione', 'Importo'])

	return _prepare_df(movimenti)
