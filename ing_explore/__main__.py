"""ing_explore
CLI interface for the AccountStatements.
Use --help to see the usage.
"""

import os
import argparse
from datetime import datetime
from . import AccountStatements, read_csv, read_xlsx, __version__
import matplotlib.pyplot as plt

def _to_csv_files(statements, out_dir):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	statements.incomes().to_csv(os.path.join(out_dir, "incomes.csv"))
	statements.incomes(group_types=True).to_csv(os.path.join(out_dir, "incomes_groups.csv"))
	statements.expenses().to_csv(os.path.join(out_dir, "expenses.csv"))
	statements.expenses(group_types=True).to_csv(os.path.join(out_dir, "expenses_groups.csv"))
	
	statements.month_amounts().to_csv(os.path.join(out_dir, "months.csv"))

	statements.transfers().to_csv(os.path.join(out_dir, "transfers.csv"))

	statements.operations().to_csv(os.path.join(out_dir, "operations.csv"))

def _to_images(statements, out_dir, start_balance):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	df, ax = statements.month_chart(start_balance=start_balance)
	ax.figure.savefig(os.path.join(out_dir, "months.png"))
	

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--in", "-i", required=True, help="The input file CSV o XLSX")
	ap.add_argument("--out", "-o", required=False, help="The output directory")
	ap.add_argument("--balance_at", "-ba", required=False, help="Calculate the balance at the day. Format dd/mm/yyyy (es: 05/03/2019)")
	ap.add_argument("--start_balance", "-sb", required=False, help="Set the initial balance.")
	ap.add_argument("--giro", "-g", required=False, action='store_true', help="Include the internal transfers")
	ap.add_argument("-v", "--version", action="version", version=f"{__package__} v{__version__}")

	args = vars(ap.parse_args())

	file_in = args["in"]
	out_dir = args["out"] or "output"
	include_giro = args["giro"]	
	balance_at = args["balance_at"]
	start_balance = float( args["start_balance"] or "0" )
	
	_, extension = os.path.splitext(file_in)

	if extension == '.csv':
		df = read_csv(file_in)
	elif extension == '.xlsx':
		df = read_xlsx(file_in)
	else:
		raise ValueError("Only .csv or .xlsx extension allowed")

	statements = AccountStatements(df, giro=include_giro)

	if balance_at is not None:
		date_balance = datetime.strptime(balance_at, "%d/%m/%Y")		
		balance = statements.balance_at(date_balance)
		balance = balance + start_balance
		print(balance.round(2))
	else:		
		_to_csv_files(statements, out_dir)
		_to_images(statements, out_dir, start_balance)

if __name__ == '__main__':
	main()