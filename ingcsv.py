"""
IngCsv
CLI interface for the EstrattoConto.
Use --help to see the usage.
"""

import os
import argparse
from datetime import datetime
from transaction import EstrattoConto, read_csv

def to_csv_files(estratto, out_dir):
	if not os.path.exists(out_dir):
	    os.makedirs(out_dir)

	estratto.entrate().to_csv(os.path.join(out_dir, "entrate.csv"))
	estratto.entrate(group_causale=True).to_csv(os.path.join(out_dir, "entrate_causale.csv"))
	estratto.uscite().to_csv(os.path.join(out_dir, "uscite.csv"))
	estratto.uscite(group_causale=True).to_csv(os.path.join(out_dir, "uscite_causale.csv"))
	
	estratto.mensili().to_csv(os.path.join(out_dir, "mensili.csv"))

	estratto.bonifici().to_csv(os.path.join(out_dir, "bonifici.csv"))

	estratto.disposizioni().to_csv(os.path.join(out_dir, "disposizioni.csv"))

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--in", "-i", required=True, help="Il file CSV (estratto conto) es: MovimentiContoCorrenteArancio.csv")
	ap.add_argument("--out", "-o", required=False, help="La cartella dove verranno creati i file di output")
	ap.add_argument("--saldo_al", "-s", required=False, help="Calcolo del saldo al giorno. Formato dd/mm/yyyy (es: 05/03/2019)")
	ap.add_argument("--giroconti", "-g", required=False, action='store_true', help="Vengono inclusi i giroconti tra i movimenti")

	args = vars(ap.parse_args())

	file_in = args["in"]
	out_dir = args["out"] or "output"
	include_giroconti = args["giroconti"]	
	saldo_al = args["saldo_al"]
	
	df = read_csv(file_in)
	estratto = EstrattoConto(df, giroconti=include_giroconti)

	if saldo_al is not None:
		date_saldo = datetime.strptime(saldo_al, "%d/%m/%Y")		
		saldo = estratto.saldo_al(date_saldo)
		print(saldo)
	else:		
		to_csv_files(estratto, out_dir)

if __name__ == '__main__':
	main()