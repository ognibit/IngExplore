"""
DataFrame loaders from different sources for the EstrattoConto init.
"""

import pandas as pd
import openpyxl as excel

def _prepare_df(movimenti):
	"""Cast the string columns into the right type"""
	# Converte le date in datetime
	movimenti['Data valuta'] = pd.to_datetime(movimenti['Data valuta'],format='%d/%m/%Y')
	movimenti['Data contabile'] = pd.to_datetime(movimenti['Data contabile'],format='%d/%m/%Y')

	# Converte l'importo in numero
	importo_series = movimenti['Importo'].str.replace('.','')
	importo_series = importo_series.str.extract('([-]*\d+,\d+)')[0]
	importo_series = importo_series.str.replace(',','.')
	movimenti['Importo'] = pd.to_numeric(importo_series)    
	
	return movimenti

def read_csv(filename, *args, **kwargs):
	"""
	Load from CSV file a Pandas DataFrame with the columns:
		- 'Data contabile' [datetime]
		- 'Data valuta' [datetime]
		- 'Causale' [string]
		- 'Descrizione operazione', [string]
		- 'Importo', [float]

	Parameters
	----------
	filename: str
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

	filename: str
		The path of the XLSX file.

	Returns
	-------
	DataFrame	
	"""
	#TODO add import openpyxl as excel to requirements
	workbook = excel.load_workbook(filename)
	sheet = workbook.active

	# get all the transactions, no header, no footer
	rows = [[cell.value for cell in row] for row in sheet.rows if row[0].value and "/" in row[0].value and row[1].value]

	movimenti = pd.DataFrame(rows, columns=['Data contabile', 'Data valuta', 'Causale', 'Descrizione operazione', 'Importo'])

	return _prepare_df(movimenti)
