import unittest
from datetime import datetime
import pandas as pd
from EstrattoConto import EstrattoConto

def mock_loader(data):
	columns = ['Data contabile', 'Causale', 'Descrizione operazione', 'Importo']
	
	movimenti = pd.DataFrame(data, columns=columns)
	movimenti['Data contabile'] = pd.to_datetime(movimenti['Data contabile'],format='%d/%m/%Y')
	movimenti['Data valuta'] = movimenti['Data contabile']
	
	return movimenti

class TestSaldoAl(unittest.TestCase):

	def base_loader(self):
		def _loader(f):
			return mock_loader([['01/01/2019', 'Ricarica Tel.', 'nulla', -10.0],
								['02/01/2019', 'Carta di credito.', 'nulla', -5.0],
								['03/01/2019', 'ACCREDITO BONIFICO', 'nulla', 18.0]])
		return _loader

	def test_saldo_al_before(self):
		estratto = EstrattoConto('test', loader=self.base_loader())
		self.assertEquals(estratto.saldo_al(datetime.strptime('31/12/2018','%d/%m/%Y')), 0.0)

	def test_saldo_al_after(self):
		estratto = EstrattoConto('test', loader=self.base_loader())
		self.assertEquals(estratto.saldo_al(datetime.strptime('20/01/2019','%d/%m/%Y')), 3.0)

	def test_saldo_al_inf(self):
		estratto = EstrattoConto('test', loader=self.base_loader())
		self.assertEquals(estratto.saldo_al(datetime.strptime('01/01/2019','%d/%m/%Y')), -10.0)

	def test_saldo_al_up(self):
		estratto = EstrattoConto('test', loader=self.base_loader())
		self.assertEquals(estratto.saldo_al(datetime.strptime('03/01/2019','%d/%m/%Y')), 3.0)

	def test_saldo_al_mid(self):
		estratto = EstrattoConto('test', loader=self.base_loader())
		self.assertEquals(estratto.saldo_al(datetime.strptime('02/01/2019','%d/%m/%Y')), -15.0)

if __name__ == '__main__':
	unittest.main()