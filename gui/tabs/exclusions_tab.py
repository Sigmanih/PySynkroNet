"""
Scheda per la gestione delle esclusioni
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
from datetime import datetime
from core.config import DEFAULT_EXCLUSIONS

class ExclusionsTab:
    """Scheda per la gestione delle esclusioni"""
    
    def __init__(self, parent):
        self.parent = parent
        self.title = "⚙️ Gestione Esclusioni"
        self.current_exclusions = DEFAULT_EXCLUSIONS.copy()
        self._create_tab()
    
    def _create_tab(self):
        """Crea il contenuto della scheda"""
        self.frame = ttk.Frame(self.parent, style='Custom.TFrame')
        self._create_description_section()
        self._create_dirs_section()
        self._create_files_section()
        self._create_extensions_section()
        self._create_buttons()
    
    def _create_description_section(self):
        """Crea la sezione descrizione"""
        desc_section = ttk.LabelFrame(self.frame, text="ℹ️ Informazioni Esclusioni", style='Section.TLabelframe')
        desc_section.pack(fill='x', pady=(0, 15), padx=15)
        
        desc_text = """Queste esclusioni vengono applicate automaticamente quando crei un PDF da un progetto.
I file e cartelle esclusi non verranno inclusi nel PDF generato.
📁 Cartelle: Directory intere da escludere (es: venv, node_modules)
📄 File: Nomi specifici di file da escludere (es: .env, config.py)
🔤 Estensioni: Tipi di file da escludere per estensione (es: .jpg, .exe)

