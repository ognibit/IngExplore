"""Unit tests for AccountStatements.balance_at()"""

import unittest
from datetime import datetime
import pandas as pd
from ing_explore import AccountStatements
from test.utils import mock_loader

class TestBalanceAt(unittest.TestCase):

	estratto = AccountStatements(mock_loader([['01/01/2019', 'Ricarica Tel.', 'nulla', -10.0],
							['02/01/2019', 'Carta di credito.', 'nulla', -5.0],
							['03/01/2019', 'ACCREDITO BONIFICO', 'nulla', 18.0]]))

	movimenti_giro = mock_loader([['01/01/2019', 'Ricarica Tel.', 'nulla', -10.0],      # -10
							['03/01/2019', 'ACCREDITO BONIFICO', 'nulla', 20.0],      #  10
							['04/01/2019', 'GIRO DA MIEI CONTI', 'nulla', 1000.0],    # 1010
							['05/01/2019', 'GIRO VERSO MIEI CONTI', 'nulla', -500.0], # 510
							['05/01/2019', 'VS.DISPOSIZIONE', 'nulla', -10.0]])       # 500

	def test_balance_at_before(self):		
		self.assertEqual(self.estratto.balance_at(datetime.strptime('31/12/2018','%d/%m/%Y')), 0.0)

	def test_balance_at_after(self):
		self.assertEqual(self.estratto.balance_at(datetime.strptime('20/01/2019','%d/%m/%Y')), 3.0)

	def test_balance_at_inf(self):
		self.assertEqual(self.estratto.balance_at(datetime.strptime('01/01/2019','%d/%m/%Y')), -10.0)

	def test_balance_at_up(self):
		self.assertEqual(self.estratto.balance_at(datetime.strptime('03/01/2019','%d/%m/%Y')), 3.0)

	def test_balance_at_mid(self):
		self.assertEqual(self.estratto.balance_at(datetime.strptime('02/01/2019','%d/%m/%Y')), -15.0)

	def test_balance_at_with_giroconto(self):
		estratto_giro = AccountStatements(self.movimenti_giro, giro=True)
		self.assertEqual(estratto_giro.balance_at(datetime.strptime('06/01/2019','%d/%m/%Y')), 500)

	def test_balance_at_without_giroconto(self):
		estratto_giro = AccountStatements(self.movimenti_giro, giro=False)
		self.assertEqual(estratto_giro.balance_at(datetime.strptime('06/01/2019','%d/%m/%Y')), 0)

if __name__ == '__main__':
	unittest.main()