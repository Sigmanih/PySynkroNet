#File: folder_to_pdf.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import sys
import webbrowser
from datetime import datetime
from fpdf import FPDF


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
        """Aggiunge il contenuto di un file al PDF"""
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
                content = f"[Impossibile leggere il file {file_path} - formato binario o codifica sconosciuta]"
                
        except Exception as e:
            content = f"[Errore nella lettura del file {file_path}: {str(e)}]"
        
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
        self.pdf.set_font('Courier', '', 8)  # Dimensione font più piccola per più contenuto
        
        # Dividi il contenuto in linee e aggiungi al PDF
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Pulisci ogni linea
            clean_line = self.clean_text(line)
            
            # Gestisci linee troppo lunghe
            if len(clean_line) > 120:
                # Tronca le linee molto lunghe
                clean_line = clean_line[:120] + "... [troncato]"
            
            # Aggiungi numero di linea
            line_number = f"{i:4d} | {clean_line}"
            self.pdf.cell(0, 4, line_number, ln=True)  # Altezza linea più piccola
    
    def create_pdf(self, project_path, output_pdf="project_documentation.pdf", custom_exclusions=None):
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
        
        # Informazioni sulle esclusioni
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, "Cartelle escluse:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        for excluded_dir in sorted(self.excluded_dirs):
            self.pdf.cell(0, 5, f"  - {excluded_dir}", ln=True)
        
        self.pdf.ln(5)
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, "File esclusi:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        for excluded_file in sorted(self.excluded_files):
            self.pdf.cell(0, 5, f"  - {excluded_file}", ln=True)
        
        self.pdf.ln(5)
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, "Estensioni escluse:", ln=True)
        self.pdf.set_font('Arial', '', 10)
        for excluded_ext in sorted(self.excluded_extensions):
            self.pdf.cell(0, 5, f"  - {excluded_ext}", ln=True)
        
        # Elenco dei file processati
        processed_files = []
        
        # Cerca ricorsivamente tutti i file
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_path)
                
                if not self.should_exclude(file_path, relative_path):
                    processed_files.append(str(relative_path))
                    self.add_file_to_pdf(file_path, relative_path)
        
        # Salva il PDF
        self.pdf.output(output_pdf)
        return len(processed_files)


class UniversalPDFToProject:
    def __init__(self):
        pass
        
    def recreate_project_structure(self, pdf_path, output_folder):
        """Placeholder per la ricostruzione del progetto"""
        # Per ora restituiamo True per simulare il successo
        # Implementa qui la logica di ricostruzione dal PDF
        return True


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

    # ... (tutto il resto del codice dell'interfaccia rimane uguale) ...

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
            
            # Crea il PDF
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

    # ... (il resto del codice rimane invariato) ...

def main():
    root = tk.Tk()
    app = AdvancedPDFProjectManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()