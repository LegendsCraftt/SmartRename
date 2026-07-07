# Smart Rename

Smart Rename is a desktop file renaming tool built with PyQt6 for batch operations such as removing characters, deleting exact strings, and cleaning whitespace in filenames.

Created by [Tyler Emery](https://github.com/TylerBuilds-Official)  
Version: `v1.0.1`  
License: [MIT](LICENSE)

## Features

- Drag-and-drop file selection or file picker mode
- Remove characters from the start or end of filenames
- Remove exact strings from filenames
- Remove all spaces from filenames
- Preview rename results before applying changes
- Undo the most recent rename operation
- Automatic logging to `Documents/smart_rename_log.txt`
- Clean, dark-themed user interface

## Download

[Download the latest Windows `.exe` release](https://github.com/TylerBuilds-Official/SmartRename/releases/latest)

**Windows note:**  
You may see a Microsoft SmartScreen warning the first time you launch the app.  
Select **More info** and then **Run anyway** to continue. This is common for unsigned applications.

## Usage

1. Launch `SmartRename.exe`.
2. Add files by dragging and dropping them, or by clicking **Open Files** in File Mode.
3. Configure rename options:
   - Remove a set number of characters from the start or end
   - Remove a specific string
   - Remove all spaces
4. Click **Preview Changes**.
5. Click **Apply Changes**.
6. Optional: click **Undo** to revert the latest rename operation.

## Logging

All rename operations are written to:

- `Documents/smart_rename_log.txt`

The log includes original and updated filenames with timestamps.

## Built With

- Python 3.11+
- PyQt6
- Python `logging` module

## Support

For bug reports or feature requests, open an [issue on GitHub](https://github.com/TylerBuilds-Official/SmartRename/issues).

## License

This project is licensed under the [MIT License](LICENSE).
