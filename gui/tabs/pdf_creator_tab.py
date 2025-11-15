"""
Scheda per la creazione di PDF da progetti
"""
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from pathlib import Path
import threading
from core.pdf_converter import PDFConverter

class PDFCreatorTab:
    """Scheda per la creazione di PDF da progetti"""
    
    def __init__(self, parent):
        self.parent = parent
        self.title = "? Crea PDF da Progetto"
        self.pdf_converter = PDFConverter()
        self.include_excluded_files = tk.BooleanVar(value=False)  # Nuovo flag
        self._create_tab()
    
    def _create_tab(self):
        """Crea il contenuto della scheda"""
        self.frame = ttk.Frame(self.parent, style='Custom.TFrame')
        self._create_project_section()
        self._create_output_section()
        self._create_progress_section()
        self._create_log_section()
        self._create_buttons()
    
    def _create_project_section(self):
        """Crea la sezione selezione progetto"""
        project_section = ttk.LabelFrame(self.frame, text="📁 Selezione Progetto", style='Section.TLabelframe')
        project_section.pack(fill='x', pady=(0, 15), padx=15)
        project_section.columnconfigure(1, weight=1)
        
        # Etichetta
        project_label = tk.Label(
            project_section,
            text="Cartella del progetto:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        project_label.grid(row=0, column=0, sticky='w', pady=12, padx=12)
        
        # Entry per il percorso
        self.project_path = tk.StringVar()
        project_entry = tk.Entry(
            project_section,
            textvariable=self.project_path,
            width=70,
            font=('Segoe UI', 9),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            highlightthickness=1,
            highlightcolor='#569cd6'
        )
        project_entry.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        
        # Pulsante sfoglia
        browse_project_btn = tk.Button(
            project_section,
            text="Sfoglia 📁",
            command=self._browse_project,
            bg='#0e639c',
            fg='#ffffff',
            relief='flat',
            width=15
        )
        browse_project_btn.grid(row=0, column=2, padx=8, pady=8)
    
    def _create_output_section(self):
        """Crea la sezione output PDF"""
        options_section = ttk.LabelFrame(self.frame, text='🔧 Opzioni', style='Section.TLabelframe')
        options_section.pack(fill='x', pady=(0, 15), padx=15)
        
        options_frame = tk.Frame(options_section, bg='#1e1e1e')
        options_frame.pack(fill='x', padx=12, pady=8)
        
        # Checkbutton per includere file esclusi
        include_excluded_cb = tk.Checkbutton(
            options_frame,
            text="Includi file esclusi nel PDF",
            variable=self.include_excluded_files,
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            selectcolor='#3c3c3c',
            activebackground='#1e1e1e',
            activeforeground='#d4d4d4'
        )
        include_excluded_cb.pack(side='left', padx=10)
        output_section = ttk.LabelFrame(self.frame, text="📄 Output PDF", style='Section.TLabelframe')
        output_section.pack(fill='x', pady=(0, 15), padx=15)
        output_section.columnconfigure(1, weight=1)
        
        # Etichetta
        output_label = tk.Label(
            output_section,
            text="File PDF di output:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        output_label.grid(row=0, column=0, sticky='w', pady=12, padx=12)
        
        # Entry per l'output
        self.output_pdf = tk.StringVar(value="project_Snapshot.pdf")
        output_entry = tk.Entry(
            output_section,
            textvariable=self.output_pdf,
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
            text="Sfoglia 💾",
            command=self._browse_output_pdf,
            bg='#0e639c',
            fg='#ffffff',
            relief='flat',
            width=15
        )
        browse_output_btn.grid(row=0, column=2, padx=8, pady=8)
    
        
    def _create_progress_section(self):
        """Crea la sezione progresso"""
        progress_section = ttk.LabelFrame(self.frame, text="📊 Progresso", style='Section.TLabelframe')
        progress_section.pack(fill='x', pady=(0, 15), padx=15)
        
        # Etichetta progresso
        self.progress_label = tk.Label(
            progress_section,
            text="Pronto per iniziare...",
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.progress_label.pack(anchor='w', padx=12, pady=(8, 2))
        
        # Barra di progresso
        self.progress_bar = ttk.Progressbar(
            progress_section,
            style="Custom.Horizontal.TProgressbar",
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', padx=12, pady=(2, 8))
    
    def _create_log_section(self):
        """Crea la sezione log"""
        log_section = ttk.LabelFrame(self.frame, text="📝 Log di Creazione", style='Section.TLabelframe')
        log_section.pack(fill='both', expand=True, pady=(0, 15), padx=15)
        
        # Area di testo per il log
        self.create_log = scrolledtext.ScrolledText(
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
        self.create_log.pack(fill='both', expand=True, padx=12, pady=12)
    
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
        
        stats_btn = tk.Button(
            left_button_frame,
            text="📈 Statistiche Progetto",
            command=self._show_project_stats,
            bg='#9cdcfe',
            fg='#000000',
            relief='flat'
        )
        stats_btn.pack(side='left', padx=5)
        
        # Pulsanti destra
        right_button_frame = tk.Frame(button_frame, bg='#1e1e1e')
        right_button_frame.pack(side='right')
        
        self.create_pdf_btn = tk.Button(
            right_button_frame,
            text="🔄 GENERA PDF",
            command=self._start_create_pdf,
            bg='#388a34',
            fg='#000000',
            font=('Segoe UI', 10, 'bold'),
            width=15,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        self.create_pdf_btn.pack(side='right', padx=5)
    
    def _browse_project(self):
        """Apri dialogo per selezione cartella progetto"""
        path = filedialog.askdirectory(title="📁 Seleziona cartella progetto")
        if path:
            self.project_path.set(path)
            self._log_message(f"Progetto selezionato: {Path(path).name}")
    
    def _browse_output_pdf(self):
        """Apri dialogo per salvataggio PDF"""
        path = filedialog.asksaveasfilename(
            title="💾 Salva PDF come",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("Tutti i file", "*.*")]
        )
        if path:
            self.output_pdf.set(path)
    
    def _clear_log(self):
        """Pulisce il log"""
        self.create_log.delete(1.0, tk.END)
        self._log_message("Log pulito")
    
    def _export_log(self):
        """Esporta il log in un file"""
        content = self.create_log.get(1.0, tk.END)
        path = filedialog.asksaveasfilename(
            title="📤 Esporta log",
            defaultextension=".txt",
            initialfile="create_log.txt",
            filetypes=[("Text files", "*.txt"), ("Tutti i file", "*.*")]
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self._log_message(f"Log esportato: {Path(path).name}")
    
    def _show_project_stats(self):
        """Mostra statistiche del progetto"""
        if not self.project_path.get():
            tk.messagebox.showwarning("Attenzione", "Seleziona prima un progetto valido")
            return
        
        try:
            from core.file_manager import FileManager
            fm = FileManager()
            stats = fm.get_project_stats(self.project_path.get())
            
            stats_text = f"""
Statistiche Progetto: {Path(self.project_path.get()).name}

File totali: {stats['total_files']}
Dimensione totale: {stats['total_size_mb']:.2f} MB

Estensioni principali:
"""
            for ext, count in sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True)[:10]:
                stats_text += f" {ext or 'Nessuna'}: {count} file\n"
            
            tk.messagebox.showinfo("📈 Statistiche Progetto", stats_text)
            
        except Exception as e:
            tk.messagebox.showerror("Errore", f"Errore nel calcolo statistiche: {str(e)}")
    
    def _start_create_pdf(self):
        """Avvia la creazione del PDF"""
        if not self.project_path.get():
            tk.messagebox.showerror("Errore", "Seleziona una cartella progetto")
            return
        
        if not self.output_pdf.get():
            tk.messagebox.showerror("Errore", "Specifica un file PDF di output")
            return
        
        self.create_pdf_btn.config(state='disabled', bg='#666666')
        self._log_message("🔄 Avvio creazione PDF...")
        
        # Avvia in un thread separato
        thread = threading.Thread(target=self._create_pdf_thread)
        thread.daemon = True
        thread.start()
    
    def _create_pdf_thread(self):
        """Thread per la creazione del PDF"""
        try:
            self._log_message('? Inizio creazione PDF...')
            self._log_message(f"? Progetto: {self.project_path.get()}")
            self._log_message(f"? Output: {self.output_pdf.get()}")
            self._log_message(f"? Includi file esclusi: {self.include_excluded_files.get()}")
            
            # Prepara le esclusioni
            custom_exclusions = {}
            
            # Reset barra di progresso
            self._update_progress(0, 100)
            
            # Crea il PDF con il flag per includere file esclusi
            files_processed, pdf_path = self.pdf_converter.create_project_pdf(
                self.project_path.get(),
                self.output_pdf.get(),
                custom_exclusions,
                self._update_progress,
                include_excluded=self.include_excluded_files.get(),
                open_after_creation=True  # Apri automaticamente dopo la creazione
            )
            
            self._log_message(f"? PDF creato con successo! File processati: {files_processed}")
            self._log_message(f"? PDF salvato in: {pdf_path}")
            self._log_message(f"? PDF aperto automaticamente")
            
            tk.messagebox.showinfo('Successo', 
                                f"PDF creato con successo!\n"
                                f"File processati: {files_processed}\n"
                                f"PDF salvato in: {pdf_path}\n\n"
                                f"Il PDF è stato aperto automaticamente.")
        
        except Exception as e:
            error_msg = f"? Errore durante la creazione del PDF: {str(e)}"
            self._log_message(error_msg)
            tk.messagebox.showerror("Errore", f"Errore durante la creazione del PDF:\n{str(e)}")
        
        finally:
            self.create_pdf_btn.config(state='normal', bg='#388a34')
    
    def _update_progress(self, current, total):
        """Aggiorna la barra di progresso"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_label.config(text=f"Elaborazione: {current}/{total} file ({percentage:.1f}%)")
        else:
            self.progress_bar['value'] = 0
            self.progress_label.config(text='Pronto per iniziare...')
    
    def _log_message(self, message):
        """Aggiunge un messaggio al log"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.create_log.insert(tk.END, f"{timestamp} - {message}\n")
        self.create_log.see(tk.END)
        self.create_log.update_idletasks()