import unittest
from datetime import datetime
import pandas as pd
from ing_explore import AccountStatements
from test.utils import mock_loader


class TestCharts(unittest.TestCase):

	estratto = AccountStatements(mock_loader([['01/01/2019', 'Ricarica Tel.', 'uscita 1', -10.0],
							['02/01/2019', 'Carta di credito.', 'uscita 2', -5.0],
							['03/02/2019', 'ACCREDITO BONIFICO', 'entrata 1', 18.0],
							['04/02/2019', 'VOSTRA DISPOSIZIONE', 'uscita 3', -55.0],
							['05/03/2019', 'ACCREDITO BONIFICO', 'entrata 2', 100.0],
							['06/03/2019', 'VOSTRA DISPOSIZIONE', 'uscita 4', -77.66],
							['07/04/2019', 'Altre entrate', 'entrata 3', 1.55],
							]))

	def assertChart(self, df, index, data, entrate, uscite, saldo=None):
			self.assertEqual(df.index[index], pd.to_datetime(data))
			self.assertEqual(df["Entrate"].iloc[index], entrate)
			self.assertEqual(df["Uscite"].iloc[index], uscite)
			if saldo:
				self.assertEqual(df["Saldo"].iloc[index], saldo)

	def test_month_chart_default(self):
		df, ax = self.estratto.month_chart()
		self.assertIsNotNone(df)
		self.assertIsNotNone(ax)
		self.assertEqual(len(df), 4)
		
		self.assertTrue(all(df.columns.values == ['Entrate', 'Uscite', 'Saldo']))

		self.assertChart(df, 0, '2019-01-31 00:00:00', 0.0, 15.0, -15.0)
		self.assertChart(df, 1, '2019-02-28 00:00:00', 18.0, 55.0, -52.0)
		self.assertChart(df, 2, '2019-03-31 00:00:00', 100.0, 77.66, -29.66)
		self.assertChart(df, 3, '2019-04-30 00:00:00', 1.55, 0.0, -28.11)

	def test_month_chart_saldo_iniziale(self):
		df, ax = self.estratto.month_chart(start_balance=-1000.0)
		self.assertIsNotNone(df)
		self.assertIsNotNone(ax)
		self.assertEqual(len(df), 4)
		
		self.assertTrue(all(df.columns.values == ['Entrate', 'Uscite', 'Saldo']))

		self.assertChart(df, 0, '2019-01-31 00:00:00', 0.0, 15.0, -1015.0)
		self.assertChart(df, 1, '2019-02-28 00:00:00', 18.0, 55.0, -1052.0)
		self.assertChart(df, 2, '2019-03-31 00:00:00', 100.0, 77.66, -1029.66)
		self.assertChart(df, 3, '2019-04-30 00:00:00', 1.55, 0.0, -1028.11)

	def test_month_chart_no_saldo(self):
		df, ax = self.estratto.month_chart(with_balance=False)
		self.assertIsNotNone(df)
		self.assertIsNotNone(ax)
		self.assertEqual(len(df), 4)
		
		self.assertTrue(all(df.columns.values == ['Entrate', 'Uscite']))

		self.assertChart(df, 0, '2019-01-31 00:00:00', 0.0, 15.0)
		self.assertChart(df, 1, '2019-02-28 00:00:00', 18.0, 55.0)
		self.assertChart(df, 2, '2019-03-31 00:00:00', 100.0, 77.66)
		self.assertChart(df, 3, '2019-04-30 00:00:00', 1.55, 0.0)		