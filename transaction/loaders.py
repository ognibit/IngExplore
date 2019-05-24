import pandas as pd

def read_csv(filename, *args, **kwargs):
	"""
	Load from CSV file a Pandas DataFrame with the columns:
		- 'Data contabile' [datetime]
		- 'Data valuta' [datetime]
		- 'Causale' [string]
		- 'Descrizione operazione', [string]
		- 'Importo', [float]
	"""
	movimenti = pd.read_csv(filename, parse_dates=True, **kwargs) 
	# Converte le date in datetime
	movimenti['Data valuta'] = pd.to_datetime(movimenti['Data valuta'],format='%d/%m/%Y')
	movimenti['Data contabile'] = pd.to_datetime(movimenti['Data contabile'],format='%d/%m/%Y')

	# Converte l'importo in numero
	importo_series = movimenti['Importo'].str.replace('.','')
	importo_series = importo_series.str.extract('([-]*\d+,\d+)')[0]
	importo_series = importo_series.str.replace(',','.')
	movimenti['Importo'] = pd.to_numeric(importo_series)    
	
	return movimenti

