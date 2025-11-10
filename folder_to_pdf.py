# File: folder_to_pdf.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import sys
import webbrowser
from datetime import datetime
from fpdf import FPDF
import re


class PythonProjectToPDF:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.excluded_dirs = set()
        self.excluded_files = set()
        self.excluded_extensions = set()
        
    def should_exclude(self, file_path, relative_path):
        """Determina se un file o cartella dovrebbe essere escluso"""
        # Controlla se è una cartella esclusa
        if any(excluded_dir in str(relative_path).split(os.sep) for excluded_dir in self.excluded_dirs):
            return True
            
        # Controlla se è un file escluso
        if file_path.name in self.excluded_files:
            return True
            
        # Controlla l'estensione del file
        if file_path.suffix.lower() in self.excluded_extensions:
            return True
            
        return False
    
    def clean_text(self, text):
        """Pulisce il testo rimuovendo o sostituendo caratteri non compatibili con latin-1"""
        try:
            # Prova a codificare in latin-1 per verificare la compatibilità
            text.encode('latin-1')
            return text
        except UnicodeEncodeError:
            # Sostituisci i caratteri non compatibili
            cleaned_text = text.encode('latin-1', errors='replace').decode('latin-1')
            return cleaned_text
    
    def add_file_to_pdf(self, file_path, relative_path):
        """Aggiunge il contenuto di un file al PDF PRESERVANDO GLI SPAZI ORIGINALI"""
        try:
            # Prova diverse codifiche
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            
            if content is None:
                content = f"Impossibile leggere il file {file_path} - formato binario o codifica sconosciuta"
            
        except Exception as e:
            content = f"Errore nella lettura del file {file_path}: {str(e)}"
        
        # Pulisci il contenuto dai caratteri non compatibili
        content = self.clean_text(content)
        relative_path_str = self.clean_text(str(relative_path))
        
        # Aggiungi una nuova pagina per ogni file
        self.pdf.add_page()
        
        # Intestazione del file
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, f"File: {relative_path_str}", ln=True)
        self.pdf.ln(5)
        
        # Contenuto del file
        self.pdf.set_font('Courier', '', 8)  # Usa Courier per preservare spaziatura fissa
        
        # Dividi il contenuto in linee e aggiungi al PDF PRESERVANDO GLI SPAZI
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Pulisci ogni linea MA PRESERVA GLI SPAZI ORIGINALI
            clean_line = self.clean_text(line)
            
            # Gestione righe lunghe: dividi in più righe se necessario
            max_line_width = 100  # Larghezza massima approssimativa in caratteri
            
            if len(clean_line) <= max_line_width:
                # Linea normale - scrivi normalmente
                line_number = f"{i:4d} |"
                self.pdf.set_font('Courier', '', 8)
                self.pdf.cell(len(line_number) * 1.5, 4, line_number, ln=0)
                self.pdf.cell(0, 4, clean_line, ln=True)
            else:
                # Linea lunga - dividi in più righe
                line_number = f"{i:4d} |"
                indent_spaces = " " * len(line_number)  # Spazi per l'allineamento
                
                # Scrivi la prima parte con il numero di linea
                self.pdf.set_font('Courier', '', 8)
                self.pdf.cell(len(line_number) * 1.5, 4, line_number, ln=0)
                self.pdf.cell(0, 4, clean_line[:max_line_width], ln=True)
                
                # Dividi il resto della linea in segmenti
                remaining_text = clean_line[max_line_width:]
                while remaining_text:
                    # Prendi il prossimo segmento (leggermente più corto per lo spazio di indentazione)
                    segment_width = max_line_width - len(line_number) + 3
                    if len(remaining_text) > segment_width:
                        segment = remaining_text[:segment_width]
                        remaining_text = remaining_text[segment_width:]
                    else:
                        segment = remaining_text
                        remaining_text = ""
                    
                    # Scrivi il segmento con l'indentazione
                    self.pdf.set_font('Courier', '', 8)
                    self.pdf.cell(len(line_number) * 1.5, 4, indent_spaces, ln=0)
                    self.pdf.cell(0, 4, segment, ln=True)
        
        self.pdf.ln(5)

    def count_files(self, project_path):
        """Conta il numero totale di file che verranno processati"""
        project_path = Path(project_path)
        count = 0
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_path)
                if not self.should_exclude(file_path, relative_path):
                    count += 1
        return count

    def create_pdf(self, project_path, output_pdf="project_Snapshot.pdf", custom_exclusions=None, progress_callback=None):
        """Crea il PDF dalla cartella del progetto"""       
        # Applica le esclusioni
        if custom_exclusions:
            if 'dirs' in custom_exclusions:
                self.excluded_dirs.update(custom_exclusions['dirs'])
            if 'files' in custom_exclusions:
                self.excluded_files.update(custom_exclusions['files'])
            if 'extensions' in custom_exclusions:
                self.excluded_extensions.update(custom_exclusions['extensions'])
        
        project_path = Path(project_path)
        
        total_files = self.count_files(project_path)
        processed_count = 0
        
        if not project_path.exists():
            raise ValueError(f"La cartella '{project_path}' non esiste.")
        
        # Pagina titolo
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 20)
        self.pdf.cell(0, 20, "DOCUMENTAZIONE PROGETTO PYTHON", ln=True, align='C')
        self.pdf.ln(10)
        
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f"Progetto: {project_path.name}", ln=True)
        self.pdf.cell(0, 10, f"Cartella: {project_path.absolute()}", ln=True)
        self.pdf.ln(10)
        
        # Trova le esclusioni effettivamente applicate al progetto
        applied_excluded_dirs = set()
        applied_excluded_files = set()
        
        # Scansiona il progetto per trovare quali esclusioni sono effettivamente applicate
        for item_path in project_path.rglob('*'):
            if item_path.is_file():
                relative_path = item_path.relative_to(project_path)
                
                # Controlla se il file sarebbe escluso
                if self.should_exclude(item_path, relative_path):
                    relative_parts = str(relative_path).split(os.sep)
                    
                    # Controlla esclusione per cartella
                    for excluded_dir in self.excluded_dirs:
                        if excluded_dir in relative_parts:
                            applied_excluded_dirs.add(excluded_dir)
                    
                    # Raggruppa TUTTI i file esclusi (sia per nome che per estensione)
                    excluded_reason = ""
                    
                    # File escluso per nome specifico
                    if item_path.name in self.excluded_files:
                        excluded_reason = f"{item_path.name} (file escluso)"
                        applied_excluded_files.add(excluded_reason)
                    
                    # File escluso per estensione
                    elif item_path.suffix.lower() in self.excluded_extensions:
                        excluded_reason = f"{relative_path} (estensione {item_path.suffix.lower()})"
                        applied_excluded_files.add(excluded_reason)
                    
                    # File escluso per essere in cartella esclusa
                    else:
                        for excluded_dir in self.excluded_dirs:
                            if excluded_dir in relative_parts:
                                excluded_reason = f"{relative_path} (cartella {excluded_dir})"
                                applied_excluded_files.add(excluded_reason)
                                break
        
        # Informazioni sulle esclusioni APPLICATE
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, "Cartelle escluse:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        
        if applied_excluded_dirs:
            for excluded_dir in sorted(applied_excluded_dirs):
                self.pdf.cell(0, 5, f"  - {excluded_dir}", ln=True)
        else:
            self.pdf.cell(0, 5, "  Nessuna cartella esclusa trovata nel progetto", ln=True)
        
        self.pdf.ln(5)
        
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, "Estensioni escluse:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        
        # Mostra solo le estensioni escluse che sono state effettivamente trovate
        found_extensions = set()
        for excluded_item in applied_excluded_files:
            if "(estensione" in excluded_item:
                # Estrae l'estensione dalla stringa
                ext_start = excluded_item.find("(estensione ") + 12
                ext_end = excluded_item.find(")", ext_start)
                extension = excluded_item[ext_start:ext_end]
                found_extensions.add(extension)
        
        if found_extensions:
            for excluded_ext in sorted(found_extensions):
                self.pdf.cell(0, 5, f"  - {excluded_ext}", ln=True)
        else:
            self.pdf.cell(0, 5, "  Nessuna estensione esclusa trovata nel progetto", ln=True)
        
        self.pdf.ln(5)
        
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, "File esclusi:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        
        if applied_excluded_files:
            for excluded_file in sorted(applied_excluded_files):
                self.pdf.cell(0, 5, f"  - {excluded_file}", ln=True)
        else:
            self.pdf.cell(0, 5, "  Nessun file escluso trovato nel progetto", ln=True)
        
        self.pdf.ln(10)
        
        # Elenco dei file processati
        processed_files = []
        
        # Cerca ricorsivamente tutti i file
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_path)
                
                if not self.should_exclude(file_path, relative_path):
                    processed_files.append(str(relative_path))
                    self.add_file_to_pdf(file_path, relative_path)
                    
                    # Aggiorna il progresso
                    processed_count += 1
                    if progress_callback:
                        progress_callback(processed_count, total_files)
        
        # Salva il PDF
        self.pdf.output(output_pdf)
        return len(processed_files)


class AdvancedPDFProjectManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Advanced PDF Project Manager")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2b2b2b")
        
        # Variabili principali
        self.project_path = tk.StringVar()
        self.output_pdf = tk.StringVar(value="project_Snapshot.pdf")
        self.pdf_to_read = tk.StringVar()
        self.reconstruction_output = tk.StringVar()
        
        # Esclusioni predefinite complete
        self.default_excluded_dirs = {
            'venv', '.venv', '__pycache__', '.git', '.vscode', '.idea', 
            'node_modules', 'build', 'dist', 'models2', '.continue',
            '.vs', 'target', 'out', 'bin', 'obj', 'packages', '.gradle',
            '.settings', '.metadata', '.recommenders', 'gradle', 'jvm'
        }
        
        self.default_excluded_files = {
            'config.py', 'settings.py', 'local_settings.py', '.env', 
            '.gitignore', '.gitattributes', '.env.local', '.env.production',
            'package-lock.json', 'yarn.lock', 'thumbs.db', '.DS_Store',
            'desktop.ini'
        }
        
        self.default_excluded_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.safetensors',
            '.bin', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            '.ico', '.svg', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt',
            '.pptx', '.zip', '.rar', '.7z', '.tar', '.gz', '.mp4', '.avi',
            '.mkv', '.mov', '.mp3', '.wav', '.flac', '.ogg', '.db', '.sqlite',
            '.sqlite3', '.mdb', '.accdb', '.pdb', '.idb', '.class', '.jar',
            '.war', '.ear'
        }
        
        # Variabili per le esclusioni
        self.exclude_dirs_var = tk.StringVar(value=", ".join(sorted(self.default_excluded_dirs)))
        self.exclude_files_var = tk.StringVar(value=", ".join(sorted(self.default_excluded_files)))
        self.exclude_extensions_var = tk.StringVar(value=", ".join(sorted(self.default_excluded_extensions)))
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Configura gli stili per l'interfaccia"""
        style = ttk.Style()
        
        # Tema per ttk
        style.configure('Custom.TFrame', background='#2b2b2b')
        style.configure('Custom.TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('Custom.TButton', background='#0e639c', foreground='#ffffff')
        style.configure('Success.TButton', background='#388a34', foreground='#ffffff')
        style.configure('Section.TLabelframe', background='#2b2b2b', foreground='#ce9178')
        style.configure('Section.TLabelframe.Label', background='#2b2b2b', foreground='#ce9178')
        
    def setup_ui(self):
        """Configura l'interfaccia utente principale"""
        # Header con titolo
        header_frame = ttk.Frame(self.root, style='Custom.TFrame')
        header_frame.pack(fill='x', padx=15, pady=10)
        
        # Usiamo tk.Label invece di ttk.Label per avere più controllo sullo stile
        title_label = tk.Label(header_frame, 
                              text="📁 Advanced PDF Project Manager", 
                              font=('Segoe UI', 20, 'bold'),
                              bg='#2b2b2b',
                              fg='#569cd6')
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(header_frame,
                                text="Crea PDF da progetti e ricrea progetti da PDF - Supporta tutti i tipi di file",
                                font=('Segoe UI', 12),
                                bg='#2b2b2b',
                                fg='#9cdcfe')
        subtitle_label.pack(pady=5)
        
        # Notebook per le schede
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Creazione delle schede
        self.create_pdf_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.recreate_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.exclusions_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.settings_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        
        self.notebook.add(self.create_pdf_frame, text="📄 Crea PDF da Progetto")
        self.notebook.add(self.recreate_frame, text="🔄 Ricrea Progetto da PDF")
        self.notebook.add(self.exclusions_frame, text="🚫 Gestione Esclusioni")
        self.notebook.add(self.settings_frame, text="⚙️ Impostazioni & Info")
        
        self.setup_create_pdf_tab()
        self.setup_recreate_tab()
        self.setup_exclusions_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.setup_status_bar()
        
    def setup_create_pdf_tab(self):
        """Configura la scheda per creare PDF da progetto"""
        main_frame = ttk.Frame(self.create_pdf_frame, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sezione selezione progetto
        project_section = ttk.LabelFrame(main_frame, text="📂 Selezione Progetto", style='Section.TLabelframe')
        project_section.pack(fill='x', pady=10)
        
        project_label = tk.Label(project_section, text="Cartella del progetto:", 
                               font=('Segoe UI', 10), bg='#2b2b2b', fg='#ffffff')
        project_label.grid(row=0, column=0, sticky='w', pady=8, padx=10)
        
        project_entry = tk.Entry(project_section, textvariable=self.project_path, 
                               width=70, font=('Segoe UI', 9),
                               bg='#3c3c3c', fg='#ffffff', insertbackground='#ffffff')
        project_entry.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        
        browse_project_btn = ttk.Button(project_section, text="Sfoglia 📁", 
                                      command=self.browse_project, width=15)
        browse_project_btn.grid(row=0, column=2, padx=8, pady=8)
        
        # Sezione output PDF
        output_section = ttk.LabelFrame(main_frame, text="💾 Output PDF", style='Section.TLabelframe')
        output_section.pack(fill='x', pady=10)
        
        output_label = tk.Label(output_section, text="File PDF di output:", 
                              font=('Segoe UI', 10), bg='#2b2b2b', fg='#ffffff')
        output_label.grid(row=0, column=0, sticky='w', pady=8, padx=10)
        
        output_entry = tk.Entry(output_section, textvariable=self.output_pdf, 
                              width=70, font=('Segoe UI', 9),
                              bg='#3c3c3c', fg='#ffffff', insertbackground='#ffffff')
        output_entry.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        
        browse_output_btn = ttk.Button(output_section, text="Sfoglia 💾", 
                                     command=self.browse_output_pdf, width=15)
        browse_output_btn.grid(row=0, column=2, padx=8, pady=8)
        
        # Sezione progresso
        progress_section = ttk.LabelFrame(main_frame, text="📊 Progresso", style='Section.TLabelframe')
        progress_section.pack(fill='x', pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_section, orient='horizontal', length=400, mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        
        self.progress_label = tk.Label(progress_section, text="0%", 
                                     font=('Segoe UI', 9), bg='#2b2b2b', fg='#ffffff')
        self.progress_label.pack(pady=5)
        
        # Sezione log
        log_section = ttk.LabelFrame(main_frame, text="📋 Log di Creazione", style='Section.TLabelframe')
        log_section.pack(fill='both', expand=True, pady=10)
        
        self.create_log = scrolledtext.ScrolledText(
            log_section, 
            height=15, 
            width=90, 
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#ffffff',
            selectbackground='#264f78'
        )
        self.create_log.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pulsanti azione
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill='x', pady=15)
        
        clear_log_btn = ttk.Button(button_frame, text="🧹 Pulisci Log", 
                                 command=self.clear_create_log)
        clear_log_btn.pack(side='left', padx=5)
        
        export_log_btn = ttk.Button(button_frame, text="📤 Esporta Log", 
                                  command=self.export_create_log)
        export_log_btn.pack(side='left', padx=5)
        
        stats_btn = ttk.Button(button_frame, text="📊 Statistiche Progetto", 
                             command=self.show_project_stats)
        stats_btn.pack(side='left', padx=5)
        
        self.create_pdf_btn = ttk.Button(
            button_frame, 
            text="🚀 Crea PDF", 
            command=self.start_create_pdf, 
            style='Success.TButton',
            width=20
        )
        self.create_pdf_btn.pack(side='right', padx=5)

    def update_progress(self, current, total):
        """Aggiorna la barra di progresso"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_label.config(text=f"{percentage:.1f}% ({current}/{total} file)")
        else:
            self.progress_bar['value'] = 0
            self.progress_label.config(text="0%")

    def setup_recreate_tab(self):
        """Configura la scheda per ricreare progetto da PDF"""
        main_frame = ttk.Frame(self.recreate_frame, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sezione PDF sorgente
        pdf_section = ttk.LabelFrame(main_frame, text="📄 PDF Sorgente", style='Section.TLabelframe')
        pdf_section.pack(fill='x', pady=10)
        
        pdf_label = tk.Label(pdf_section, text="File PDF:", 
                           font=('Segoe UI', 10), bg='#2b2b2b', fg='#ffffff')
        pdf_label.grid(row=0, column=0, sticky='w', pady=8, padx=10)
        
        pdf_entry = tk.Entry(pdf_section, textvariable=self.pdf_to_read, 
                           width=70, font=('Segoe UI', 9),
                           bg='#3c3c3c', fg='#ffffff', insertbackground='#ffffff')
        pdf_entry.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        
        browse_pdf_btn = ttk.Button(pdf_section, text="Sfoglia 📄", 
                                  command=self.browse_pdf, width=15)
        browse_pdf_btn.grid(row=0, column=2, padx=8, pady=8)
        
        # Sezione output progetto
        output_section = ttk.LabelFrame(main_frame, text="📁 Output Progetto", style='Section.TLabelframe')
        output_section.pack(fill='x', pady=10)
        
        output_label = tk.Label(output_section, text="Cartella di output:", 
                              font=('Segoe UI', 10), bg='#2b2b2b', fg='#ffffff')
        output_label.grid(row=0, column=0, sticky='w', pady=8, padx=10)
        
        output_entry = tk.Entry(output_section, textvariable=self.reconstruction_output, 
                              width=70, font=('Segoe UI', 9),
                              bg='#3c3c3c', fg='#ffffff', insertbackground='#ffffff')
        output_entry.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        
        browse_output_btn = ttk.Button(output_section, text="Sfoglia 📁", 
                                     command=self.browse_reconstruction_output, width=15)
        browse_output_btn.grid(row=0, column=2, padx=8, pady=8)
        
        # Sezione log
        log_section = ttk.LabelFrame(main_frame, text="📋 Log di Ricostruzione", style='Section.TLabelframe')
        log_section.pack(fill='both', expand=True, pady=10)
        
        self.recreate_log = scrolledtext.ScrolledText(
            log_section, 
            height=15, 
            width=90, 
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#ffffff',
            selectbackground='#264f78'
        )
        self.recreate_log.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pulsanti azione
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill='x', pady=15)
        
        clear_log_btn = ttk.Button(button_frame, text="🧹 Pulisci Log", 
                                 command=self.clear_recreate_log)
        clear_log_btn.pack(side='left', padx=5)
        
        export_log_btn = ttk.Button(button_frame, text="📤 Esporta Log", 
                                  command=self.export_recreate_log)
        export_log_btn.pack(side='left', padx=5)
        
        open_folder_btn = ttk.Button(button_frame, text="📂 Apri Cartella Output", 
                                   command=self.open_output_folder)
        open_folder_btn.pack(side='left', padx=5)
        
        self.recreate_btn = ttk.Button(
            button_frame, 
            text="🔄 Ricrea Progetto", 
            command=self.start_recreate_project, 
            style='Success.TButton',
            width=20
        )
        self.recreate_btn.pack(side='right', padx=5)
        
    def setup_exclusions_tab(self):
        """Configura la scheda per gestire le esclusioni"""
        main_frame = ttk.Frame(self.exclusions_frame, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Descrizione
        desc_section = ttk.LabelFrame(main_frame, text="ℹ️ Informazioni Esclusioni", style='Section.TLabelframe')
        desc_section.pack(fill='x', pady=10)
        
        desc_text = """
Queste esclusioni vengono applicate automaticamente quando crei un PDF da un progetto.
I file e cartelle esclusi non verranno inclusi nel PDF generato.

• Cartelle: Directory intere da escludere (es: venv, node_modules)
• File: Nomi specifici di file da escludere (es: .env, config.py)  
• Estensioni: Tipi di file da escludere per estensione (es: .jpg, .exe)

Separare i valori con virgole.
        """
        
        desc_label = tk.Label(desc_section, text=desc_text, justify='left', 
                            font=('Segoe UI', 9), bg='#2b2b2b', fg='#d4d4d4')
        desc_label.pack(pady=10, padx=10, anchor='w')
        
        # Sezione cartelle escluse
        dirs_section = ttk.LabelFrame(main_frame, text="📁 Cartelle Escluse", style='Section.TLabelframe')
        dirs_section.pack(fill='x', pady=10)
        
        dirs_label = tk.Label(dirs_section, text="Cartelle da escludere:", 
                            font=('Segoe UI', 10), bg='#2b2b2b', fg='#ffffff')
        dirs_label.pack(anchor='w', padx=10, pady=5)
        
        self.dirs_text = scrolledtext.ScrolledText(
            dirs_section, 
            height=4, 
            width=90,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.dirs_text.pack(fill='x', padx=10, pady=5)
        self.dirs_text.insert('1.0', ", ".join(sorted(self.default_excluded_dirs)))
        
        # Sezione file esclusi
        files_section = ttk.LabelFrame(main_frame, text="📄 File Esclusi", style='Section.TLabelframe')
        files_section.pack(fill='x', pady=10)
        
        files_label = tk.Label(files_section, text="File da escludere:", 
                             font=('Segoe UI', 10), bg='#2b2b2b', fg='#ffffff')
        files_label.pack(anchor='w', padx=10, pady=5)
        
        self.files_text = scrolledtext.ScrolledText(
            files_section, 
            height=4, 
            width=90,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.files_text.pack(fill='x', padx=10, pady=5)
        self.files_text.insert('1.0', ", ".join(sorted(self.default_excluded_files)))
        
        # Sezione estensioni escluse
        extensions_section = ttk.LabelFrame(main_frame, text="🔧 Estensioni Escluse", style='Section.TLabelframe')
        extensions_section.pack(fill='x', pady=10)
        
        extensions_label = tk.Label(extensions_section, text="Estensioni da escludere:", 
                                  font=('Segoe UI', 10), bg='#2b2b2b', fg='#ffffff')
        extensions_label.pack(anchor='w', padx=10, pady=5)
        
        self.extensions_text = scrolledtext.ScrolledText(
            extensions_section, 
            height=4, 
            width=90,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.extensions_text.pack(fill='x', padx=10, pady=5)
        self.extensions_text.insert('1.0', ", ".join(sorted(self.default_excluded_extensions)))
        
        # Pulsanti gestione esclusioni
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill='x', pady=15)
        
        save_btn = ttk.Button(button_frame, text="💾 Salva Esclusioni", 
                            command=self.save_exclusions, style='Success.TButton')
        save_btn.pack(side='left', padx=5)
        
        reset_btn = ttk.Button(button_frame, text="🔄 Ripristina Default", 
                             command=self.reset_exclusions)
        reset_btn.pack(side='left', padx=5)
        
        export_btn = ttk.Button(button_frame, text="📤 Esporta Configurazione", 
                              command=self.export_exclusions)
        export_btn.pack(side='left', padx=5)
        
        import_btn = ttk.Button(button_frame, text="📥 Importa Configurazione", 
                              command=self.import_exclusions)
        import_btn.pack(side='left', padx=5)
        
    def setup_settings_tab(self):
        """Configura la scheda impostazioni e informazioni"""
        main_frame = ttk.Frame(self.settings_frame, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Informazioni applicazione
        info_section = ttk.LabelFrame(main_frame, text="ℹ️ Informazioni Applicazione", style='Section.TLabelframe')
        info_section.pack(fill='x', pady=10)
        
        info_text = """
🚀 Advanced PDF Project Manager - Versione 3.0

Funzionalità Principali:
• 📄 Crea PDF da progetti (supporta tutti i tipi di file di testo/codice)
• 🔄 Ricrea progetti completi da PDF
• 🚫 Gestione avanzata delle esclusioni (file binari, immagini, etc.)
• 🎨 Interfaccia moderna con tema scuro
• ⚡ Operazioni in background non bloccanti

Supporta:
• Python, JavaScript, Java, C++, C#, HTML, CSS, JSON, XML, Markdown
• Tutti i linguaggi di programmazione e file di testo
• Strutture progetto complesse con sottocartelle

Tecnologie:
• Python 3.8+
• Tkinter per l'interfaccia
• PyPDF2 per l'elaborazione PDF
• Threading per operazioni non bloccanti
        """
        
        info_label = tk.Label(info_section, text=info_text, justify='left', 
                            font=('Segoe UI', 9), bg='#2b2b2b', fg='#d4d4d4')
        info_label.pack(pady=10, padx=10, anchor='w')
        
        # Statistiche e utilità
        stats_section = ttk.LabelFrame(main_frame, text="📊 Statistiche & Utilità", style='Section.TLabelframe')
        stats_section.pack(fill='x', pady=10)
        
        # Pulsanti utilità
        utils_frame = ttk.Frame(stats_section, style='Custom.TFrame')
        utils_frame.pack(fill='x', pady=10)
        
        docs_btn = ttk.Button(utils_frame, text="📖 Documentazione", 
                            command=self.open_documentation, width=20)
        docs_btn.pack(side='left', padx=5)
        
        bug_btn = ttk.Button(utils_frame, text="🐛 Segnala Bug", 
                           command=self.report_bug, width=20)
        bug_btn.pack(side='left', padx=5)
        
        suggest_btn = ttk.Button(utils_frame, text="💡 Suggerimenti", 
                               command=self.suggest_features, width=20)
        suggest_btn.pack(side='left', padx=5)
        
        update_btn = ttk.Button(utils_frame, text="🔄 Controlla Aggiornamenti", 
                              command=self.check_updates, width=20)
        update_btn.pack(side='left', padx=5)
        
    def setup_status_bar(self):
        """Configura la status bar"""
        status_frame = ttk.Frame(self.root, relief='sunken', padding=2, style='Custom.TFrame')
        status_frame.pack(fill='x', side='bottom')
        
        self.status_var = tk.StringVar(value="🟢 Pronto - Seleziona un'operazione per iniziare")
        status_label = tk.Label(status_frame, textvariable=self.status_var, 
                              font=('Segoe UI', 9), bg='#2b2b2b', fg='#569cd6')
        status_label.pack(side='left')
        
    def browse_project(self):
        path = filedialog.askdirectory(title="📁 Seleziona cartella progetto")
        if path:
            self.project_path.set(path)
            self.update_status(f"📁 Progetto selezionato: {Path(path).name}")
    
    def browse_output_pdf(self):
        path = filedialog.asksaveasfilename(
            title="💾 Salva PDF come",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("Tutti i file", "*.*")]
        )
        if path:
            self.output_pdf.set(path)
    
    def browse_pdf(self):
        path = filedialog.askopenfilename(
            title="📄 Seleziona PDF",
            filetypes=[("PDF files", "*.pdf"), ("Tutti i file", "*.*")]
        )
        if path:
            self.pdf_to_read.set(path)
            self.update_status(f"📄 PDF selezionato: {Path(path).name}")
    
    def browse_reconstruction_output(self):
        path = filedialog.askdirectory(title="📁 Seleziona cartella output")
        if path:
            self.reconstruction_output.set(path)
    
    def update_status(self, message):
        self.status_var.set(f"📅 {datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()
    
    def log_create(self, message):
        self.create_log.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.create_log.see(tk.END)
        self.root.update_idletasks()
    
    def log_recreate(self, message):
        self.recreate_log.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.recreate_log.see(tk.END)
        self.root.update_idletasks()
    
    def clear_create_log(self):
        self.create_log.delete(1.0, tk.END)
        self.update_status("Log di creazione pulito")
    
    def clear_recreate_log(self):
        self.recreate_log.delete(1.0, tk.END)
        self.update_status("Log di ricostruzione pulito")
    
    def export_create_log(self):
        self.export_log(self.create_log, "create_log.txt")
    
    def export_recreate_log(self):
        self.export_log(self.recreate_log, "recreate_log.txt")
    
    def export_log(self, log_widget, filename):
        content = log_widget.get(1.0, tk.END)
        path = filedialog.asksaveasfilename(
            title="📤 Esporta log",
            defaultextension=".txt",
            initialfile=filename,
            filetypes=[("Text files", "*.txt"), ("Tutti i file", "*.*")]
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.update_status(f"Log esportato: {Path(path).name}")
    
    def save_exclusions(self):
        """Salva le esclusioni dalle text area"""
        try:
            dirs_text = self.dirs_text.get(1.0, tk.END).strip()
            files_text = self.files_text.get(1.0, tk.END).strip()
            extensions_text = self.extensions_text.get(1.0, tk.END).strip()
            
            self.exclude_dirs_var.set(dirs_text)
            self.exclude_files_var.set(files_text)
            self.exclude_extensions_var.set(extensions_text)
            
            messagebox.showinfo("Successo", "Esclusioni salvate con successo!")
            self.update_status("Configurazione esclusioni salvata")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")
    
    def reset_exclusions(self):
        """Ripristina le esclusioni predefinite"""
        self.dirs_text.delete(1.0, tk.END)
        self.dirs_text.insert('1.0', ", ".join(sorted(self.default_excluded_dirs)))
        
        self.files_text.delete(1.0, tk.END)
        self.files_text.insert('1.0', ", ".join(sorted(self.default_excluded_files)))
        
        self.extensions_text.delete(1.0, tk.END)
        self.extensions_text.insert('1.0', ", ".join(sorted(self.default_excluded_extensions)))
        
        self.update_status("Esclusioni ripristinate ai valori predefiniti")
    
    def export_exclusions(self):
        """Esporta la configurazione delle esclusioni"""
        try:
            path = filedialog.asksaveasfilename(
                title="📤 Esporta configurazione esclusioni",
                defaultextension=".txt",
                initialfile="exclusions_config.txt",
                filetypes=[("Text files", "*.txt"), ("Tutti i file", "*.*")]
            )
            if path:
                config = f"""# Advanced PDF Project Manager - Configurazione Esclusioni
# Esportato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[DIRS]
{self.dirs_text.get(1.0, tk.END).strip()}

[FILES]
{self.files_text.get(1.0, tk.END).strip()}

[EXTENSIONS]
{self.extensions_text.get(1.0, tk.END).strip()}
"""
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(config)
                self.update_status(f"Configurazione esportata: {Path(path).name}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione: {str(e)}")
    
    def import_exclusions(self):
        """Importa la configurazione delle esclusioni"""
        try:
            path = filedialog.askopenfilename(
                title="📥 Importa configurazione esclusioni",
                filetypes=[("Text files", "*.txt"), ("Tutti i file", "*.*")]
            )
            if path:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parsing semplice del file di configurazione
                sections = content.split('[')
                for section in sections:
                    if section.startswith('DIRS]'):
                        dirs_content = section[5:].split('[')[0].strip()
                        self.dirs_text.delete(1.0, tk.END)
                        self.dirs_text.insert('1.0', dirs_content)
                    elif section.startswith('FILES]'):
                        files_content = section[6:].split('[')[0].strip()
                        self.files_text.delete(1.0, tk.END)
                        self.files_text.insert('1.0', files_content)
                    elif section.startswith('EXTENSIONS]'):
                        extensions_content = section[10:].split('[')[0].strip()
                        self.extensions_text.delete(1.0, tk.END)
                        self.extensions_text.insert('1.0', extensions_content)
                
                self.update_status(f"Configurazione importata: {Path(path).name}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'importazione: {str(e)}")
    
    def show_project_stats(self):
        """Mostra statistiche del progetto selezionato"""
        if not self.project_path.get() or not os.path.exists(self.project_path.get()):
            messagebox.showwarning("Attenzione", "Seleziona prima un progetto valido")
            return
        
        try:
            project_path = Path(self.project_path.get())
            total_files = 0
            total_size = 0
            extensions = {}
            
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
                    ext = file_path.suffix.lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            stats_text = f"""
Statistiche Progetto: {project_path.name}

File totali: {total_files}
Dimensione totale: {total_size / (1024*1024):.2f} MB

Estensioni principali:
"""
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
                stats_text += f"  {ext or 'Nessuna'}: {count} file\n"
            
            messagebox.showinfo("📊 Statistiche Progetto", stats_text)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel calcolo statistiche: {str(e)}")
    
    def open_output_folder(self):
        """Apre la cartella di output nel file explorer"""
        if self.reconstruction_output.get() and os.path.exists(self.reconstruction_output.get()):
            os.startfile(self.reconstruction_output.get())
            self.update_status("Cartella output aperta")
        else:
            messagebox.showwarning("Attenzione", "Cartella di output non valida")
    
    def open_documentation(self):
        webbrowser.open("https://github.com/Sigmanih/PySynkroNet/")
    
    def report_bug(self):
        webbrowser.open("https://github.com/Sigmanih/PySynkroNet/issues")
    
    def suggest_features(self):
        webbrowser.open("https://github.com/Sigmanih/PySynkroNet/discussions")
    
    def check_updates(self):
        messagebox.showinfo("Aggiornamenti", "🔄 Controllo aggiornamenti in sviluppo")
    
    def start_create_pdf(self):
        """Avvia la creazione del PDF in un thread separato"""
        if not self.project_path.get():
            messagebox.showerror("Errore", "Seleziona una cartella progetto")
            return
        
        if not self.output_pdf.get():
            messagebox.showerror("Errore", "Specifica un file PDF di output")
            return
        
        self.create_pdf_btn.config(state='disabled')
        self.update_status("🚀 Avvio creazione PDF...")
        
        thread = threading.Thread(target=self.create_pdf_thread)
        thread.daemon = True
        thread.start()
    
    def create_pdf_thread(self):
        """Thread per la creazione del PDF"""
        try:
            self.log_create("🚀 Inizio creazione PDF...")
            self.log_create(f"📁 Progetto: {self.project_path.get()}")
            self.log_create(f"📄 Output: {self.output_pdf.get()}")
            
            # Prepara le esclusioni dalle text area
            custom_exclusions = {}
            
            dirs_text = self.dirs_text.get(1.0, tk.END).strip()
            if dirs_text:
                dirs = [d.strip() for d in dirs_text.split(',') if d.strip()]
                custom_exclusions['dirs'] = dirs
                self.log_create(f"📁 Cartelle escluse: {len(dirs)} elementi")
            
            files_text = self.files_text.get(1.0, tk.END).strip()
            if files_text:
                files = [f.strip() for f in files_text.split(',') if f.strip()]
                custom_exclusions['files'] = files
                self.log_create(f"📄 File esclusi: {len(files)} elementi")
            
            extensions_text = self.extensions_text.get(1.0, tk.END).strip()
            if extensions_text:
                exts = [e.strip() for e in extensions_text.split(',') if e.strip()]
                custom_exclusions['extensions'] = exts
                self.log_create(f"🔧 Estensioni escluse: {len(exts)} elementi")
            
            # Reset barra di progresso
            self.root.after(0, self.update_progress, 0, 100)
            
            # Crea il PDF
            converter = PythonProjectToPDF()
            
            # Definiamo il callback per il progresso
            def progress_callback(current, total):
                self.root.after(0, self.update_progress, current, total)
            
            files_processed = converter.create_pdf(
                self.project_path.get(),
                self.output_pdf.get(),
                custom_exclusions,
                progress_callback  # Passa il callback
            )
            
            self.log_create(f"✅ PDF creato con successo! File processati: {files_processed}")
            self.update_status("✅ PDF creato con successo!")
            messagebox.showinfo("Successo", f"PDF creato con successo!\nFile processati: {files_processed}")
            
        except Exception as e:
            error_msg = f"❌ Errore durante la creazione del PDF: {str(e)}"
            self.log_create(error_msg)
            self.update_status("❌ Errore nella creazione PDF")
            messagebox.showerror("Errore", f"Errore durante la creazione del PDF:\n{str(e)}")
        finally:
            self.create_pdf_btn.config(state='normal')
    
    def start_recreate_project(self):
        """Avvia la ricostruzione del progetto in un thread separato"""
        if not self.pdf_to_read.get():
            messagebox.showerror("Errore", "Seleziona un file PDF")
            return
        
        if not self.reconstruction_output.get():
            messagebox.showerror("Errore", "Specifica una cartella di output")
            return
        
        if not os.path.exists(self.pdf_to_read.get()):
            messagebox.showerror("Errore", "Il file PDF specificato non esiste")
            return
        
        self.recreate_btn.config(state='disabled')
        self.update_status("🔄 Avvio ricostruzione progetto...")
        
        # Per ora mostriamo un messaggio in quanto la ricostruzione è gestita da pdf_to_folder.py
        self.log_recreate("ℹ️ La funzionalità di ricostruzione è gestita dal modulo pdf_to_folder.py")
        self.log_recreate("ℹ️ Usa il file pdf_to_folder.py per ricostruire progetti da PDF")
        messagebox.showinfo("Info", "La ricostruzione del progetto da PDF è gestita dal modulo separato pdf_to_folder.py")
        self.recreate_btn.config(state='normal')

def main():
    root = tk.Tk()
    app = AdvancedPDFProjectManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()