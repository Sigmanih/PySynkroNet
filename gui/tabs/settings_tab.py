"""
Scheda per le impostazioni e informazioni dell'applicazione
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from core.config import APP_CONFIG

class SettingsTab:
    """Scheda per le impostazioni e informazioni"""
    
    def __init__(self, parent):
        self.parent = parent
        self.title = "🔧 Impostazioni & Info"
        self._create_tab()
    
    def _create_tab(self):
        """Crea il contenuto della scheda"""
        self.frame = ttk.Frame(self.parent, style='Custom.TFrame')
        self._create_info_section()
        self._create_utils_section()
        self._create_about_section()
    
    def _create_info_section(self):
        """Crea la sezione informazioni applicazione"""
        info_section = ttk.LabelFrame(self.frame, text="ℹ️ Informazioni Applicazione", style='Section.TLabelframe')
        info_section.pack(fill='x', pady=(0, 15), padx=15)
        
        info_text = f"""
{APP_CONFIG['name']} - Versione {APP_CONFIG['version']}

🌟 Funzionalità Principali:
• 📄 Crea PDF da progetti (supporta tutti i tipi di file di testo/codice)
• 🔄 Ricrea progetti completi da PDF con indentazione perfetta
• ⚙️ Gestione avanzata delle esclusioni (file binari, immagini, etc.)
• 🎨 Interfaccia moderna con tema scuro e design intuitivo
• ⚡ Operazioni in background non bloccanti con progresso in tempo reale

🌐 Supporta:
• Python, JavaScript, Java, C++, C#, HTML, CSS, JSON, XML, Markdown
• Tutti i linguaggi di programmazione e file di testo
• Strutture progetto complesse con sottocartelle multiple

🛠️ Tecnologie:
• Python 3.8+ • Tkinter • PyPDF2 • Threading

🎯 Caratteristiche Uniche:
• Preservazione perfetta di indentazione e spaziatura originale
• Ricostruzione fedele della struttura del progetto
• Gestione intelligente delle esclusioni
• Report dettagliati di ricostruzione
        """
        
        info_label = tk.Label(
            info_section,
            text=info_text,
            justify='left',
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        info_label.pack(pady=12, padx=12, anchor='w')
    
    def _create_utils_section(self):
        """Crea la sezione utilità"""
        utils_section = ttk.LabelFrame(self.frame, text="🔧 Statistiche & Utilità", style='Section.TLabelframe')
        utils_section.pack(fill='x', pady=(0, 15), padx=15)
        
        # Frame per i pulsanti utilità
        utils_frame = tk.Frame(utils_section, bg='#1e1e1e')
        utils_frame.pack(fill='x', pady=12, padx=12)
        
        # Pulsante documentazione
        docs_btn = tk.Button(
            utils_frame,
            text="📚 Documentazione",
            command=self._open_documentation,
            bg='#0e639c',
            fg='#ffffff',
            font=('Segoe UI', 9),
            relief='flat',
            width=18
        )
        docs_btn.pack(side='left', padx=8)
        
        # Pulsante segnala bug
        bug_btn = tk.Button(
            utils_frame,
            text="🐛 Segnala Bug",
            command=self._report_bug,
            bg='#ce9178',
            fg='#000000',
            font=('Segoe UI', 9),
            relief='flat',
            width=18
        )
        bug_btn.pack(side='left', padx=8)
        
        # Pulsante suggerimenti
        suggest_btn = tk.Button(
            utils_frame,
            text="💡 Suggerimenti",
            command=self._suggest_features,
            bg='#569cd6',
            fg='#000000',
            font=('Segoe UI', 9),
            relief='flat',
            width=18
        )
        suggest_btn.pack(side='left', padx=8)
        
        # Pulsante aggiornamenti
        update_btn = tk.Button(
            utils_frame,
            text="🔄 Aggiornamenti",
            command=self._check_updates,
            bg='#388a34',
            fg='#000000',
            font=('Segoe UI', 9),
            relief='flat',
            width=18
        )
        update_btn.pack(side='left', padx=8)
    
    def _create_about_section(self):
        """Crea la sezione about"""
        about_section = ttk.LabelFrame(self.frame, text="👨‍💻 Informazioni Sviluppatore", style='Section.TLabelframe')
        about_section.pack(fill='x', pady=(0, 15), padx=15)
        
        about_text = f"""
{APP_CONFIG['name']}
👤 Sviluppatore: {APP_CONFIG['author']}
🚀 Versione: {APP_CONFIG['version']}
🔗 Repository: {APP_CONFIG['repository']}
📅 Data: Novembre 2025

⚖️ Licenza: MIT License
📄 Consulta il file LICENSE per i dettagli.

❤️ Sviluppato con Python e Tkinter
        """
        
        about_label = tk.Label(
            about_section,
            text=about_text,
            justify='left',
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        about_label.pack(pady=12, padx=12, anchor='w')
        
        # Pulsante repository
        repo_btn = tk.Button(
            about_section,
            text="🌐 Vai al Repository",
            command=self._open_repository,
            bg='#569cd6',
            fg='#000000',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            width=20
        )
        repo_btn.pack(pady=(0, 12), padx=12)
    
    def _open_documentation(self):
        """Apre la documentazione"""
        webbrowser.open(f"{APP_CONFIG['repository']}")
        self._show_status("Documentazione aperta nel browser")
    
    def _report_bug(self):
        """Apre la pagina per segnalare bug"""
        webbrowser.open(f"{APP_CONFIG['repository']}/issues/new")
        self._show_status("Pagina segnalazione bug aperta")
    
    def _suggest_features(self):
        """Apre la pagina per suggerimenti"""
        webbrowser.open(f"{APP_CONFIG['repository']}/discussions")
        self._show_status("Pagina suggerimenti aperta")
    
    def _check_updates(self):
        """Controlla gli aggiornamenti"""
        messagebox.showinfo(
            "Aggiornamenti", 
            "✅ Sei aggiornato all'ultima versione!\n\n"
            f"Versione corrente: {APP_CONFIG['version']}\n\n"
            "Per controllare aggiornamenti futuri, visita il repository GitHub."
        )
    
    def _open_repository(self):
        """Apre il repository GitHub"""
        webbrowser.open(APP_CONFIG['repository'])
        self._show_status("Repository GitHub aperto")
    
    def _show_status(self, message):
        """Mostra un messaggio di status (da implementare nel main window)"""
        # Questo metodo sarà collegato al main window per aggiornare la status bar
        print(f"Status: {message}")