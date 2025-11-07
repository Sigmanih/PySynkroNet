#File: pdf_to_folder.py
import re
import os
import PyPDF2
from pathlib import Path
import datetime

class UniversalPDFToProject:
    def __init__(self):
        self.files_data = {}
        self.metadata = {}
        
    def extract_pdf_content(self, pdf_path):
        """Estrae il contenuto dal PDF con gestione errori migliorata"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    full_text += page_text + "\n"
                
                return full_text
        except Exception as e:
            print(f"Errore nell'estrazione del PDF: {e}")
            return None

    def parse_files_from_pdf(self, pdf_text):
        """Analizza il PDF e estrae tutti i file con il loro contenuto"""
        lines = pdf_text.split('\n')
        current_file = None
        current_content = []
        reading_file_content = False
        
        for line in lines:
            line = line.strip()
            
            # Cerca l'inizio di un nuovo file
            if line.startswith('File:'):
                # Salva il file precedente se esiste
                if current_file and current_content:
                    # Unisci il contenuto e pulisci
                    full_content = '\n'.join(current_content).strip()
                    if full_content:
                        self.files_data[current_file] = full_content
                
                # Inizia un nuovo file
                file_path = line[5:].strip()  # Rimuove "File:"
                current_file = file_path
                current_content = []
                reading_file_content = True
                continue
            
            # Se stiamo leggendo il contenuto di un file e non è una linea di metadati
            if (reading_file_content and current_file and 
                line and 
                not line.startswith('DOCUMENTAZIONE') and
                not line.startswith('Cartelle') and
                not line.startswith('File') and
                not line.startswith('Estensioni') and
                not line.startswith('Progetto:') and
                not line.startswith('Cartella:')):
                
                # Gestisce le linee numerate (pattern: "123 | contenuto")
                line_match = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', line)
                if line_match:
                    content_part = line_match.group(2)
                    current_content.append(content_part)
                else:
                    # Se non è una linea numerata ma abbiamo contenuto, potrebbe essere continuazione
                    if current_content and not re.match(r'^\s*\d+\s*\|', line):
                        current_content[-1] += ' ' + line
                    elif line:  # Nuova linea di contenuto
                        current_content.append(line)
        
        # Salva l'ultimo file
        if current_file and current_content:
            full_content = '\n'.join(current_content).strip()
            if full_content:
                self.files_data[current_file] = full_content
        
        return self.files_data

    def clean_file_content(self, content, file_extension):
        """Pulisce il contenuto in base al tipo di file"""
        if not content:
            return content
            
        # Rimuove i tag [troncato] se presenti
        content = content.replace('... [troncato]', '')
        
        # Gestione specifica per diversi tipi di file
        if file_extension in ['.py', '.js', '.java', '.c', '.cpp', '.h', '.cs']:
            # Linguaggi di programmazione - corregge l'indentazione
            content = self.fix_code_indentation(content)
        elif file_extension in ['.html', '.xml', '.svg']:
            # File markup - corregge la formattazione
            content = self.fix_markup_formatting(content)
        elif file_extension in ['.json']:
            # JSON - tenta di correggere la formattazione
            content = self.fix_json_formatting(content)
        elif file_extension in ['.css', '.scss', '.less']:
            # CSS - corregge la formattazione
            content = self.fix_css_formatting(content)
        elif file_extension in ['.md', '.rst', '.txt']:
            # Documentazione - pulizia base
            content = self.fix_text_formatting(content)
        
        return content

    def fix_code_indentation(self, content):
        """Corregge l'indentazione per codice sorgente"""
        lines = content.split('\n')
        fixed_lines = []
        indent_level = 0
        in_multiline_string = False
        string_delimiter = None
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fixed_lines.append('')
                continue
            
            # Gestione stringhe multilinea
            if not in_multiline_string:
                if '"""' in stripped or "'''" in stripped:
                    in_multiline_string = True
                    string_delimiter = '"""' if '"""' in stripped else "'''"
            else:
                if string_delimiter in stripped:
                    in_multiline_string = False
            
            if in_multiline_string:
                fixed_lines.append('    ' * indent_level + stripped)
                continue
            
            # Calcola indentazione per codice
            line_indent = 0
            
            # Riduci indentazione per certe keyword
            if (stripped.startswith(('return', 'break', 'continue', 'pass')) or
                stripped in ('else:', 'elif:', 'except:', 'finally:')):
                line_indent = max(0, indent_level - 1)
            else:
                line_indent = indent_level
            
            fixed_lines.append('    ' * line_indent + stripped)
            
            # Aumenta indentazione dopo certe strutture
            if (stripped.endswith(':') and 
                not stripped.startswith('#') and
                not any(stripped.startswith(kw) for kw in ['import', 'from', 'def ', 'class '])):
                indent_level += 1
            # Riduci indentazione per fine blocco implicito
            elif stripped in ['return', 'break', 'continue', 'pass']:
                indent_level = max(0, indent_level - 1)
        
        return '\n'.join(fixed_lines)

    def fix_markup_formatting(self, content):
        """Corregge la formattazione per file markup (HTML, XML, etc.)"""
        # Unisce tag che potrebbero essere stati spezzati
        content = re.sub(r'<\s*/\s*(\w+)\s*>', r'</\1>', content)
        content = re.sub(r'<(\w+)([^>]*)>\s*<\s*/\s*\1\s*>', r'<\1\2></\1>', content)
        
        lines = content.split('\n')
        fixed_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fixed_lines.append('')
                continue
            
            # Gestione tag di chiusura
            if stripped.startswith('</'):
                indent_level = max(0, indent_level - 1)
            
            fixed_lines.append('  ' * indent_level + stripped)
            
            # Gestione tag di apertura (non auto-chiusi)
            if (stripped.startswith('<') and 
                not stripped.startswith('</') and 
                not stripped.endswith('/>') and
                not '<!--' in stripped and
                not stripped.endswith('-->')):
                indent_level += 1
        
        return '\n'.join(fixed_lines)

    def fix_json_formatting(self, content):
        """Corregge la formattazione JSON"""
        try:
            # Tenta di parsare e riformattare il JSON
            import json
            parsed = json.loads(content)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except:
            # Se il parsing fallisce, fa del suo meglio
            content = re.sub(r',\s*', ', ', content)
            content = re.sub(r':\s*', ': ', content)
            return content

    def fix_css_formatting(self, content):
        """Corregge la formattazione CSS"""
        lines = content.split('\n')
        fixed_lines = []
        in_rule = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fixed_lines.append('')
                continue
            
            if stripped.endswith('{'):
                fixed_lines.append(stripped)
                in_rule = True
            elif stripped == '}':
                fixed_lines.append(stripped)
                in_rule = False
            elif in_rule:
                fixed_lines.append('  ' + stripped)
            else:
                fixed_lines.append(stripped)
        
        return '\n'.join(fixed_lines)

    def fix_text_formatting(self, content):
        """Corregge la formattazione per file di testo"""
        # Unisce paragrafi spezzati
        lines = content.split('\n')
        fixed_lines = []
        current_paragraph = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_paragraph:
                    fixed_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                fixed_lines.append('')
            elif stripped.startswith(('#', '-', '*', '>')):  # Mantiene formattazione markdown
                if current_paragraph:
                    fixed_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                fixed_lines.append(stripped)
            else:
                current_paragraph.append(stripped)
        
        if current_paragraph:
            fixed_lines.append(' '.join(current_paragraph))
        
        return '\n'.join(fixed_lines)

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
        
        print("🔍 Analizzando il contenuto del PDF...")
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
                
                # Pulisci il contenuto in base al tipo di file
                cleaned_content = self.clean_file_content(raw_content, file_extension)
                
                # Scrivi il file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                files_created += 1
                print(f"✅ Creato: {file_path}")
                
            except Exception as e:
                error_msg = f"❌ Errore con {file_path}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        # Scrivi un report di ricostruzione
        self.write_reconstruction_report(output_path, files_created, errors, files_data)
        
        print(f"\n🎉 Ricostruzione completata!")
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
            report_content += f"- {file_path} ({file_extension}, {content_length} caratteri)\n"

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

        with open(output_path / "RICOSTRUZIONE_REPORT.txt", 'w', encoding='utf-8') as f:
            f.write(report_content)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ricrea un intero progetto da PDF - Supporta qualsiasi tipo di file di testo/codice'
    )
    parser.add_argument('pdf_path', help='Percorso del PDF sorgente')
    parser.add_argument('output_folder', help='Cartella di destinazione per il progetto ricostruito')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"❌ Errore: Il file PDF '{args.pdf_path}' non esiste.")
        return
    
    print("🛠️  Ricostruzione progetto da PDF")
    print("=" * 50)
    
    recreator = UniversalPDFToProject()
    success = recreator.recreate_project_structure(args.pdf_path, args.output_folder)
    
    if success:
        print("\n✅ Ricostruzione completata con successo!")
        print(f"📁 Il progetto è stato ricreato in: {args.output_folder}")
    else:
        print("\n❌ Ricostruzione fallita!")

if __name__ == "__main__":
    # Esempio di utilizzo diretto
    if len(os.sys.argv) == 1:
        print("Ricostruzione progetto da PDF")
        print("=" * 40)
        
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