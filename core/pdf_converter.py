"""
Modulo per la conversione di progetti in documenti PDF
"""

import os
import subprocess
import sys
from pathlib import Path
from fpdf import FPDF
from core.file_manager import FileManager
from core.config import SUPPORTED_ENCODINGS, MAX_LINE_WIDTH

class PDFConverter:
    """Gestisce la conversione di progetti in PDF"""
    
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.file_manager = FileManager()
        # Crea la cartella Saved all'inizializzazione
        self._ensure_saved_directory()
    
    def _ensure_saved_directory(self):
        """Crea la cartella Saved se non esiste"""
        saved_dir = Path("Saved")
        saved_dir.mkdir(exist_ok=True)
    
    def _get_saved_pdf_path(self, project_path, custom_output_path=None):
        """Restituisce il percorso del PDF nella cartella Saved"""
        if custom_output_path:
            return custom_output_path
        
        project_name = Path(project_path).name
        pdf_filename = f"{project_name}_Snapshot.pdf"
        return Path("Saved") / pdf_filename
    
    def _open_pdf(self, pdf_path):
        """Apre il PDF con il visualizzatore predefinito del sistema"""
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return False
            
            if sys.platform == "win32":
                # Windows
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                # macOS
                subprocess.run(["open", pdf_path])
            else:
                # Linux
                subprocess.run(["xdg-open", pdf_path])
            return True
        except Exception as e:
            print(f"Errore nell'apertura del PDF: {e}")
            return False
    
    def _scan_project_exclusions(self, project_path):
        """Scansiona il progetto per trovare le esclusioni effettivamente presenti"""
        project_path = Path(project_path)
        found_exclusions = {
            'dirs': set(),
            'files': set(),
            'extensions': set()
        }
        
        # Scansiona tutte le directory per trovare quelle escluse effettivamente presenti
        for dir_path in project_path.rglob('*'):
            if dir_path.is_dir():
                relative_dir = dir_path.relative_to(project_path)
                if self.file_manager.should_exclude(dir_path, relative_dir):
                    # Trova il componente directory che corrisponde a un'esclusione
                    for excluded_dir in self.file_manager.excluded_dirs:
                        if excluded_dir in str(relative_dir).split(os.sep):
                            found_exclusions['dirs'].add(excluded_dir)
        
        # Scansiona tutti i file per trovare esclusioni effettive
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_path)
                
                # Controlla esclusione per nome file
                if file_path.name in self.file_manager.excluded_files:
                    found_exclusions['files'].add(file_path.name)
                
                # Controlla esclusione per estensione
                file_ext = file_path.suffix.lower()
                if file_ext in self.file_manager.excluded_extensions:
                    found_exclusions['extensions'].add(file_ext)
                
                # Controlla pattern con wildcard
                for pattern in self.file_manager.excluded_files:
                    if '*' in pattern:
                        import fnmatch
                        if fnmatch.fnmatch(file_path.name, pattern):
                            found_exclusions['files'].add(pattern)
        
        return found_exclusions
    
    def create_project_pdf(self, project_path, output_pdf=None, custom_exclusions=None, 
                          progress_callback=None, include_excluded=False, open_after_creation=True):
        """Crea un PDF dal progetto"""
        # Applica esclusioni personalizzate
            # REINIZIALIZZA il PDF ogni volta per evitare accumulo di pagine
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        if custom_exclusions:
            self.file_manager.update_exclusions(**custom_exclusions)
        
        project_path = Path(project_path)
        
        if not project_path.exists():
            raise ValueError(f"La cartella '{project_path}' non esiste.")
        
        # Determina il percorso di output (usa sempre la cartella Saved)
        final_output_pdf = self._get_saved_pdf_path(project_path, output_pdf)
        
        # Scansiona il progetto per trovare esclusioni effettive
        actual_exclusions = self._scan_project_exclusions(project_path)
        
        # Conta i file totali
        if include_excluded:
            # Se include_excluded è True, conta tutti i file
            total_files = sum(1 for _ in project_path.rglob('*') if _.is_file())
        else:
            # Altrimenti conta solo i file non esclusi
            total_files = self.file_manager.count_project_files(project_path)     
        
        processed_count = 0
        
        # Pagina titolo
        self._add_title_page(project_path, final_output_pdf, include_excluded, actual_exclusions)
        
        # Elenco file processati
        processed_files = []
        excluded_files_found = []
        
        # Processa tutti i file
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_path)
                
                is_excluded = self.file_manager.should_exclude(file_path, relative_path)
                
                if include_excluded or not is_excluded:
                    # Se include_excluded è True, aggiungi tutti i file
                    # Se include_excluded è False, aggiungi solo i file non esclusi
                    self._add_file_to_pdf(file_path, relative_path)
                    processed_files.append(str(relative_path))
                else:
                    # Registra i file esclusi trovati (per debug/informazioni)
                    excluded_files_found.append(str(relative_path))

                # Aggiorna il progresso
                processed_count += 1
                if progress_callback:
                    progress_callback(processed_count, total_files)
        
        # Salva il PDF
        self.pdf.output(final_output_pdf)
        
        # Apri il PDF dopo la creazione se richiesto
        if open_after_creation:
            self._open_pdf(final_output_pdf)
        
        return len(processed_files), str(final_output_pdf)
    
    def _add_title_page(self, project_path, output_pdf, include_excluded, actual_exclusions):
        """Aggiunge la pagina titolo al PDF"""
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 20)
        self.pdf.cell(0, 20, "DOCUMENTAZIONE PROGETTO PYTHON", ln=True, align='C')
        self.pdf.ln(10)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f'Progetto: {project_path.name}', ln=True)
        self.pdf.cell(0, 10, f'Cartella: {project_path.absolute()}', ln=True)
        self.pdf.cell(0, 10, f'PDF salvato in: {output_pdf}', ln=True)
        self.pdf.cell(0, 10, f'File esclusi inclusi: {"SI" if include_excluded else "NO"}', ln=True)
        self.pdf.ln(10)
        
        # Aggiungi informazioni sulle esclusioni SOLO se stiamo includendo i file esclusi
        if include_excluded:
            self._add_exclusions_info(actual_exclusions)
    
    def _add_exclusions_info(self, actual_exclusions):
        """Aggiunge informazioni sulle esclusioni EFFETTIVE trovate nel progetto"""
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, "ESCLUSIONI APPLICATE (trovate nel progetto):", ln=True)
        self.pdf.ln(5)
    
        # Cartelle escluse trovate
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, "Cartelle escluse:", ln=True)
        self.pdf.set_font('Arial', '', 10)
    
        if actual_exclusions['dirs']:
            for excluded_dir in sorted(actual_exclusions['dirs']):
                self.pdf.cell(0, 5, f" - {excluded_dir}", ln=True)
        else:
            self.pdf.cell(0, 5, "Nessuna cartella esclusa trovata nel progetto", ln=True)
        
        self.pdf.ln(5)
        
        # Estensioni escluse trovate
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, "Estensioni escluse:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        
        if actual_exclusions['extensions']:
            for excluded_ext in sorted(actual_exclusions['extensions']):
                self.pdf.cell(0, 5, f" - {excluded_ext}", ln=True)
        else:
            self.pdf.cell(0, 5, "Nessuna estensione esclusa trovata nel progetto", ln=True)
        
        self.pdf.ln(5)
        
        # File esclusi trovati
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, "File esclusi:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        
        if actual_exclusions['files']:
            for excluded_file in sorted(actual_exclusions['files']):
                self.pdf.cell(0, 5, f" - {excluded_file}", ln=True)
        else:
            self.pdf.cell(0, 5, "Nessun file escluso trovato nel progetto", ln=True)
        
        self.pdf.ln(10)
    
    
    def _add_file_to_pdf(self, file_path, relative_path):
        """Aggiunge un file al PDF"""
        try:
            # Leggi il contenuto del file
            content = self._read_file_content(file_path)

            # Pulisci il testo
            content = self._clean_text(content)
            relative_path_str = self._clean_text(str(relative_path))

            # Controlla se il contenuto è vuoto
            if not content.strip():
                # Se il file è vuoto, aggiungi solo l'intestazione
                self.pdf.add_page()
                self.pdf.set_font('Arial', 'B', 14)
                self.pdf.cell(0, 10, f'File: {relative_path_str}', ln=True)
                self.pdf.ln(5)
                self.pdf.set_font('Arial', '', 10)
                self.pdf.cell(0, 10, 'File vuoto', ln=True)
                return

            # Aggiungi una nuova pagina SOLO se necessario
            # Controlla se c'è spazio sufficiente nella pagina corrente
            current_y = self.pdf.get_y()
            page_height = self.pdf.h - 2 * self.pdf.b_margin
            
            # Stima dell'altezza necessaria: intestazione (20) + spazio (10) + almeno 5 righe (20)
            estimated_height = 50
            
            if current_y + estimated_height > page_height:
                self.pdf.add_page()
            
            # Intestazione del file
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.cell(0, 10, f'File: {relative_path_str}', ln=True)
            self.pdf.ln(5)

            # Contenuto del file
            self.pdf.set_font('Courier', '', 8)

            # Dividi il contenuto in linee
            lines = content.split('\n')
            line_height = 4
            
            for i, line in enumerate(lines, 1):
                clean_line = self._clean_text(line)
                
                # Controlla se serve una nuova pagina
                current_y = self.pdf.get_y()
                if current_y + line_height > page_height:
                    self.pdf.add_page()
                    # Ripristina il font dopo l'aggiunta della pagina
                    self.pdf.set_font('Courier', '', 8)

                if len(clean_line) <= MAX_LINE_WIDTH:
                    # Linea normale
                    line_number = f'{i:4d}|'
                    self.pdf.set_font('Courier', '', 8)
                    self.pdf.cell(len(line_number) * 1.5, line_height, line_number)
                    self.pdf.cell(0, line_height, clean_line, ln=True)
                else:
                    # Linea lunga - dividi in più righe
                    line_number = f'{i:4d}|'
                    indent_spaces = " " * len(line_number)

                    # Prima parte
                    first_segment = clean_line[:MAX_LINE_WIDTH]
                    self.pdf.set_font('Courier', '', 8)
                    self.pdf.cell(len(line_number) * 1.5, line_height, line_number)
                    self.pdf.cell(0, line_height, first_segment, ln=True)

                    # Parti successive
                    remaining_text = clean_line[MAX_LINE_WIDTH:]
                    while remaining_text:
                        # Controlla se serve nuova pagina
                        current_y = self.pdf.get_y()
                        if current_y + line_height > page_height:
                            self.pdf.add_page()
                            self.pdf.set_font('Courier', '', 8)
                        
                        segment_width = MAX_LINE_WIDTH - len(line_number) + 3
                        if len(remaining_text) > segment_width:
                            segment = remaining_text[:segment_width]
                            remaining_text = remaining_text[segment_width:]
                        else:
                            segment = remaining_text
                            remaining_text = ""
                        
                        self.pdf.set_font('Courier', '', 8)
                        self.pdf.cell(len(line_number) * 1.5, line_height, indent_spaces)
                        self.pdf.cell(0, line_height, segment, ln=True)

            self.pdf.ln(5)

        except Exception as e:
            # In caso di errore, aggiungi un messaggio di errore
            self.pdf.add_page()
            self.pdf.set_font('Arial', 'B', 14)
            self.pdf.cell(0, 10, f'File: {relative_path}', ln=True)
            self.pdf.ln(5)
            self.pdf.set_font('Arial', '', 10)
            self.pdf.cell(0, 10, f'Errore nella lettura del file: {str(e)}', ln=True)
    
    def _read_file_content(self, file_path):
        """Legge il contenuto del file provando diverse codifiche"""
        for encoding in SUPPORTED_ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except (UnicodeDecodeError, Exception):
                continue
        
        # Se nessuna codifica funziona, restituisci messaggio di errore
        return f'Impossibile leggere il file {file_path} - formato binario o codifica sconosciuta'
    
    def _clean_text(self, text):
        """Pulisce il testo per la compatibilità PDF"""
        try:
            text.encode('latin-1')
            return text
        except UnicodeEncodeError:
            cleaned_text = text.encode('latin-1', errors='replace').decode('latin-1')
            return cleaned_text