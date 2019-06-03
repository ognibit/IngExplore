==========
Quickstart
==========
The module can be executed from command line.

Installation
---------------
You can install the module downloading the source code
::
    git clone https://github.com/ognibit/IngExplore.git
    cd IngExplore
    pip install -r requirements.txt

Run
----------
The module can be run as follow
::
    cd IngExplore
    python -m ing_explore --in <file_in> [options]

Export Analysis
---------------
You can get a bunch of files extracted and rationalized from the input one
::
    python -m ing_explore --in /tmp/ing_2018.xlsx --out /tmp/2018

Using the `--giro` (or `-g`) the transactions from and to your accounts are included into the exports, otherwise they are excluded by default.

After the exection you can find these files into the output directory:
    - **incomes.csv**: all the incomes.
    - **incomes_groups.csv**: the incomes grouped by type.
    - **expenses.csv**: all the expenses.
    - **expenses_groups.csv**: the expenses grouped by type.
    - **months.csv**: type on row, months on columns (plus total amounts).
    - **transfers.csv**: all the transfers, with sender and note extracted.
    - **operations.csv**: all the operations, with note extracted.
    - **months.png**: a bar chart with incomes, expenses and balance per motnhs. With the option `--start_balance` you can set the initial balance to get the actual values.

Balance At
----------
If you only want to know the balance at a day, you can use the following option
::
    python -m ing_expense --in /tmp/2018.xslx --balance_at 25/04/2019 --start_balance 1000.0
    1234.56

If you don't specify the starting balance, you get the relative balance starting from the first transaction.

The date are in the *DD/MM/YYYY* format.
