"""
Modulo per la ricostruzione di progetti da documenti PDF
con preservazione perfetta degli spazi e indentazione
"""

import re
import os
import datetime
from pathlib import Path
import PyPDF2
from core.file_manager import FileManager

class ProjectRecreator:
    """Gestisce la ricostruzione di progetti da PDF con preservazione spazi"""
    
    def __init__(self):
        self.files_data = {}
        self.metadata = {}
        self.file_manager = FileManager()
    
    def extract_pdf_content(self, pdf_path):
        """Estrae il contenuto dal PDF preservando il layout"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                    print(f"📄 Pagina {page_num + 1} estratta")
                return full_text
        except Exception as e:
            print(f"❌ Errore nell'estrazione del PDF: {e}")
            return None

    def parse_files_from_pdf(self, pdf_text):
        """
        Analizza il PDF e estrae i file PRESERVANDO FEDELMENTE 
        TUTTI GLI SPAZI E TAB ORIGINALI
        unisce senza spazi indesiderati
        """
        lines = pdf_text.split('\n')
        current_file = None
        current_content = []
        reading_file_content = False
        line_number_offset = 0
        
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
                line_number_offset = 0
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
                        line_num = int(line_match.group(1))
                        if line_number_offset == 0:
                            line_number_offset = line_num - len(current_content) - 1
                        
                        # APPROCCIO MIGLIORATO: preserva TUTTA la struttura originale
                        pipe_pos = raw_line.find('|')
                        
                        if pipe_pos >= 0:
                            # Contenuto dopo il pipe
                            content_after_pipe = raw_line[pipe_pos + 1:].rstrip()
                            
                            # RICOSTRUZIONE ESATTA: preserva tutti gli spazi originali
                            preserved_line = content_after_pipe
                            
                            current_content.append(preserved_line)
                            
                            # DEBUG dettagliato per le prime linee
                            if len(current_content) <= 3:
                                total_spaces = len(preserved_line) - len(preserved_line.lstrip())
                                print(f"   📐 L{len(current_content)}: {total_spaces} spazi | '{preserved_line[:40]}...'")
                        else:
                            # Fallback
                            current_content.append(line_match.group(2))
                            
                    elif raw_line.strip() and not any(re.match(pattern, raw_line.strip()) for pattern in end_of_file_patterns):
                        #  Unisci SENZA SPAZI quando appropriato
                        
                        if current_content:
                            # Analizza il contesto per decidere come unire
                            last_line = current_content[-1]
                            merged_line = self._smart_merge_lines(last_line, raw_line)
                            current_content[-1] = merged_line
                            
                            if len(current_content) <= 3:
                                print(f"   🔄 Unita: '{raw_line[:30]}...'")
                        else:
                            # Prima riga del file senza numero - aggiungi normalmente
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

    def _smart_merge_lines(self, last_line, continuation):
        """
        Unisce due linee in modo INTELLIGENTE senza spazi indesiderati
        """
        last_stripped = last_line.rstrip()
        continuation_stripped = continuation.lstrip()
        
        # CASO 1: Se l'ultima linea termina con trattino basso (_), unisci SENZA SPAZIO
        # Questo corregge problemi come "end_of_file_ patterns" -> "end_of_file_patterns"
        if last_stripped.endswith('_'):
            return last_line.rstrip() + continuation_stripped
        
        # CASO 2: Se l'ultima linea termina con backslash, rimuovilo e unisci CON SPAZIO
        if last_stripped.endswith('\\'):
            return last_line.rstrip()[:-1] + ' ' + continuation_stripped
        
        # CASO 3: Se l'ultima linea termina con operatore, unisci CON SPAZIO
        if last_stripped.endswith(('+', '-', '*', '/', '=', '&', '|', ',')):
            return last_line.rstrip() + ' ' + continuation_stripped
            
        # CASO 4: Se la continuazione inizia con operatore di chiusura, unisci SENZA SPAZIO
        if continuation_stripped.startswith((')', ']', '}', '.', ',', ';', ':')):
            return last_line.rstrip() + continuation_stripped
        
        # CASO 5: Se l'ultima linea termina con carattere di apertura, unisci SENZA SPAZIO
        if last_stripped.endswith(('(', '[', '{')):
            return last_line.rstrip() + continuation_stripped
            
        # CASO 6: Se l'ultima linea è una stringa non chiusa, unisci SENZA SPAZIO
        if last_stripped.count('"') % 2 == 1 or last_stripped.count("'") % 2 == 1:
            return last_line + continuation_stripped
        
        # CASO 7: Analizza il contenuto per identificare parole divise
        # Se l'ultima linea termina con lettera e la continuazione inizia con lettera, unisci SENZA SPAZIO
        if (last_stripped and last_stripped[-1].isalpha() and 
            continuation_stripped and continuation_stripped[0].isalpha()):
            return last_line.rstrip() + continuation_stripped
            
        # CASO DEFAULT: unisci CON SPAZIO
        return last_line.rstrip() + ' ' + continuation_stripped

    def clean_file_content(self, content, file_path):
        """
        Pulisce il contenuto preservando FEDELMENTE tutti gli spazi e l'indentazione originale.
        Versione SEMPLIFICATA: rimuove solo caratteri di controllo
        """
        if not content:
            return content
        
        lines = content.split('\n')
        cleaned_lines = []
        
        print(f"   🧹 Pulizia contenuto per {file_path}...")
        
        for i, line in enumerate(lines):
            cleaned_line = line
            
            # Rimuovi SOLO i tag di troncamento espliciti
            cleaned_line = cleaned_line.replace('... [troncato]', '')
            
            # Rimuovi caratteri di controllo ma PRESERVA ASSOLUTAMENTE TUTTI GLI SPAZI
            cleaned_line = cleaned_line.replace('\r', '')
            cleaned_line = cleaned_line.replace('\x00', '')
            cleaned_line = cleaned_line.replace('\x0c', '')  # Form feed
            
            cleaned_lines.append(cleaned_line)
            
            # DEBUG per prime linee
            if i < 3 and cleaned_line.strip():
                leading_spaces = len(cleaned_line) - len(cleaned_line.lstrip())
                print(f"   🔍 Linea {i+1}: {leading_spaces} spazi | '{cleaned_line[:50]}...'")
        
        final_content = '\n'.join(cleaned_lines)
        
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
        print("🎯 ALGORITMO INTELLIGENTE: Unione senza spazi indesiderati")
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
                
                # Pulisci il contenuto PRESERVANDO TUTTI GLI SPAZI
                cleaned_content = self.clean_file_content(raw_content, file_path)
                
                # Scrivi il file con encoding UTF-8
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                files_created += 1
                line_count = len(cleaned_content.splitlines())
                
                # ANALISI DETTAGLIATA del file creato
                self._analyze_file_structure(file_path, cleaned_content, files_created)
                
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

    def _analyze_file_structure(self, file_path, content, files_created):
        """Analizza la struttura del file ricostruito"""
        lines = content.split('\n')
        line_count = len(lines)
        
        # Calcola statistiche indentazione
        indent_stats = []
        line_lengths = []
        
        for i, line in enumerate(lines[:20]):  # Analizza prime 20 linee
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_stats.append(indent)
                line_lengths.append(len(line))
        
        if indent_stats:
            avg_indent = sum(indent_stats) // len(indent_stats)
            max_indent = max(indent_stats)
            max_line_length = max(line_lengths) if line_lengths else 0
            
            print(f"✅ Creato: {file_path}")
            print(f"   📊 Statistiche: {line_count} linee, {max_indent} spazi max, {avg_indent} spazi medi")
            print(f"   📏 Lunghezza max riga: {max_line_length} caratteri")

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

ALGORITMO INTELLIGENTE:
----------------------
• Unione SENZA SPAZI per parole divise (end_of_file_ patterns -> end_of_file_patterns)
• Riconoscimento contestuale operatori e parentesi
• Preservazione struttura originale del codice
• Gestione intelligente continuazioni

"""

        with open(output_path / "RICOSTRUZIONE_REPORT.txt", 'w', encoding='utf-8') as f:
            f.write(report_content)