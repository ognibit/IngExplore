"""Tests for the EstrattoConto export functions"""

import unittest
from datetime import datetime
import pandas as pd
from ing_explore import EstrattoConto
from test.utils import mock_loader

def get_first_value(df, filter_col, filter_value, result_col):
	return df[df[filter_col] == filter_value][result_col].values[0]

def get_record(df, filter_value, result_col):
	return get_first_value(df, 'Descrizione operazione', filter_value, result_col)

class TestSaldoAl(unittest.TestCase):

	estratto = EstrattoConto(mock_loader([['01/01/2019', 'Ricarica Tel.', 'uscita 1', -10.0],
							['02/01/2019', 'Carta di credito.', 'uscita 2', -5.0],
							['03/01/2019', 'ACCREDITO BONIFICO', 'entrata 1', 18.0],
							['04/01/2019', 'VOSTRA DISPOSIZIONE', 'uscita 3', -55.0],
							['05/01/2019', 'ACCREDITO BONIFICO', 'entrata 2', 100.0],
							['06/02/2019', 'VOSTRA DISPOSIZIONE', 'uscita 4', -77.66],
							['07/02/2019', 'Altre entrate', 'entrata 3', 1.55],
							]))

	descrizioni = EstrattoConto(mock_loader([['01/01/2019', 'Ricarica Tel.', 'uscita 1', -10.0],
							['02/01/2019', 'Carta di credito.', 'uscita 2', -5.0],
							['03/01/2019', 'ACCREDITO BONIFICO', 'Bonifico N. 0000000000000000 BIC Ordinante XXXXXXXXXXX Data Ordine Codifica Ordinante IT74T0000000000000000000000 Anagrafica Ordinante DITTA Note: STIPENDIO', 18.0],
							['04/01/2019', 'VS.DISPOSIZIONE', 'BONIFICO DA VOI DISPOSTO NOP 00000000000 A FAVORE DI Pinco Pallo C. BENEF. IT76I0000000000000000000000 NOTE: disposizione 1', -55.0],
							['05/01/2019', 'ACCREDITO BONIFICO', 'Bonifico N. 0000000000000000 BIC Ordinante XXXXXXXXXXX Data Ordine Codifica Ordinante IT74T0000000000000000000000 Anagrafica Ordinante TIZIO Note: ALTRO', 100.0],
							['06/02/2019', 'VS.DISPOSIZIONE', 'BONIFICO DA VOI DISPOSTO NOP 00000000000 A FAVORE DI Giulio Cesare C. BENEF. IT76I0000000000000000000000 NOTE: disposizione 2', -77.66],
							['07/02/2019', 'Altre entrate', 'entrata 3', 1.55],
							]))


	#========= ENTRATE ==============#
	def test_entrate(self):
		entrate = self.estratto.entrate()		
		self.assertEqual(len(entrate), 3)
		self.assertEqual(get_record(entrate, 'entrata 1', 'Entrate'), 18.0)
		self.assertEqual(get_record(entrate, 'entrata 2', 'Entrate'), 100.0)
		self.assertEqual(get_record(entrate, 'entrata 3', 'Entrate'), 1.55)

	def test_entrate_group_causale(self):
		entrate = self.estratto.entrate(group_causale=True)		
		self.assertEqual(len(entrate), 2)		
		self.assertEqual(entrate.loc['ACCREDITO BONIFICO'].values[0], 118.0)
		self.assertEqual(entrate.loc['Altre entrate'].values[0], 1.55)

	#========= USCITE ==============#
	def test_uscite(self):
		uscite = self.estratto.uscite()
		self.assertEqual(len(uscite), 4)
		self.assertEqual(get_record(uscite, 'uscita 1', 'Uscite'), 10.0)
		self.assertEqual(get_record(uscite, 'uscita 2', 'Uscite'), 5.0)
		self.assertEqual(get_record(uscite, 'uscita 3', 'Uscite'), 55.0)
		self.assertEqual(get_record(uscite, 'uscita 4', 'Uscite'), 77.66)

	def test_uscite_group_causale(self):
		uscite = self.estratto.uscite(group_causale=True)		
		self.assertEqual(len(uscite), 3)		
		self.assertEqual(uscite.loc['Ricarica Tel.'].values[0], 10.0)
		self.assertEqual(uscite.loc['Carta di credito.'].values[0], 5.00)
		self.assertEqual(uscite.loc['VOSTRA DISPOSIZIONE'].values[0], 132.66)

	#========= OTHERS ==============#
	def test_mensili(self):
		mensili = self.estratto.mensili()		
		self.assertTrue(all(mensili.columns.values == ['2019-01', '2019-02', 'TOTALE']))
		self.assertTrue(all(mensili.index.values == ['ACCREDITO BONIFICO', 'Altre entrate', 'Carta di credito.', 'Ricarica Tel.', 'VOSTRA DISPOSIZIONE', 'TOTALE']))
		self.assertEqual(mensili.loc['TOTALE']['TOTALE'], -28.11)

	def test_bonifici(self):
		bonifici = self.descrizioni.bonifici()
		self.assertTrue(all(bonifici.columns.values == ['Data contabile', 'Descrizione operazione', 'Importo', 'Data valuta', 'bonifico_ordinante', 'bonifico_nota']))
		self.assertEqual(len(bonifici), 2)
		self.assertEqual(get_first_value(bonifici, 'bonifico_ordinante', 'DITTA', 'Importo'), 18.0)
		self.assertEqual(get_first_value(bonifici, 'bonifico_ordinante', 'DITTA', 'bonifico_nota'), 'STIPENDIO')

	def test_disposizioni(self):
		disposizioni = self.descrizioni.disposizioni()
		self.assertTrue(all(disposizioni.columns.values == ['Data contabile', 'Descrizione operazione', 'Importo', 'Data valuta', 'disposizione_nota']))
		self.assertEqual(len(disposizioni), 2)
		self.assertEqual(get_first_value(disposizioni, 'disposizione_nota', 'disposizione 1', 'Importo'), -55.00)
		self.assertEqual(get_first_value(disposizioni, 'disposizione_nota', 'disposizione 2', 'Importo'), -77.66)

	#TODO test with and without giroconti