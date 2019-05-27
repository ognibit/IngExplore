import numpy as np
import pandas as pd

class EstrattoConto():
	"""Il modulo per l'elaborazione del CSV IngDirect in Italiano"""
	columns = ['Data contabile', 'Data valuta', 'Causale', 'Descrizione operazione', 'Importo']

	def __init__(self, df, giroconti=False):
		"""
		Parameters	
		----------
		df: DataFrame
			Columns: 'Data contabile', 'Data valuta', 'Causale', 'Descrizione operazione', 'Importo'
			'Data contabile': datetime64
			'Data valuta': datetime64
			'Causale': str
			'Descrizione operazione': str
			'Importo': numeric

		giroconti: boolean (default False) 
			Se True include anche i giroconti nei calcoli.			
		"""
		self.movimenti = df.copy()

		# New Columns
		self.movimenti['Entrate'] = self.movimenti[self.movimenti['Importo'] > 0]['Importo']
		self.movimenti['Uscite'] = self.movimenti[self.movimenti['Importo'] < 0]['Importo']
		self.movimenti['Uscite'] = -1 * self.movimenti['Uscite']
		self.movimenti.fillna(0, inplace=True)

		if not giroconti:
			self.movimenti = self.movimenti[self.movimenti["Causale"] != 'GIRO DA MIEI CONTI']
			self.movimenti = self.movimenti[self.movimenti["Causale"] != 'GIRO VERSO MIEI CONTI']			

	def entrate(self, group_causale=False):
		"""
		Parameters	
		----------
			group_causale: boolean (default False)
			Indica se avere o meno le entrate raggruppate e sommate per Causale 
		Returns
		-------
			DataFrame('Data contabile', 'Causale', 'Descrizione operazione', 'Data valuta', 'Entrate')
			if group_causale == True: DataFrame('Causale', 'Entrate')
		"""		
		entrate = self.movimenti[self.movimenti['Importo'] >= 0].drop(["Importo","Uscite"], axis=1)

		if group_causale:
			return entrate.groupby('Causale').sum()
		else:
			return entrate
		
	def uscite(self, group_causale=False):
		"""
		Parameters	
		----------
			group_causale: boolean (default False)
			Indica se avere o meno le uscite raggruppate e sommate per Causale 
		Returns
		-------
			DataFrame('Data contabile', 'Causale', 'Descrizione operazione', 'Data valuta', 'Uscite')
			if group_causale == True: DataFrame('Causale', 'Uscite')

			'Uscite' numeric positive
		"""				
		uscite = self.movimenti[self.movimenti['Importo'] < 0].drop(["Importo","Entrate"], axis=1)

		if group_causale:
			return uscite.groupby('Causale').sum()
		else:
			return uscite	

	def mensili(self):
		"""
		Parameters	
		----------

		Returns
		-------
			DataFrame pivot: 
				- index: Causale
				- column: mese
				- value: sum(Importo)
			With margins (TOTALE)
		"""				
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
			, margins_name='TOTALE').fillna(0).round(2)

	def bonifici(self):
		"""
		Parameters	
		----------

		Returns
		-------
			DataFrame:
				-'Data contabile'
				-'Descrizione operazione'
				-'Importo'
				-'Data valuta',
				-'bonifico_ordinante'
				-'bonifico_nota'				
		"""				
		bonifici = self.movimenti[self.movimenti['Causale'] == 'ACCREDITO BONIFICO'].drop(["Entrate","Uscite","Causale"], axis=1)
		bonifico_desc = bonifici['Descrizione operazione'].str.split('Ordinante').apply(lambda x: x[-1])
		bonifici['bonifico_ordinante'] = bonifico_desc.str.split('Note:').apply(lambda x: x[0].strip())
		bonifici['bonifico_nota'] = bonifico_desc.str.split('Note:').apply(lambda x: x[1].strip())		

		return bonifici
		
	def disposizioni(self):
		"""
		Parameters	
		----------

		Returns
		-------
			DataFrame:
				-'Data contabile'
				-'Descrizione operazione'
				-'Importo'
				-'Data valuta'
				-'disposizione_nota'			
		"""				
		disposizioni = self.movimenti[self.movimenti['Causale'] == 'VS.DISPOSIZIONE'].drop(["Entrate","Uscite","Causale"], axis=1)
		disposizione_nota = disposizioni['Descrizione operazione']
		disposizione_nota = disposizione_nota.str.split('NOTE:').apply(lambda x: x[1])
		disposizione_nota = disposizione_nota.str.strip()
		disposizioni['disposizione_nota'] = disposizione_nota	

		return disposizioni	

	def saldo_al(self, al):
		"""
		Somma degli importi dall'inizio dei movimenti fino al giorno indicato compreso

		Parameters	
		----------
			al: datetime
			La data (compresa) di cui si vuole sapere il saldo.
		Returns
		-------
		float
		"""				
		return self.movimenti[self.movimenti["Data contabile"] <= al ]["Importo"].sum().round(2)		
		
