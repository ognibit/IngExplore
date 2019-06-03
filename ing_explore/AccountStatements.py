import numpy as np
import pandas as pd

class AccountStatements():	
	"""A wrapper for the DataFrame containg the account transactions.

	Parameters	
	----------
	df : DataFrame
		- Columns: 'Data contabile', 'Data valuta', 'Causale', 'Descrizione operazione', 'Importo'
		- 'Data contabile': datetime64
		- 'Data valuta': datetime64
		- 'Causale': str
		- 'Descrizione operazione': str
		- 'Importo': numeric

	giro : boolean (default False) 
		include the internal accounts transfers (giro)
	"""


	columns = ['Data contabile', 'Data valuta', 'Causale', 'Descrizione operazione', 'Importo']

	def __init__(self, df, giro=False):
		self.transactions = df.copy()

		# New Columns
		self.transactions['Entrate'] = self.transactions[self.transactions['Importo'] > 0]['Importo']
		self.transactions['Uscite'] = self.transactions[self.transactions['Importo'] < 0]['Importo']
		self.transactions['Uscite'] = -1 * self.transactions['Uscite']
		self.transactions.fillna(0, inplace=True)

		if not giro:
			self.transactions = self.transactions[self.transactions["Causale"] != 'GIRO DA MIEI CONTI']
			self.transactions = self.transactions[self.transactions["Causale"] != 'GIRO VERSO MIEI CONTI']			

	def incomes(self, group_types=False):
		"""Get only the incomes.

		Parameters	
		----------
		group_types : boolean (default False)
			Set if the output has to be grouped by transaction types.

		Returns
		-------
		DataFrame('Data contabile', 'Causale', 'Descrizione operazione', 'Data valuta', 'Entrate')
			if group_types == True: DataFrame('Causale', 'Entrate')
		"""		
		incomes = self.transactions[self.transactions['Importo'] >= 0].drop(["Importo","Uscite"], axis=1)

		if group_types:
			return incomes.groupby('Causale').sum()
		else:
			return incomes
		
	def expenses(self, group_types=False):
		"""Get only the expenses.

		Parameters	
		----------
		expenses : boolean (default False)
			Set if the output has to be grouped by transaction types. 
		
		Returns
		-------
		DataFrame('Data contabile', 'Causale', 'Descrizione operazione', 'Data valuta', 'Uscite')
			if expenses == True: DataFrame('Causale', 'Uscite')

			'Uscite' numeric positive
		"""				
		expenses = self.transactions[self.transactions['Importo'] < 0].drop(["Importo","Entrate"], axis=1)

		if group_types:
			return expenses.groupby('Causale').sum()
		else:
			return expenses	

	def month_amounts(self):
		"""Type on row, months on columns (plus total amounts).

		Parameters	
		----------

		Returns
		-------
		DataFrame pivot : 
			- index: Causale
			- column: mese
			- value: sum(Importo)
			With margins (TOTALE)
		"""				
		types = np.unique(self.transactions['Causale'].values)
		types_df = self.transactions['Causale'].str.get_dummies()

		for typ in types:
			types_df[typ] = self.transactions[ self.transactions['Causale'] == typ ]['Importo'].abs()

		types_df.fillna(0, inplace=True)

		months = self.transactions.join(types_df)
		months['mese'] = self.transactions['Data contabile'].dt.strftime('%Y-%m')
		return months.pivot_table('Importo'
			, index='Causale'
			, columns='mese'
			, aggfunc='sum'
			, margins=True
			, margins_name='TOTALE').fillna(0).round(2)

	def transfers(self):
		"""Get only the transfers.

		Parameters	
		----------

		Returns
		-------
		DataFrame :
			- 'Data contabile'
			- 'Descrizione operazione'
			- 'Importo'
			- 'Data valuta',
			- 'bonifico_ordinante'
			- 'bonifico_nota'				
		"""				
		transfers = self.transactions[self.transactions['Causale'] == 'ACCREDITO BONIFICO'].drop(["Entrate","Uscite","Causale"], axis=1)
		transfers_desc = transfers['Descrizione operazione'].str.split('Ordinante').apply(lambda x: x[-1])
		transfers['bonifico_ordinante'] = transfers_desc.str.split('Note:').apply(lambda x: x[0].strip())
		transfers['bonifico_nota'] = transfers_desc.str.split('Note:').apply(lambda x: x[1].strip())		

		return transfers
		
	def operations(self):
		"""Get only the operations.

		Parameters	
		----------

		Returns
		-------
		DataFrame :
			- 'Data contabile'
			- 'Descrizione operazione'
			- 'Importo'
			- 'Data valuta'
			- 'disposizione_nota'			
		"""				
		operations = self.transactions[self.transactions['Causale'] == 'VS.DISPOSIZIONE'].drop(["Entrate","Uscite","Causale"], axis=1)
		operations_note = operations['Descrizione operazione']
		operations_note = operations_note.str.split('NOTE:').apply(lambda x: x[1])
		operations_note = operations_note.str.strip()
		operations['disposizione_nota'] = operations_note	

		return operations	

	def balance_at(self, at):
		"""Sum of the amounts from the beggining of the transactions to the input day.

		Parameters	
		----------
		al : datetime
			The day, included, when to get the balance amount.

		Returns
		-------
		float
		"""				
		return self.transactions[self.transactions["Data contabile"] <= at ]["Importo"].sum().round(2)		
		
	def month_chart(self, index_date_column='Data contabile', with_balance=True, start_balance=0.0):
		"""Incomes and expenses grouped by month to build a chart.

		Parameters	
		----------
		index_date_column : str, default 'Data contabile'
			The aggregation column. 'Data contabile' or 'Data valuta'

		with_balance : bool, default True
			Add the Saldo column to the output.

		start_balance : float, default 0.0
			The initial balance.

		Returns
		-------
		DataFrame, matplotlib.axes.Axes
		"""
		columns = ['Entrate','Uscite']

		transactions_ts = self.transactions.set_index(index_date_column)
		months = transactions_ts.resample('M').sum()

		if with_balance:
			months["Saldo"] = months["Importo"].cumsum() + start_balance
			columns.append('Saldo')

		months = months[columns]
		months = months.round(2)

		ax = months[columns].plot(kind='barh', figsize=(14,6), color=['green','red','steelblue'])

		ax.set(title='Bilancio Mensile', xlabel='Euro')

		# Y format
		yticks = [pd.to_datetime(item.get_text()).strftime('%Y-%b') for item in ax.get_yticklabels()]
		ax.set_yticklabels(yticks);

		return months, ax