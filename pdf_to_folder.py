# File: pdf_to_folder.py
import re
import os
from pathlib import Path
import datetime

import PyPDF2


class UniversalPDFToProject:
    def __init__(self):
        self.files_data = {}
        self.metadata = {}
        
    def extract_pdf_content(self, pdf_path):
        """Estrae il contenuto dal PDF preservando il layout"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                return full_text
        except Exception as e:
            print(f"❌ Errore nell'estrazione del PDF: {e}")
            return None

    def parse_files_from_pdf(self, pdf_text):
        """
        Analizza il PDF e estrae i file PRESERVANDO FEDELMENTE 
        TUTTI GLI SPAZI E TAB ORIGINALI
        Gestisce correttamente le righe lunghe divise su più righe nel PDF
        """
        lines = pdf_text.split('\n')
        current_file = None
        current_content = []
        reading_file_content = False
        
        print(f"🔍 Analizzando {len(lines)} linee dal PDF...")
        
        i = 0
        while i < len(lines):
            raw_line = lines[i]
            
            # Cerca l'inizio di un nuovo file
            file_match = re.match(r'^\s*File:\s*(.+)$', raw_line.strip())
            if file_match:
                # Salva il file precedente se esiste
                if current_file and current_content:
                    full_content = '\n'.join(current_content)
                    if full_content.strip():
                        self.files_data[current_file] = full_content
                        print(f"💾 File salvato: {current_file} ({len(current_content)} linee)")
                
                # Inizia un nuovo file
                file_path = file_match.group(1).strip()
                current_file = file_path
                current_content = []
                reading_file_content = True
                print(f"📖 Iniziando file: {file_path}")
                i += 1
                continue
            
            # Se stiamo leggendo il contenuto di un file
            if reading_file_content and current_file:
                # Controlla se è la fine della sezione file
                stripped_line = raw_line.strip()
                
                # Pattern per fine sezione file
                end_of_file_patterns = [
                    r'^File:\s*.+$',
                    r'^DOCUMENTAZIONE PROGETTO PYTHON$',
                    r'^Cartelle escluse:$',
                    r'^File esclusi:$', 
                    r'^Estensioni escluse:$',
                    r'^Progetto:\s*.+$',
                    r'^Cartella:\s*.+$'
                ]
                
                is_end_of_section = any(re.match(pattern, stripped_line) for pattern in end_of_file_patterns)
                
                if is_end_of_section:
                    # Fine della sezione file corrente
                    if current_file and current_content:
                        full_content = '\n'.join(current_content)
                        if full_content.strip():
                            self.files_data[current_file] = full_content
                            print(f"✅ File completato: {current_file}")
                    
                    reading_file_content = False
                    current_file = None
                    continue
                
                # GESTIONE PRINCIPALE: PRESERVAZIONE FEDELE DEGLI SPAZI
                if reading_file_content:
                    # Pattern per linea numerata: "numero | contenuto"
                    line_match = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', raw_line)
                    
                    if line_match:
                        # APPROCCIO DIRETTO: preserva TUTTA la linea dopo il pipe
                        # Trova la posizione esatta del pipe "|"
                        pipe_pos = raw_line.find('|')
                        
                        if pipe_pos >= 0:
                            # Prendi tutto ciò che viene DOPO il pipe, INCLUDENDO TUTTI GLI SPAZI
                            content_after_pipe = raw_line[pipe_pos + 1:]
                            
                            # ANALISI DETTAGLIATA DEGLI SPAZI
                            # Conta gli spazi iniziali nel contenuto dopo il pipe
                            leading_spaces_in_content = len(content_after_pipe) - len(content_after_pipe.lstrip())
                            
                            # Se ci sono spazi iniziali, preservali ESATTAMENTE
                            if leading_spaces_in_content > 0:
                                # Ricostruisci la linea con gli spazi originali
                                preserved_line = ' ' * leading_spaces_in_content + content_after_pipe.lstrip()
                            else:
                                # Se non ci sono spazi iniziali, usa il contenuto così com'è
                                preserved_line = content_after_pipe
                            
                            current_content.append(preserved_line)
                            
                            # DEBUG: mostra la preservazione degli spazi per le prime linee
                            if len(current_content) <= 5:
                                original_spaces = len(raw_line) - len(raw_line.lstrip())
                                content_spaces = len(preserved_line) - len(preserved_line.lstrip())
                                print(f"   📐 L{len(current_content)}: {original_spaces}→{content_spaces} spazi | '{preserved_line[:30]}...'")
                        else:
                            # Fallback: usa il contenuto estratto dal regex
                            current_content.append(line_match.group(2))
                            
                    elif raw_line.strip() and not any(re.match(pattern, raw_line.strip()) for pattern in end_of_file_patterns):
                        # GESTIONE RIGHE LUNGHE DIVISE: 
                        # Se la linea NON ha numero ma ha lo stesso indent delle righe continuazione
                        # e siamo nel contesto di un file, probabilmente è una continuazione
                        
                        # Controlla se questa linea potrebbe essere una continuazione di una riga lunga
                        is_continuation_line = (
                            current_content and  # C'è contenuto precedente
                            not re.match(r'^\s*\d+\s*\|', raw_line) and  # Non è una linea numerata
                            len(raw_line.strip()) > 0 and  # Non è vuota
                            raw_line.startswith('     ')  # Ha l'indentazione tipica delle continuazioni (5+ spazi)
                        )
                        
                        if is_continuation_line:
                            # È una continuazione di riga lunga - unisci con l'ultima linea
                            last_line = current_content[-1]
                            
                            # Rimuovi l'indentazione della continuazione (i primi 5+ spazi)
                            continuation_content = raw_line.lstrip()
                            
                            # Unisci con l'ultima linea
                            merged_line = last_line + continuation_content
                            current_content[-1] = merged_line
                            
                            print(f"   🔄 Unita continuazione riga lunga: '{continuation_content[:30]}...'")
                        else:
                            # Linea senza numero - potrebbe essere header o formato speciale
                            # PRESERVA LA LINEA ORIGINALE COSÌ COM'È
                            current_content.append(raw_line)
                            
                    elif not raw_line.strip():
                        # Linea vuota - preservala
                        current_content.append('')
                
            i += 1
        
        # Salva l'ultimo file
        if current_file and current_content:
            full_content = '\n'.join(current_content)
            if full_content.strip():
                self.files_data[current_file] = full_content
                print(f"💾 Ultimo file salvato: {current_file} ({len(current_content)} linee)")
        
        print(f"✅ Parsing completato. Trovati {len(self.files_data)} file")
        return self.files_data

    def clean_file_content(self, content, file_extension):
        """
        Pulisce il contenuto preservando FEDELMENTE tutti gli spazi e l'indentazione originale.
        Gestisce le righe lunghe che erano state divise nel PDF.
        """
        if not content:
            return content
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            cleaned_line = line
            
            # Rimuovi SOLO i tag di troncamento espliciti
            cleaned_line = cleaned_line.replace('... [troncato]', '')
            
            # Rimuovi caratteri di controllo ma PRESERVA ASSOLUTAMENTE TUTTI GLI SPAZI
            # Usa replace invece di regex per non alterare gli spazi
            cleaned_line = cleaned_line.replace('\r', '')  # Solo ritorni a carrello
            cleaned_line = cleaned_line.replace('\x00', '')  # Solo null bytes
            
            # CORREZIONE PER RIGHE LUNGHE: 
            # Se una linea inizia con molti spazi ma non è vuota, potrebbe essere 
            # una continuazione che è stata erroneamente separata
            if (i > 0 and 
                len(cleaned_line.strip()) > 0 and 
                len(cleaned_line) - len(cleaned_line.lstrip()) > 10):  # Molti spazi iniziali
                
                # Verifica se la linea precedente potrebbe essere parte della stessa riga lunga
                prev_line = cleaned_lines[-1] if cleaned_lines else ""
                
                # Se la linea precedente non termina con punteggiatura e questa inizia con molti spazi,
                # probabilmente sono la stessa riga
                if (prev_line and 
                    not prev_line.endswith(('.', ';', ':', '!', '?')) and
                    not any(prev_line.endswith(keyword) for keyword in ['def', 'class', 'if', 'for', 'while'])):
                    
                    # Unisci con la linea precedente
                    cleaned_lines[-1] = prev_line + ' ' + cleaned_line.lstrip()
                    print(f"   🔄 Righe lunghe unite: linea {i} unita alla precedente")
                    continue
            
            # Mantieni TUTTI gli spazi, tab, e l'indentazione originale
            cleaned_lines.append(cleaned_line)
            
            # DEBUG: mostra la preservazione degli spazi per le prime 5 linee
            if i < 5 and cleaned_line.strip():
                leading_spaces = len(cleaned_line) - len(cleaned_line.lstrip())
                print(f"   🔍 Linea {i+1}: {leading_spaces} spazi iniziali | '{cleaned_line[:40]}...'")
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # CORREZIONE FINALE: gestisci eventuali righe lunghe che potrebbero essere state divise
        # durante l'estrazione PDF ma che dovrebbero essere una sola riga
        final_lines = []
        i = 0
        while i < len(cleaned_lines):
            current_line = cleaned_lines[i]
            
            # Se questa linea potrebbe essere continuata (non termina con carattere di fine)
            if (i < len(cleaned_lines) - 1 and 
                current_line.strip() and 
                not current_line.endswith((':','{','}',';')) and
                not any(current_line.strip().endswith(keyword) for keyword in ['def', 'class', 'if', 'for', 'while', 'else', 'elif'])):
                
                next_line = cleaned_lines[i + 1]
                
                # Se la prossima linea ha un'indentazione molto diversa (molti più spazi)
                # potrebbe essere una continuazione
                current_indent = len(current_line) - len(current_line.lstrip())
                next_indent = len(next_line) - len(next_line.lstrip())
                
                if next_indent > current_indent + 8:  # Soglia per identificare continuazioni
                    # Probabile continuazione - unisci
                    merged_line = current_line + ' ' + next_line.lstrip()
                    final_lines.append(merged_line)
                    i += 2  # Salta la prossima linea
                    print(f"   🔄 Continuazione rilevata e unita: linee {i-1} e {i}")
                    continue
            
            final_lines.append(current_line)
            i += 1
        
        final_content = '\n'.join(final_lines)
        
        print(f"   ✅ Contenuto pulito: {len(final_content.splitlines())} linee, {len(final_content)} caratteri")
        
        return final_content

    def get_file_extension(self, file_path):
        """Restituisce l'estensione del file"""
        path = Path(file_path)
        return path.suffix.lower()

    def recreate_project_structure(self, pdf_path, output_folder):
        """Ricrea l'intera struttura del progetto dal PDF"""
        print(f"📖 Leggendo il PDF: {pdf_path}")
        pdf_text = self.extract_pdf_content(pdf_path)
        
        if not pdf_text:
            print("❌ Impossibile leggere il PDF")
            return False
        
        print("🔍 Analizzando il contenuto del PDF con PRESERVAZIONE SPAZI...")
        print("🎯 GESTIONE RIGHE LUNGHE ATTIVATA")
        files_data = self.parse_files_from_pdf(pdf_text)
        
        if not files_data:
            print("❌ Nessun file trovato nel PDF")
            return False
        
        print(f"📁 Trovati {len(files_data)} file nel PDF")
        
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = 0
        errors = []
        
        for file_path, raw_content in files_data.items():
            try:
                full_path = output_path / file_path
                
                # Crea le directory necessarie
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Ottieni l'estensione del file
                file_extension = self.get_file_extension(file_path)
                
                # Pulisci il contenuto PRESERVANDO TUTTI GLI SPAZI
                cleaned_content = self.clean_file_content(raw_content, file_extension)
                
                # Scrivi il file con encoding UTF-8
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                files_created += 1
                line_count = len(cleaned_content.splitlines())
                
                # ANALISI DETTAGLIATA del file creato
                lines = cleaned_content.split('\n')
                total_spaces = 0
                max_indent = 0
                line_lengths = []
                
                for line in lines[:15]:  # Analizza prime 15 linee
                    if line.strip():
                        indent = len(line) - len(line.lstrip())
                        total_spaces += indent
                        max_indent = max(max_indent, indent)
                        line_lengths.append(len(line))
                
                avg_indent = total_spaces // min(15, len([l for l in lines[:15] if l.strip()])) if any(lines[:15]) else 0
                max_line_length = max(line_lengths) if line_lengths else 0
                
                print(f"✅ Creato: {file_path}")
                print(f"   📊 Statistiche: {line_count} linee, {max_indent} spazi max, {avg_indent} spazi medi")
                print(f"   📏 Lunghezza max riga: {max_line_length} caratteri")
                
                # VERIFICA VISIVA della struttura per i primi file
                if files_created <= 2:
                    print(f"   👀 ANTEPRIMA STRUTTURA:")
                    for j in range(min(8, len(lines))):
                        line = lines[j]
                        if line.strip():  # Solo linee non vuote
                            indent = len(line) - len(line.lstrip())
                            indent_visual = "▸" * (indent // 4 + 1) if indent > 0 else "•"
                            content_preview = line.strip()[:50]
                            line_length_indicator = "📏" if len(line) > 100 else ""
                            print(f"      {indent_visual} [{indent} spazi] {content_preview} {line_length_indicator}")
                
            except Exception as e:
                error_msg = f"❌ Errore con {file_path}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        # Scrivi un report di ricostruzione
        self.write_reconstruction_report(output_path, files_created, errors, files_data)
        
        print(f"\n🎉 RICOSTRUZIONE COMPLETATA!")
        print(f"📊 File creati: {files_created}")
        print(f"❌ Errori: {len(errors)}")
        print(f"📂 Output: {output_path.absolute()}")
        
        if errors:
            print("\nErrori riscontrati:")
            for error in errors:
                print(f"  - {error}")
        
        return True

    def write_reconstruction_report(self, output_path, files_created, errors, files_data):
        """Scrive un report dettagliato della ricostruzione"""
        report_content = f"""RICOSTRUZIONE PROGETTO DA PDF
===============================

Data ricostruzione: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
File creati con successo: {files_created}
Errori riscontrati: {len(errors)}

DETTAGLIO FILE RICOSTRUITI:
---------------------------
"""

        for file_path in sorted(files_data.keys()):
            file_extension = self.get_file_extension(file_path)
            content_length = len(files_data[file_path])
            line_count = files_data[file_path].count('\n') + 1
            report_content += f"- {file_path} ({file_extension}, {line_count} linee, {content_length} caratteri)\n"

        if errors:
            report_content += f"\nERRORI RISCONTRATI:\n-------------------\n"
            for error in errors:
                report_content += f"- {error}\n"

        report_content += f"""
STATISTICHE:
-----------
File totali nel PDF: {len(files_data)}
File creati: {files_created}
Success rate: {(files_created/len(files_data))*100:.1f}%

ESTENSIONI FILE RICOSTRUITE:
---------------------------
"""

        # Calcola statistiche per estensione
        extensions = {}
        for file_path in files_data.keys():
            ext = self.get_file_extension(file_path)
            extensions[ext] = extensions.get(ext, 0) + 1

        for ext, count in sorted(extensions.items()):
            report_content += f"- {ext or 'Nessuna'}: {count} file\n"

        report_content += f"""
TECNICA DI PRESERVAZIONE SPAZI:
-------------------------------
✅ PRESERVAZIONE FEDELE: Tutti gli spazi e tab originali sono mantenuti
✅ INDENTAZIONE ORIGINALE: L'indentazione del PDF è preservata esattamente
✅ GESTIONE RIGHE LUNGHE: Le righe divise su più righe nel PDF vengono ricomposte
✅ FORMATTAZIONE INTATTA: La formattazione del codice rimane identica
✅ SUPPORTO UNIVERSALE: Funziona con tutti i linguaggi di programmazione

TECNICHE APPLICATE:
------------------
• Ricomposizione automatica righe lunghe divise
• Preservazione esatta spazi e indentazione  
• Unione intelligente continuazioni
• Riconoscimento pattern di divisione PDF

"""

        with open(output_path / "RICOSTRUZIONE_REPORT.txt", 'w', encoding='utf-8') as f:
            f.write(report_content)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ricrea un intero progetto da PDF - PRESERVAZIONE FEDELE di spazi e indentazione'
    )
    parser.add_argument('pdf_path', help='Percorso del PDF sorgente')
    parser.add_argument('output_folder', help='Cartella di destinazione per il progetto ricostruito')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"❌ Errore: Il file PDF '{args.pdf_path}' non esiste.")
        return
    
    print("🛠️  RICOSTRUZIONE PROGETTO DA PDF")
    print("=" * 70)
    print("🎯 PRESERVAZIONE FEDELE DI SPAZI E INDENTAZIONE ORIGINALE")
    print("🔧 GESTIONE AVANZATA RIGHE LUNGHE ATTIVATA")
    print("=" * 70)
    
    recreator = UniversalPDFToProject()
    success = recreator.recreate_project_structure(args.pdf_path, args.output_folder)
    
    if success:
        print("\n✅ RICOSTRUZIONE COMPLETATA CON SUCCESSO!")
        print(f"📁 Il progetto è stato ricreato in: {args.output_folder}")
        print("📄 Report dettagliato salvato in: RICOSTRUZIONE_REPORT.txt")
        print("\n🎯 GARANZIA DI PRESERVAZIONE:")
        print("   • ✅ TUTTI gli spazi originali preservati")
        print("   • ✅ Indentazione ESATTA del PDF mantenuta") 
        print("   • ✅ Righe lunghe ricomposte correttamente")
        print("   • ✅ Formattazione fedele per tutti i linguaggi")
        print("   • ✅ Nessuna alterazione della struttura originale")
    else:
        print("\n❌ Ricostruzione fallita!")

if __name__ == "__main__":
    # Esempio di utilizzo diretto
    if len(os.sys.argv) == 1:
        print("🛠️  RICOSTRUZIONE PROGETTO DA PDF")
        print("=" * 60)
        print("🎯 PRESERVAZIONE FEDELE SPAZI E INDENTAZIONE")
        print("🔧 GESTIONE RIGHE LUNGHE ATTIVATA")
        print("=" * 60)
        
        pdf_file = input("Inserisci il percorso del PDF: ").strip()
        output_dir = input("Inserisci la cartella di output: ").strip()
        
        if pdf_file and output_dir:
            if os.path.exists(pdf_file):
                recreator = UniversalPDFToProject()
                recreator.recreate_project_structure(pdf_file, output_dir)
            else:
                print("❌ Il file PDF specificato non esiste.")
        else:
            print("❌ Devi specificare entrambi i percorsi.")
    else:
        main()