Separare i valori con virgole. Usa * per i pattern (es: *.tmp)
        """
        
        desc_label = tk.Label(
            desc_section,
            text=desc_text,
            justify='left',
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        desc_label.pack(pady=12, padx=12, anchor='w')
    
    def _create_dirs_section(self):
        """Crea la sezione cartelle escluse"""
        dirs_section = ttk.LabelFrame(self.frame, text="📁 Cartelle Escluse", style='Section.TLabelframe')
        dirs_section.pack(fill='x', pady=(0, 15), padx=15)
        
        # Etichetta
        dirs_label = tk.Label(
            dirs_section,
            text="Cartelle da escludere:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        dirs_label.pack(anchor='w', padx=12, pady=(8, 5))
        
        # Area di testo per le cartelle
        self.dirs_text = scrolledtext.ScrolledText(
            dirs_section,
            height=6,
            width=90,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            relief='flat',
            borderwidth=1
        )
        self.dirs_text.pack(fill='x', padx=12, pady=(0, 8))
        
        # Inserisci i valori predefiniti
        self.dirs_text.insert('1.0', ", ".join(sorted(self.current_exclusions['dirs'])))
    
    def _create_files_section(self):
        """Crea la sezione file esclusi"""
        files_section = ttk.LabelFrame(self.frame, text="📄 File Esclusi", style='Section.TLabelframe')
        files_section.pack(fill='x', pady=(0, 15), padx=15)
        
        # Etichetta
        files_label = tk.Label(
            files_section,
            text="File da escludere:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        files_label.pack(anchor='w', padx=12, pady=(8, 5))
        
        # Area di testo per i file
        self.files_text = scrolledtext.ScrolledText(
            files_section,
            height=6,
            width=90,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            relief='flat',
            borderwidth=1
        )
        self.files_text.pack(fill='x', padx=12, pady=(0, 8))
        
        # Inserisci i valori predefiniti
        self.files_text.insert('1.0', ", ".join(sorted(self.current_exclusions['files'])))
    
    def _create_extensions_section(self):
        """Crea la sezione estensioni escluse"""
        extensions_section = ttk.LabelFrame(self.frame, text="🔤 Estensioni Escluse", style='Section.TLabelframe')
        extensions_section.pack(fill='x', pady=(0, 15), padx=15)
        
        # Etichetta
        extensions_label = tk.Label(
            extensions_section,
            text="Estensioni da escludere:",
            font=('Segoe UI', 10, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        extensions_label.pack(anchor='w', padx=12, pady=(8, 5))
        
        # Area di testo per le estensioni
        self.extensions_text = scrolledtext.ScrolledText(
            extensions_section,
            height=10,
            width=90,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            relief='flat',
            borderwidth=1
        )
        self.extensions_text.pack(fill='x', padx=12, pady=(0, 8))
        
        # Inserisci i valori predefiniti
        self.extensions_text.insert('1.0', ", ".join(sorted(self.current_exclusions['extensions'])))
    
    def _create_buttons(self):
        """Crea i pulsanti di gestione"""
        button_frame = tk.Frame(self.frame, bg='#1e1e1e')
        button_frame.pack(fill='x', pady=15, padx=15)
        
        # Pulsante salva
        save_btn = tk.Button(
            button_frame,
            text="💾 Salva Esclusioni",
            command=self._save_exclusions,
            bg='#388a34',
            fg='#000000',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            width=20
        )
        save_btn.pack(side='left', padx=5)
        
        # Pulsante reset
        reset_btn = tk.Button(
            button_frame,
            text="🔄 Ripristina Default",
            command=self._reset_exclusions,
            bg='#ce9178',
            fg='#000000',
            relief='flat',
            width=20
        )
        reset_btn.pack(side='left', padx=5)
        
        # Pulsante esporta
        export_btn = tk.Button(
            button_frame,
            text="📤 Esporta Configurazione",
            command=self._export_exclusions,
            bg='#569cd6',
            fg='#000000',
            relief='flat',
            width=20
        )
        export_btn.pack(side='left', padx=5)
        
        # Pulsante importa
        import_btn = tk.Button(
            button_frame,
            text="📥 Importa Configurazione",
            command=self._import_exclusions,
            bg='#9cdcfe',
            fg='#000000',
            relief='flat',
            width=20
        )
        import_btn.pack(side='left', padx=5)
    
    def _save_exclusions(self):
        """Salva le esclusioni dalle text area"""
        try:
            # Leggi i valori dalle text area
            dirs_text = self.dirs_text.get(1.0, tk.END).strip()
            files_text = self.files_text.get(1.0, tk.END).strip()
            extensions_text = self.extensions_text.get(1.0, tk.END).strip()
            
            # Parsifica i valori
            dirs = [d.strip() for d in dirs_text.split(',') if d.strip()]
            files = [f.strip() for f in files_text.split(',') if f.strip()]
            extensions = [e.strip() for e in extensions_text.split(',') if e.strip()]
            
            # Aggiorna le esclusioni correnti
            self.current_exclusions = {
                'dirs': set(dirs),
                'files': set(files),
                'extensions': set(extensions)
            }
            
            messagebox.showinfo("Successo", "Esclusioni salvate con successo!")
            self._show_status("Configurazione esclusioni salvata")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")
    
    def _reset_exclusions(self):
        """Ripristina le esclusioni predefinite"""
        self.current_exclusions = DEFAULT_EXCLUSIONS.copy()
        
        # Aggiorna le text area
        self.dirs_text.delete(1.0, tk.END)
        self.dirs_text.insert('1.0', ", ".join(sorted(self.current_exclusions['dirs'])))
        
        self.files_text.delete(1.0, tk.END)
        self.files_text.insert('1.0', ", ".join(sorted(self.current_exclusions['files'])))
        
        self.extensions_text.delete(1.0, tk.END)
        self.extensions_text.insert('1.0', ", ".join(sorted(self.current_exclusions['extensions'])))
        
        self._show_status("Esclusioni ripristinate ai valori predefiniti")
    
    def _export_exclusions(self):
        """Esporta la configurazione delle esclusioni"""
        try:
            path = filedialog.asksaveasfilename(
                title="📤 Esporta configurazione esclusioni",
                defaultextension=".txt",
                initialfile="exclusions_config.txt",
                filetypes=[("Text files", "*.txt"), ("Tutti i file", "*.*")]
            )
            
            if path:
                # Prepara il contenuto del file di configurazione
                config = f"""# SyncroNet - Advanced PDF Project Manager - Configurazione Esclusioni
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
                
                self._show_status(f"Configurazione esportata: {Path(path).name}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione: {str(e)}")
    
    def _import_exclusions(self):
        """Importa la configurazione delle esclusioni"""
        try:
            path = filedialog.askopenfilename(
                title="📥 Importa configurazione esclusioni",
                filetypes=[("Text files", "*.txt"), ("Tutti i file", "*.*")]
            )
            
            if path:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parsing del file di configurazione
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
                        extensions_content = section[11:].split('[')[0].strip()
                        self.extensions_text.delete(1.0, tk.END)
                        self.extensions_text.insert('1.0', extensions_content)
                
                self._show_status(f"Configurazione importata: {Path(path).name}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'importazione: {str(e)}")
    
    def get_current_exclusions(self):
        """Restituisce le esclusioni correnti"""
        try:
            dirs_text = self.dirs_text.get(1.0, tk.END).strip()
            files_text = self.files_text.get(1.0, tk.END).strip()
            extensions_text = self.extensions_text.get(1.0, tk.END).strip()
            
            return {
                'dirs': [d.strip() for d in dirs_text.split(',') if d.strip()],
                'files': [f.strip() for f in files_text.split(',') if f.strip()],
                'extensions': [e.strip() for e in extensions_text.split(',') if e.strip()]
            }
        except:
            return self.current_exclusions
    
    def _show_status(self, message):
        """Mostra un messaggio di status (da implementare nel main window)"""
        # Questo metodo sarà collegato al main window per aggiornare la status bar
        print(f"Status: {message}")