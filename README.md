# PySyncroNet - Advanced PDF Project Manager

## Descrizione del Progetto

**PySyncroNet** è un software innovativo sviluppato in **Python** che consente la **condivisione sicura di cartelle di progetto** (in particolare contenenti codice sorgente) attraverso una conversione completa in formato **PDF**. Successivamente, il progetto può essere **ricostruito integralmente** a partire dal PDF condiviso.

L'obiettivo è fornire un metodo universale, leggibile e portabile per trasferire, archiviare o condividere progetti software senza rischi legati a file binari, malware o incompatibilità di ambienti.

---

## Funzionalità Principali

* ✨ **Conversione Progetto → PDF**
  Trasforma un'intera cartella di progetto in un documento PDF unico, includendo automaticamente tutti i file di testo e codice, con numerazione delle righe e gestione intelligente delle esclusioni.

* 🔄 **Ricostruzione Progetto → Cartella**
  A partire da un PDF generato, PySyncroNet può ricostruire fedelmente la struttura del progetto originale, ripristinando file, sottocartelle e contenuti testuali.

* ⚙️ **Gestione Avanzata delle Esclusioni**
  Configurazione completa per ignorare file o directory indesiderate (es. *venv, .git, node_modules, immagini, file binari, ecc.*) durante la generazione del PDF.

* 🔍 **Interfaccia Grafica Moderna (GUI)**
  Interfaccia in **Tkinter** con tema scuro, schede multiple (Creazione PDF, Ricostruzione, Esclusioni, Impostazioni) e log dettagliati delle operazioni.

* ⏳ **Elaborazioni in Background**
  Operazioni eseguite tramite *threading*, per garantire fluidità e reattività dell'interfaccia.

* 🔒 **Sicurezza e Portabilità**
  I file binari vengono automaticamente esclusi, rendendo i PDF generati sicuri da condividere via e-mail, cloud o piattaforme pubbliche.

---

## Architettura del Software

PySyncroNet è composto da tre moduli principali:

### 1. `folder_to_pdf.py`

Gestisce la **conversione di un progetto in PDF**.

* Include ogni file leggibile (testo, codice, configurazioni, script)
* Pulisce caratteri non compatibili e gestisce codifiche multiple (UTF-8, Latin-1, ecc.)
* Supporta esclusioni personalizzate per directory, file e tipi di estensione

### 2. `pdf_to_folder.py`

Responsabile della **ricostruzione del progetto dal PDF**.

* Estrae il testo con PyPDF2 e ricrea ogni file nella sua posizione originale
* Corregge indentazione, formattazione e troncamenti
* Genera un report dettagliato di ricostruzione con statistiche ed eventuali errori

### 3. `syncroNet.py`

Il **cuore dell'applicazione GUI**, che integra le funzionalità di conversione e ricostruzione.

* Interfaccia utente multi-tab intuitiva e accessibile
* Gestione log, esportazione configurazioni e statistiche progetto
* Compatibilità con tutti i linguaggi di programmazione testuali (Python, JS, Java, C++, HTML, JSON, ecc.)

---

## Tecnologie Utilizzate

* **Linguaggio:** Python 3.8+
* **Librerie Principali:**

  * `tkinter` – Interfaccia grafica
  * `fpdf` – Generazione PDF
  * `PyPDF2` – Lettura ed estrazione PDF
  * `pathlib`, `os`, `re`, `threading` – Gestione file e threading

---

## Installazione

1. Clonare o scaricare il repository del progetto:

   ```bash
   git clone https://github.com/tuo-username/PySyncroNet.git
   cd PySyncroNet
   ```
2. Installare le dipendenze richieste:

   ```bash
   pip install fpdf PyPDF2
   ```
3. Avviare l'applicazione:

   ```bash
   python syncroNet.py
   ```

---

## Utilizzo

### 🔄 Conversione Progetto in PDF

1. Aprire l'applicazione
2. Selezionare la cartella del progetto da convertire
3. Definire (opzionalmente) le esclusioni
4. Premere **"Crea PDF"** per generare la documentazione del progetto

### 🔄 Ricostruzione Progetto da PDF

1. Selezionare il file PDF precedentemente generato
2. Scegliere la cartella di destinazione
3. Premere **"Ricrea Progetto"** per ricostruire la struttura originale

---

## Esempi d'Uso

### Da riga di comando:

```bash
python pdf_to_folder.py progetto.pdf progetto_ricostruito/
```

### Output atteso:

```
? Ricostruzione completata con successo!
? File creati: 128
? Report: RICOSTRUZIONE_REPORT.txt
```

---

## Vantaggi Principali

* Riduzione dei rischi di condivisione (niente file eseguibili o binari)
* Compatibilità cross-platform totale
* Archiviazione a lungo termine in formato PDF leggibile
* Ideale per backup, code review, audit o documentazione di progetti

---

## Licenza

Questo progetto è distribuito sotto licenza **MIT**.
Consulta il file `LICENSE` per ulteriori dettagli.

---

## Autore

**PySyncroNet** – creato da Sigma Development
Versione: **3.0 (Advanced PDF Project Manager)**
Data: Novembre 2025
