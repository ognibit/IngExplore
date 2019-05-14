"""IngCsv"""

import os
import argparse
from EstrattoConto import EstrattoConto

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--in", "-i", required=True, help="Il file CSV (estratto conto) es: MovimentiContoCorrenteArancio.csv")
	ap.add_argument("--out", "-o", required=False, help="La cartella dove verranno creati i file di output")
	ap.add_argument("--saldo_al", "-s", required=False, help="Calcolo del saldo al giorno. Formato dd/mm/yyyy (es: 05/03/2019)")

	args = vars(ap.parse_args())

	file_in = args["in"]
	out_dir = args["out"] or "output"
	
	if not os.path.exists(out_dir):
	    os.makedirs(out_dir)

	# TODO saldo_al

	estratto = EstrattoConto(file_in)

	estratto.entrate().to_csv(os.path.join(out_dir, "entrate.csv"))
	estratto.entrate(group_causale=True).to_csv(os.path.join(out_dir, "entrate_causale.csv"))
	estratto.uscite().to_csv(os.path.join(out_dir, "uscite.csv"))
	estratto.uscite(group_causale=True).to_csv(os.path.join(out_dir, "uscite_causale.csv"))
	
	estratto.mensili().to_csv(os.path.join(out_dir, "mensili.csv"))

	estratto.bonifici().to_csv(os.path.join(out_dir, "bonifici.csv"))

	estratto.disposizioni().to_csv(os.path.join(out_dir, "disposizioni.csv"))

if __name__ == '__main__':
	main()