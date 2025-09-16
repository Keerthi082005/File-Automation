# File-Automation

**Description:**

The File Organizer is a desktop tool that scans a chosen folder and organizes files into subfolders based on file extensions (Images, Documents, Videos, Music, Archives, Scripts, Others). It supports undoing the last organization by restoring files to their original locations using a log file (.organizer_log.json).

## Features
- Organizes files into category folders.
- Handles duplicate file names by appending a numeric suffix.
- Keeps a JSON run log to allow undoing the last organization.
- Simple Tkinter GUI with browse, organize, and undo buttons.
- Cross-platform (Windows / macOS / Linux) (requires Python + Tkinter).

## Requirements
- Python 3.8+
- No external packages required (only standard library).

## How to run
1. Extract the project.
2. Run the GUI:

   ```bash
   python gui.py
   ```
3. Use **Browse** to pick a folder and click **Organize Now**.

4. To undo the last run, make sure to select the same folder and click **Undo Last**.

## Project Structure
- `organizer.py` - core organizing logic.
- `gui.py` - tkinter user interface.
- `.organizer_log.json` - generated at runtime in the target folder to record moves.
- `README.md` - this file.

## Notes & Safety
- The script moves files (not copies). Make backups if needed before running on important folders.
- The undo feature reverts only the last run recorded in `.organizer_log.json`.
