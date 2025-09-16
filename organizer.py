
from pathlib import Path
import shutil
import json
from datetime import datetime

DEFAULT_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".odt", ".rtf"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Scripts": [".py", ".js", ".html", ".css", ".sh", ".bat"],
    "Code": [".py", ".java", ".cpp", ".js", ".html"],
    "PDF": [".pdf"],
    "PPT":[".pptx"],
    "Others": []


}

class Organizer:
    def __init__(self, folder_path, categories=None, log_file=None, dry_run=False):
        self.folder = Path(folder_path).expanduser().resolve()
        if not self.folder.exists() or not self.folder.is_dir():
            raise NotADirectoryError(f"Folder not found: {self.folder}")
        self.categories = categories if categories is not None else DEFAULT_CATEGORIES
        self.log_file = Path(log_file) if log_file else self.folder / ".organizer_log.json"
        self.dry_run = dry_run
        # Load existing log if present
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.log = json.load(f)
            except Exception:
                self.log = {"runs": []}
        else:
            self.log = {"runs": []}

    def _category_for_ext(self, ext):
        ext = ext.lower()
        for cat, exts in self.categories.items():
            if ext in exts:
                return cat
        return None

    def _ensure_folder(self, name):
        p = self.folder / name
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _unique_destination(self, dest):
        """If dest exists, append a numeric suffix to filename."""
        dest = Path(dest)
        if not dest.exists():
            return dest
        stem = dest.stem
        suffix = dest.suffix
        parent = dest.parent
        i = 1
        while True:
            new_name = f"{stem} ({i}){suffix}"
            candidate = parent / new_name
            if not candidate.exists():
                return candidate
            i += 1

    def organize(self, show_progress=None):
        """Organize files in self.folder. show_progress is optional callback(name_str)."""
        moved_entries = []
        for item in self.folder.iterdir():
            if item.is_dir() and item.name.startswith('.'):
                # skip hidden directories like .git or .organizer data
                continue
            if item.is_dir():
                continue  # skip directories (we only organize files in top-level)
            ext = item.suffix.lower()
            category = self._category_for_ext(ext)
            if category is None:
                dest_folder = self._ensure_folder('Others')
            else:
                dest_folder = self._ensure_folder(category)
            dest = dest_folder / item.name
            dest = self._unique_destination(dest)
            if show_progress:
                show_progress(f"Moving {item.name} → {dest_folder.name}")
            if not self.dry_run:
                shutil.move(str(item), str(dest))
            moved_entries.append({
                "src": str(item),
                "dest": str(dest),
            })
        # write run log
        run_entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "moved": moved_entries
        }
        self.log['runs'].append(run_entry)
        if not self.dry_run:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.log, f, indent=2)
        return moved_entries

    def last_run(self):
        if not self.log.get('runs'):
            return None
        return self.log['runs'][-1]

    def undo_last(self):
        """Undo the last run by moving files back to original locations recorded in the log."""
        if not self.log.get('runs'):
            return 0
        last = self.log['runs'].pop()  # remove last run
        moved = 0
        errors = []
        for entry in last.get('moved', []):
            src = Path(entry['dest'])
            dest = Path(entry['src'])
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    shutil.move(str(src), str(dest))
                    moved += 1
            except Exception as e:
                errors.append(str(e))
        # overwrite log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2)
        return {"restored": moved, "errors": errors}
