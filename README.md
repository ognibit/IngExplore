# IngCsv
Un programma per elaborare i movimenti dei conti ING Direct nel formato CSV, versione italiana.

## Scaricare i Dati
Dal sito ing.it, nella pagina Movimenti del Conto Corrente, si può fare la ricerca dei movimenti.
In basso a destra c'è il link "Scarica Foglio di Calcolo" che permette di scaricare un excel denominato "MovimentiContoCorrenteArancio.xls". 

Aprendo il file con Excel o Calc, selezionate la tabella senza però includere le ultime righe di riepilogo. 
Copiate la selezione in un nuovo foglio e salvatelo come CSV, usando come delimitatore il carattere virgola.

Questo file è pronto per venire elaborato dal programma.

### Attenzione
Da varie prove fatte risulta che l'export non esporta tutta la ricerca, meglio non superare il quadrimestre.

## Installazione
Per poter esegurie il programma serve avere installato sul PC l'interprete Python, almeno versione 3.6. Servono poi le librerie:
- pandas
- numpy

## Esecuzione
L'esecuzione del programma avviene da linea di comando.
Il programma prende in input il file CSV dei movimenti e crea una cartella con dentro le varie elaborazioni:
- **entrate.csv**: tutte le entrate
- **entrate_causale.csv**: le entrate raggruppate per causale
- **uscite.csv**: tutte le uscite
- **uscite_causale.csv**: le uscite raggruppate per causale
- **mensili.csv**: causali in riga, mesi in colonna e totali. Una vista completa per un bilancio.
- **bonifici.csv**: il dettaglio dei bonifici, con estrazione dell'ordinante e della nota.
- **disposizioni.csv**: il dettaglio delle disposizioni, con estrazione della nota.

```python ingcsv.py --in /tmp/ing_2018.csv --out /tmp/2018```