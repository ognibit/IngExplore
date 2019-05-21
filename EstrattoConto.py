import numpy as np
import pandas as pd

class EstrattoConto():
	"""Il modulo per l'elaborazione del CSV IngDirect in Italiano"""

	def __init__(self, filename, giroconti=False):
		"""
		Args:
			filename: il path del file CSV con i movimenti del conto corrente
		Kwargs:
			giroconti: (default False) se True include anche i giroconti nei calcoli.			
		"""
		self.movimenti = pd.read_csv(filename, parse_dates=True) 
		# Converte le date in datetime
		self.movimenti['Data valuta'] = pd.to_datetime(self.movimenti['Data valuta'],format='%d/%m/%Y')
		self.movimenti['Data contabile'] = pd.to_datetime(self.movimenti['Data contabile'],format='%d/%m/%Y')

		# Converte l'importo in numero
		importo_series = self.movimenti['Importo'].str.replace('.','')
		importo_series = importo_series.str.extract('([-]*\d+,\d+)')[0]
		importo_series = importo_series.str.replace(',','.')
		self.movimenti['Importo'] = pd.to_numeric(importo_series)

		# New Columns
		self.movimenti['Entrate'] = self.movimenti[self.movimenti['Importo'] > 0]['Importo']
		self.movimenti['Uscite'] = self.movimenti[self.movimenti['Importo'] < 0]['Importo']
		self.movimenti['Uscite'] = -1 * self.movimenti['Uscite']
		self.movimenti.fillna(0, inplace=True)

		if not giroconti:
			self.movimenti = self.movimenti[self.movimenti["Causale"] != 'GIRO DA MIEI CONTI']
			self.movimenti = self.movimenti[self.movimenti["Causale"] != 'GIRO VERSO MIEI CONTI']			

	def entrate(self, group_causale=False):
		
		entrate = self.movimenti[self.movimenti['Importo'] >= 0].drop(["Importo","Uscite"], axis=1)

		if group_causale:
			return entrate.groupby('Causale').sum()
		else:
			return entrate
		
	def uscite(self, group_causale=False):
		
		uscite = self.movimenti[self.movimenti['Importo'] < 0].drop(["Importo","Entrate"], axis=1)

		if group_causale:
			return uscite.groupby('Causale').sum()
		else:
			return uscite	

	def mensili(self):
		causali = np.unique(self.movimenti['Causale'].values)
		causali_df = self.movimenti['Causale'].str.get_dummies()

		for causale in causali:
		    causali_df[causale] = self.movimenti[ self.movimenti['Causale'] == causale ]['Importo'].abs()

		causali_df.fillna(0, inplace=True)

		mensili = self.movimenti.join(causali_df)
		mensili['mese'] = self.movimenti['Data contabile'].dt.strftime('%Y-%m')
		return mensili.pivot_table('Importo'
			, index='Causale'
			, columns='mese'
			, aggfunc='sum'
			, margins=True
			, margins_name='TOTALE').fillna(0)

	def bonifici(self):
		bonifici = self.movimenti[self.movimenti['Causale'] == 'ACCREDITO BONIFICO'].drop(["Entrate","Uscite","Causale"], axis=1)
		bonifico_desc = bonifici['Descrizione operazione'].str.split('Ordinante').apply(lambda x: x[-1])
		bonifici['bonifico_ordinante'] = bonifico_desc.str.split('Note:').apply(lambda x: x[0].strip())
		bonifici['bonifico_nota'] = bonifico_desc.str.split('Note:').apply(lambda x: x[1].strip())		

		return bonifici
		
	def disposizioni(self):
		disposizioni = self.movimenti[self.movimenti['Causale'] == 'VS.DISPOSIZIONE'].drop(["Entrate","Uscite","Causale"], axis=1)
		disposizione_nota = disposizioni['Descrizione operazione']
		disposizione_nota = disposizione_nota.str.split('NOTE:').apply(lambda x: x[1])
		disposizione_nota = disposizione_nota.str.strip()
		disposizioni['disposizione_nota'] = disposizione_nota	

		return disposizioni	
