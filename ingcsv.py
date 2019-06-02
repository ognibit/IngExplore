"""
IngCsv
CLI interface for the EstrattoConto.
Use --help to see the usage.
"""

import os
import argparse
from datetime import datetime
from transaction import EstrattoConto, read_csv, read_xlsx, __version__
import matplotlib.pyplot as plt

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

def to_images(estratto, out_dir, saldo_iniziale):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)	

	df, ax = estratto.andamento_mensile(saldo_iniziale=saldo_iniziale)
	ax.figure.savefig(os.path.join(out_dir, "andamento_mensile.png"))
	

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--in", "-i", required=True, help="Il file CSV o XLSX (movimenti conto) es: MovimentiContoCorrenteArancio.csv")
	ap.add_argument("--out", "-o", required=False, help="La cartella dove verranno creati i file di output")
	ap.add_argument("--saldo_al", "-s", required=False, help="Calcolo del saldo al giorno. Formato dd/mm/yyyy (es: 05/03/2019)")
	ap.add_argument("--saldo_iniziale", "-si", required=False, help="Imposta il saldo pre-esistente. Valido per i grafici e saldo_al.")
	ap.add_argument("--giroconti", "-g", required=False, action='store_true', help="Vengono inclusi i giroconti tra i movimenti")
	ap.add_argument("-v", "--version", action="version", version='%(prog)s ' + __version__)



	args = vars(ap.parse_args())

	file_in = args["in"]
	out_dir = args["out"] or "output"
	include_giroconti = args["giroconti"]	
	saldo_al = args["saldo_al"]
	saldo_iniziale = float( args["saldo_iniziale"] or "0" )
	
	_, extension = os.path.splitext(file_in)

	if extension == '.csv':
		df = read_csv(file_in)
	elif extension == '.xlsx':
		df = read_xlsx(file_in)
	else:
		raise ValueError("Only .csv or .xlsx extension allowed")

	estratto = EstrattoConto(df, giroconti=include_giroconti)

	if saldo_al is not None:
		date_saldo = datetime.strptime(saldo_al, "%d/%m/%Y")		
		saldo = estratto.saldo_al(date_saldo)
		saldo = saldo + saldo_iniziale
		print(saldo.round(2))
	else:		
		to_csv_files(estratto, out_dir)
		to_images(estratto, out_dir, saldo_iniziale)

if __name__ == '__main__':
	main()