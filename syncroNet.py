#File: syncroNet.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import sys
import webbrowser
from datetime import datetime

# Importa le classi dai tuoi file
from folder_to_pdf import PythonProjectToPDF
from pdf_to_folder import UniversalPDFToProject


class AdvancedPDFProjectManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Advanced PDF Project Manager")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2b2b2b")
        
        # Variabili principali
        self.project_path = tk.StringVar()
        self.output_pdf = tk.StringVar(value="project_documentation.pdf")
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
            'desktop.ini', '*.tmp', '*.temp'
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
        
        # Sezione opzioni
        options_section = ttk.LabelFrame(main_frame, text="⚙️ Opzioni Ricostruzione", style='Section.TLabelframe')
        options_section.pack(fill='x', pady=10)
        
        self.auto_open_folder = tk.BooleanVar(value=True)
        self.create_report = tk.BooleanVar(value=True)
        self.overwrite_existing = tk.BooleanVar(value=False)
        
        auto_open_cb = tk.Checkbutton(options_section, text="Apri cartella output automaticamente", 
                                    variable=self.auto_open_folder, font=('Segoe UI', 9),
                                    bg='#2b2b2b', fg='#ffffff', selectcolor='#3c3c3c')
        auto_open_cb.grid(row=0, column=0, sticky='w', pady=4, padx=10)
        
        report_cb = tk.Checkbutton(options_section, text="Crea report di ricostruzione", 
                                 variable=self.create_report, font=('Segoe UI', 9),
                                 bg='#2b2b2b', fg='#ffffff', selectcolor='#3c3c3c')
        report_cb.grid(row=0, column=1, sticky='w', pady=4, padx=10)
        
        overwrite_cb = tk.Checkbutton(options_section, text="Sovrascrivi file esistenti", 
                                    variable=self.overwrite_existing, font=('Segoe UI', 9),
                                    bg='#2b2b2b', fg='#ffffff', selectcolor='#3c3c3c')
        overwrite_cb.grid(row=0, column=2, sticky='w', pady=4, padx=10)
        
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
        webbrowser.open("https://github.com/your-repo/documentation")
    
    def report_bug(self):
        webbrowser.open("https://github.com/your-repo/issues")
    
    def suggest_features(self):
        webbrowser.open("https://github.com/your-repo/discussions")
    
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
            
            # Crea il PDF usando la classe dal tuo file
            converter = PythonProjectToPDF()
            files_processed = converter.create_pdf(
                self.project_path.get(),
                self.output_pdf.get(),
                custom_exclusions
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
        
        thread = threading.Thread(target=self.recreate_project_thread)
        thread.daemon = True
        thread.start()
    
    def recreate_project_thread(self):
        """Thread per la ricostruzione del progetto"""
        try:
            self.log_recreate("🚀 Inizio ricostruzione progetto...")
            self.log_recreate(f"📄 PDF sorgente: {self.pdf_to_read.get()}")
            self.log_recreate(f"📁 Output: {self.reconstruction_output.get()}")
            
            # Ricrea il progetto usando la classe dal tuo file
            recreator = UniversalPDFToProject()
            success = recreator.recreate_project_structure(
                self.pdf_to_read.get(),
                self.reconstruction_output.get()
            )
            
            if success:
                self.log_recreate("✅ Progetto ricostruito con successo!")
                self.update_status("✅ Progetto ricostruito con successo!")
                
                if self.auto_open_folder.get():
                    self.open_output_folder()
                
                messagebox.showinfo("Successo", "Progetto ricostruito con successo!")
            else:
                self.log_recreate("❌ Ricostruzione fallita!")
                self.update_status("❌ Ricostruzione fallita")
                messagebox.showerror("Errore", "Ricostruzione del progetto fallita!")
            
        except Exception as e:
            error_msg = f"❌ Errore durante la ricostruzione: {str(e)}"
            self.log_recreate(error_msg)
            self.update_status("❌ Errore nella ricostruzione")
            messagebox.showerror("Errore", f"Errore durante la ricostruzione:\n{str(e)}")
        finally:
            self.recreate_btn.config(state='normal')

def main():
    root = tk.Tk()
    app = AdvancedPDFProjectManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()