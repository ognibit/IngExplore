"""Tests for the AccountStatements export functions"""

import unittest
from datetime import datetime
import pandas as pd
from ing_explore import AccountStatements
from test.utils import mock_loader

def get_first_value(df, filter_col, filter_value, result_col):
	return df[df[filter_col] == filter_value][result_col].values[0]

def get_record(df, filter_value, result_col):
	return get_first_value(df, 'Descrizione operazione', filter_value, result_col)

class TestSaldoAl(unittest.TestCase):

	estratto = AccountStatements(mock_loader([['01/01/2019', 'Ricarica Tel.', 'uscita 1', -10.0],
							['02/01/2019', 'Carta di credito.', 'uscita 2', -5.0],
							['03/01/2019', 'ACCREDITO BONIFICO', 'entrata 1', 18.0],
							['04/01/2019', 'VOSTRA DISPOSIZIONE', 'uscita 3', -55.0],
							['05/01/2019', 'ACCREDITO BONIFICO', 'entrata 2', 100.0],
							['06/02/2019', 'VOSTRA DISPOSIZIONE', 'uscita 4', -77.66],
							['07/02/2019', 'Altre entrate', 'entrata 3', 1.55],
							]))

	descrizioni = AccountStatements(mock_loader([['01/01/2019', 'Ricarica Tel.', 'uscita 1', -10.0],
							['02/01/2019', 'Carta di credito.', 'uscita 2', -5.0],
							['03/01/2019', 'ACCREDITO BONIFICO', 'Bonifico N. 0000000000000000 BIC Ordinante XXXXXXXXXXX Data Ordine Codifica Ordinante IT74T0000000000000000000000 Anagrafica Ordinante DITTA Note: STIPENDIO', 18.0],
							['04/01/2019', 'VS.DISPOSIZIONE', 'BONIFICO DA VOI DISPOSTO NOP 00000000000 A FAVORE DI Pinco Pallo C. BENEF. IT76I0000000000000000000000 NOTE: disposizione 1', -55.0],
							['05/01/2019', 'ACCREDITO BONIFICO', 'Bonifico N. 0000000000000000 BIC Ordinante XXXXXXXXXXX Data Ordine Codifica Ordinante IT74T0000000000000000000000 Anagrafica Ordinante TIZIO Note: ALTRO', 100.0],
							['06/02/2019', 'VS.DISPOSIZIONE', 'BONIFICO DA VOI DISPOSTO NOP 00000000000 A FAVORE DI Giulio Cesare C. BENEF. IT76I0000000000000000000000 NOTE: disposizione 2', -77.66],
							['07/02/2019', 'Altre entrate', 'entrata 3', 1.55],
							]))


	#========= INCOMES ==============#
	def test_incomes(self):
		incomes = self.estratto.incomes()		
		self.assertEqual(len(incomes), 3)
		self.assertEqual(get_record(incomes, 'entrata 1', 'Entrate'), 18.0)
		self.assertEqual(get_record(incomes, 'entrata 2', 'Entrate'), 100.0)
		self.assertEqual(get_record(incomes, 'entrata 3', 'Entrate'), 1.55)

	def test_incomes_group_types(self):
		incomes = self.estratto.incomes(group_types=True)		
		self.assertEqual(len(incomes), 2)		
		self.assertEqual(incomes.loc['ACCREDITO BONIFICO'].values[0], 118.0)
		self.assertEqual(incomes.loc['Altre entrate'].values[0], 1.55)

	#========= EXPENSES ==============#
	def test_expenses(self):
		expenses = self.estratto.expenses()
		self.assertEqual(len(expenses), 4)
		self.assertEqual(get_record(expenses, 'uscita 1', 'Uscite'), 10.0)
		self.assertEqual(get_record(expenses, 'uscita 2', 'Uscite'), 5.0)
		self.assertEqual(get_record(expenses, 'uscita 3', 'Uscite'), 55.0)
		self.assertEqual(get_record(expenses, 'uscita 4', 'Uscite'), 77.66)

	def test_expenses_group_types(self):
		expenses = self.estratto.expenses(group_types=True)		
		self.assertEqual(len(expenses), 3)		
		self.assertEqual(expenses.loc['Ricarica Tel.'].values[0], 10.0)
		self.assertEqual(expenses.loc['Carta di credito.'].values[0], 5.00)
		self.assertEqual(expenses.loc['VOSTRA DISPOSIZIONE'].values[0], 132.66)

	#========= OTHERS ==============#
	def test_month_amounts(self):
		mensili = self.estratto.month_amounts()		
		self.assertTrue(all(mensili.columns.values == ['2019-01', '2019-02', 'TOTALE']))
		self.assertTrue(all(mensili.index.values == ['ACCREDITO BONIFICO', 'Altre entrate', 'Carta di credito.', 'Ricarica Tel.', 'VOSTRA DISPOSIZIONE', 'TOTALE']))
		self.assertEqual(mensili.loc['TOTALE']['TOTALE'], -28.11)

	def test_transfers(self):
		transfers = self.descrizioni.transfers()
		self.assertTrue(all(transfers.columns.values == ['Data contabile', 'Descrizione operazione', 'Importo', 'Data valuta', 'bonifico_ordinante', 'bonifico_nota']))
		self.assertEqual(len(transfers), 2)
		self.assertEqual(get_first_value(transfers, 'bonifico_ordinante', 'DITTA', 'Importo'), 18.0)
		self.assertEqual(get_first_value(transfers, 'bonifico_ordinante', 'DITTA', 'bonifico_nota'), 'STIPENDIO')

	def test_operations(self):
		operations = self.descrizioni.operations()
		self.assertTrue(all(operations.columns.values == ['Data contabile', 'Descrizione operazione', 'Importo', 'Data valuta', 'disposizione_nota']))
		self.assertEqual(len(operations), 2)
		self.assertEqual(get_first_value(operations, 'disposizione_nota', 'disposizione 1', 'Importo'), -55.00)
		self.assertEqual(get_first_value(operations, 'disposizione_nota', 'disposizione 2', 'Importo'), -77.66)

	#TODO test with and without giro