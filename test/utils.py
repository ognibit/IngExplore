"""Common functions for unit testing"""

import pandas as pd

def mock_loader(data):
	"""
	Load the data into a DataFrame for AccountStatements

	Parameters	
	----------
	data: 2D python list
		Data reppresents the row with collumns: 'Data contabile', 'Causale', 'Descrizione operazione', 'Importo'
		'Data Contabile' must be str formatted as 'dd/mm/yyyy'
		'Importo' must be numeric

	Returns
	-------
	DataFrame
	"""
	columns = ['Data contabile', 'Causale', 'Descrizione operazione', 'Importo']
	
	movimenti = pd.DataFrame(data, columns=columns)
	movimenti['Data contabile'] = pd.to_datetime(movimenti['Data contabile'],format='%d/%m/%Y')
	movimenti['Data valuta'] = movimenti['Data contabile']
	
	return movimenti
