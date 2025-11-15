"""
Scheda per la ricostruzione di progetti da PDF
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
import threading
import os
from core.project_recreator import ProjectRecreator

class ProjectRecreatorTab:
    """Scheda per la ricostruzione di progetti da PDF"""
    
    def __init__(self, parent):
        self.parent = parent
        self.title = "🔄 Ricrea Progetto da PDF"
        self.project_recreator = ProjectRecreator()
        self._create_tab()
    
    def _create_tab(self):
        """Crea il contenuto della scheda"""
        self.frame = ttk.Frame(self.parent, style='Custom.TFrame')
        self._create_pdf_section()
        self._create_output_section()
        self._create_options_section()
        self._create_log_section()
        self._create_buttons()
    
    def _create_pdf_section(self):
        """Crea la sezione selezione PDF"""
        pdf_section = ttk.LabelFrame(self.frame, text="📄 PDF Sorgente", style='Section.TLabelframe')
        pdf_section.pack(fill='x', pady=(0, 15), padx=15)
        pdf_section.columnconfigure(1, weight=1)
        
        # Etichetta
        pdf_label = tk.Label(
            pdf_section,
            text="File PDF:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        pdf_label.grid(row=0, column=0, sticky='w', pady=12, padx=12)
        
        # Entry per il PDF
        self.pdf_to_read = tk.StringVar()
        pdf_entry = tk.Entry(
            pdf_section,
            textvariable=self.pdf_to_read,
            width=70,
            font=('Segoe UI', 9),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            highlightthickness=1,
            highlightcolor='#569cd6'
        )
        pdf_entry.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        
        # Pulsante sfoglia
        browse_pdf_btn = tk.Button(
            pdf_section,
            text="Sfoglia 📁",
            command=self._browse_pdf,
            bg='#0e639c',
            fg='#ffffff',
            relief='flat',
            width=15
        )
        browse_pdf_btn.grid(row=0, column=2, padx=8, pady=8)
    
    def _create_output_section(self):
        """Crea la sezione output progetto"""
        output_section = ttk.LabelFrame(self.frame, text="📁 Output Progetto", style='Section.TLabelframe')
        output_section.pack(fill='x', pady=(0, 15), padx=15)
        output_section.columnconfigure(1, weight=1)
        
        # Etichetta
        output_label = tk.Label(
            output_section,
            text="Cartella di output:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        output_label.grid(row=0, column=0, sticky='w', pady=12, padx=12)
        
        # Entry per l'output
        self.reconstruction_output = tk.StringVar()
        output_entry = tk.Entry(
            output_section,
            textvariable=self.reconstruction_output,
            width=70,
            font=('Segoe UI', 9),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            highlightthickness=1,
            highlightcolor='#569cd6'
        )
        output_entry.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        
        # Pulsante sfoglia
        browse_output_btn = tk.Button(
            output_section,
            text="Sfoglia 📂",
            command=self._browse_reconstruction_output,
            bg='#0e639c',
            fg='#ffffff',
            relief='flat',
            width=15
        )
        browse_output_btn.grid(row=0, column=2, padx=8, pady=8)
    
    def _create_options_section(self):
        """Crea la sezione opzioni"""
        options_section = ttk.LabelFrame(self.frame, text="⚙️ Opzioni Ricostruzione", style='Section.TLabelframe')
        options_section.pack(fill='x', pady=(0, 15), padx=15)
        
        options_frame = tk.Frame(options_section, bg='#1e1e1e')
        options_frame.pack(fill='x', padx=12, pady=8)
        
        # Checkbutton per aprire cartella automaticamente
        self.auto_open_folder = tk.BooleanVar(value=True)
        auto_open_cb = tk.Checkbutton(
            options_frame,
            text="Apri cartella output automaticamente",
            variable=self.auto_open_folder,
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            selectcolor='#3c3c3c',
            activebackground='#1e1e1e',
            activeforeground='#d4d4d4'
        )
        auto_open_cb.pack(side='left', padx=10)
        
        # Checkbutton per creare report
        self.create_report = tk.BooleanVar(value=True)
        report_cb = tk.Checkbutton(
            options_frame,
            text="Crea report di ricostruzione",
            variable=self.create_report,
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            selectcolor='#3c3c3c',
            activebackground='#1e1e1e',
            activeforeground='#d4d4d4'
        )
        report_cb.pack(side='left', padx=10)
        
        # Checkbutton per sovrascrivere file esistenti
        self.overwrite_existing = tk.BooleanVar(value=False)
        overwrite_cb = tk.Checkbutton(
            options_frame,
            text="Sovrascrivi file esistenti",
            variable=self.overwrite_existing,
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            selectcolor='#3c3c3c',
            activebackground='#1e1e1e',
            activeforeground='#d4d4d4'
        )
        overwrite_cb.pack(side='left', padx=10)
    
    def _create_log_section(self):
        """Crea la sezione log"""
        log_section = ttk.LabelFrame(self.frame, text="📝 Log di Ricostruzione", style='Section.TLabelframe')
        log_section.pack(fill='both', expand=True, pady=(0, 15), padx=15)
        
        # Area di testo per il log
        self.recreate_log = scrolledtext.ScrolledText(
            log_section,
            height=12,
            width=90,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#ffffff',
            selectbackground='#264f78',
            relief='flat',
            borderwidth=1
        )
        self.recreate_log.pack(fill='both', expand=True, padx=12, pady=12)
    
    def _create_buttons(self):
        """Crea i pulsanti di azione"""
        button_frame = tk.Frame(self.frame, bg='#1e1e1e')
        button_frame.pack(fill='x', pady=10, padx=15)
        
        # Pulsanti sinistra
        left_button_frame = tk.Frame(button_frame, bg='#1e1e1e')
        left_button_frame.pack(side='left')
        
        clear_log_btn = tk.Button(
            left_button_frame,
            text="🧹 Pulisci Log",
            command=self._clear_log,
            bg='#ce9178',
            fg='#000000',
            relief='flat'
        )
        clear_log_btn.pack(side='left', padx=5)
        
        export_log_btn = tk.Button(
            left_button_frame,
            text="📤 Esporta Log",
            command=self._export_log,
            bg='#569cd6',
            fg='#000000',
            relief='flat'
        )
        export_log_btn.pack(side='left', padx=5)
        
        open_folder_btn = tk.Button(
            left_button_frame,
            text="📂 Apri Cartella Output",
            command=self._open_output_folder,
            bg='#9cdcfe',
            fg='#000000',
            relief='flat'
        )
        open_folder_btn.pack(side='left', padx=5)
        
        # Pulsanti destra
        right_button_frame = tk.Frame(button_frame, bg='#1e1e1e')
        right_button_frame.pack(side='right')
        
        self.recreate_btn = tk.Button(
            right_button_frame,
            text="🔄 RICREA PROGETTO",
            command=self._start_recreate_project,
            bg='#388a34',
            fg='#000000',
            font=('Segoe UI', 10, 'bold'),
            width=15,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        self.recreate_btn.pack(side='right', padx=5)
    
    # Modifica _browse_pdf per partire dalla cartella Saved
    def _browse_pdf(self):
        """Apri dialogo per selezione PDF"""
        # Usa la cartella Saved come directory iniziale
        initial_dir = "Saved"
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)
        
        path = filedialog.askopenfilename(
            title="? Seleziona PDF",
            initialdir=initial_dir,
            filetypes=[("PDF files", "*.pdf"), ("Tutti i file", "*.*")]
        )
        if path:
            self.pdf_to_read.set(path)
            self._log_message(f"PDF selezionato: {Path(path).name}")
    
    def _browse_reconstruction_output(self):
        """Apri dialogo per selezione cartella output"""
        path = filedialog.askdirectory(title="📂 Seleziona cartella output")
        if path:
            self.reconstruction_output.set(path)
    
    def _clear_log(self):
        """Pulisce il log"""
        self.recreate_log.delete(1.0, tk.END)
        self._log_message("Log pulito")
    
    def _export_log(self):
        """Esporta il log in un file"""
        content = self.recreate_log.get(1.0, tk.END)
        path = filedialog.asksaveasfilename(
            title="📤 Esporta log",
            defaultextension=".txt",
            initialfile="recreate_log.txt",
            filetypes=[("Text files", "*.txt"), ("Tutti i file", "*.*")]
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log_message(f"Log esportato: {Path(path).name}")
    
    def _open_output_folder(self):
        """Apre la cartella di output nel file explorer"""
        if self.reconstruction_output.get() and os.path.exists(self.reconstruction_output.get()):
            os.startfile(self.reconstruction_output.get())
            self._log_message("Cartella output aperta")
        else:
            messagebox.showwarning("Attenzione", "Cartella di output non valida")
    
    def _start_recreate_project(self):
        """Avvia la ricostruzione del progetto"""
        if not self.pdf_to_read.get():
            messagebox.showerror("Errore", "Seleziona un file PDF")
            return
        
        if not self.reconstruction_output.get():
            messagebox.showerror("Errore", "Specifica una cartella di output")
            return
        
        if not os.path.exists(self.pdf_to_read.get()):
            messagebox.showerror("Errore", "Il file PDF specificato non esiste")
            return
        
        self.recreate_btn.config(state='disabled', bg='#666666')
        self._log_message("🔄 Avvio ricostruzione progetto...")
        
        # Avvia in un thread separato
        thread = threading.Thread(target=self._recreate_project_thread)
        thread.daemon = True
        thread.start()
    
    def _recreate_project_thread(self):
        """Thread per la ricostruzione del progetto"""
        try:
            self._log_message("🔄 Inizio ricostruzione progetto...")
            self._log_message(f"📄 PDF sorgente: {self.pdf_to_read.get()}")
            self._log_message(f"📁 Output: {self.reconstruction_output.get()}")
            
            # Ricrea il progetto
            success = self.project_recreator.recreate_project_structure(
                self.pdf_to_read.get(),
                self.reconstruction_output.get()
            )
            
            if success:
                self._log_message("✅ Progetto ricostruito con successo!")
                
                # Apri la cartella se richiesto
                if self.auto_open_folder.get():
                    self._open_output_folder()
                
                messagebox.showinfo("Successo", "Progetto ricostruito con successo!")
            else:
                self._log_message("❌ Ricostruzione fallita!")
                messagebox.showerror("Errore", "Ricostruzione del progetto fallita")
                
        except Exception as e:
            error_msg = f"❌ Errore durante la ricostruzione: {str(e)}"
            self._log_message(error_msg)
            messagebox.showerror("Errore", f"Errore durante la ricostruzione:\n{str(e)}")
        finally:
            self.recreate_btn.config(state='normal', bg='#388a34')
    
    def _log_message(self, message):
        """Aggiunge un messaggio al log"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.recreate_log.insert(tk.END, f"{timestamp} - {message}\n")
        self.recreate_log.see(tk.END)
        self.recreate_log.update_idletasks()