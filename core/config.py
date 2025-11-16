"""
Configurazioni e costanti dell'applicazione
"""

DEFAULT_EXCLUSIONS = {
    'dirs': {
        'venv', '.venv', '__pycache__', '.git', '.vscode', '.idea',
        'node_modules', 'build', 'dist', 'models2', '.continue',
        '.vs', 'target', 'out', 'bin', 'obj', 'packages', '.gradle',
        '.settings', '.metadata', '.recommenders', 'gradle', 'jvm',
        '__pypackages__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
        '.coverage', 'htmlcov', '.tox', '.eggs', '*.egg-info',
        '.terraform', '.serverless', '.next', '.nuxt', '.output',
        '.svelte-kit', '.astro', '.cache', '.parcel-cache', ".test"
    },
    'files': {
        #'config.py', 'settings.py', 
        'local_settings.py', '.env',
        '.gitignore', '.gitattributes', '.env.local', '.env.production',
        'package-lock.json', 'yarn.lock', 'thumbs.db', '.DS_Store',
        'desktop.ini', '*tmp', '*temp', '.python-version', '.ruby-version',
        '.node-version', '.nvmrc', '.editorconfig', '.prettierignore',
        '.eslintignore', '.stylelintignore', '.dockerignore',
        'composer.lock', 'Gemfile.lock', 'Pipfile.lock', 'poetry.lock',
        'Cargo.lock', 'go.sum', 'mix.lock', 'yarn-error.log',
        'npm-debug.log', '.htaccess', '.htpasswd', 'web.config',
        'robots.txt', 'sitemap.xml', '.code-workspace'
    },
    'extensions': {
        # File binari eseguibili e librerie
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.dylib', '.bundle',
        '.app', '.apk', '.ipa', '.deb', '.rpm', '.msi', '.com', '.bat',
        '.cmd', '.sh', '.bash', '.ps1', '.vbs', '.jar', '.war', '.ear',
        
        # Modelli AI e machine learning
        '.safetensors', '.bin', '.pkl', '.pickle', '.joblib', '.h5', '.hdf5',
        '.model', '.pb', '.tflite', '.onnx', '.pt', '.pth', '.ckpt',
        
        # Immagini
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
        '.ico', '.icns', '.svg', '.eps', '.ai', '.psd', '.xcf', '.kra',
        '.raw', '.cr2', '.nef', '.arw', '.dng',
        
        # Documenti (non di testo semplice)
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.odt', '.ods', '.odp', '.pages', '.numbers', '.key',
        '.epub', '.mobi', '.azw', '.azw3',
        
        # Archivi e compressione
        '.zip', '.rar', '.7z', '.tar', '.gz', '.tgz', '.bz2', '.tbz2',
        '.xz', '.txz', '.lz', '.lzma', '.arc', '.arj', '.z', '.zipx',
        
        # Audio
        '.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a', '.wma', '.aiff',
        '.ape', '.opus', '.mid', '.midi', '.kar',
        
        # Video
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v',
        '.3gp', '.3g2', '.mpeg', '.mpg', '.vob', '.ogv', '.rm', '.rmvb',
        
        # Database e file di dati binari
        '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.pdb', '.idb',
        '.frm', '.myd', '.myi', '.ibd', '.dbf', '.mdf', '.ldf',
        
        # File di sistema e configurazione binaria
        '.class', '.metadata', '.swp', '.swo', '.swn', '.bak', '.tmp',
        '.temp', '.cache', '.log', '.out', '.err',
        
        # Font
        '.ttf', '.otf', '.woff', '.woff2', '.eot', '.pfb', '.pfm',
        
        # File CAD e grafica 3D
        '.dwg', '.dxf', '.stl', '.obj', '.fbx', '.blend', '.max', '.ma',
        '.mb', '.3ds', '.iges', '.step', '.stp',
        
        # File virtuali e di virtualizzazione
        '.iso', '.img', '.vmdk', '.vhd', '.vhdx', '.ova', '.ovf',
        
        # File crittografici e di sicurezza
        '.pem', '.key', '.crt', '.cer', '.der', '.p7b', '.p7c', '.p12',
        '.pfx', '.jks', '.keystore', '.gpg', '.pgp',
        
        # File di backup e snapshot
        '.bak', '.backup', '.old', '.orig', '.save', '.snapshot',
        
        # File di log binari
        '.log', '.event', '.evtx', '.etl',
        
        # File di memoria e dump
        '.dmp', '.core', '.hprof', '.heap',
        
        # File di installazione e pacchetti
        '.msm', '.msp', '.mst', '.pkg', '.dmg', '.appimage',
        
        # File di gioco e risorse binarie
        '.unitypackage', '.asset', '.resources', '.pak', '.bundle',
        
        # File di configurazione binaria
        '.plist', '.dat', '.bin', '.data', '.idx',
        
        # File di lock e temporanei specifici
        '.lock', '.lck', '.pid', '.socket', '.fifo',
        
        # File di virtual environment
        '.pyenv', '.conda', '.pip', '.wheel',
        
        # File di container e orchestrazione
        '.docker', '.oci', '.oci-image', '.tar.gz',
        
        # File di blockchain e cryptocurrency
        '.wallet', '.block', '.chain', '.dat'
    }
}

APP_CONFIG = {
    'name': 'SyncroNet - Advanced PDF Project Manager',
    'version': '3.0',
    'author': 'Sigmanih',
    'repository': 'https://github.com/Sigmanih/PySyncroNet'
}

SUPPORTED_ENCODINGS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'ascii', 'utf-16', 'utf-32']
MAX_LINE_WIDTH = 100