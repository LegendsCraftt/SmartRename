import os
from pathlib import Path

from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QListWidgetItem, QFileDialog, QMessageBox, QToolTip

from logger import LOG_PATH, logger


class MainController:
    def __init__(self, view):
        self.view = view

    def SetEndState(self, state):
        self.view.end_check.setEnabled(not state)
        self.view.remove_string_check.setEnabled(not state)
        self.view.remove_string_text.setEnabled(not state)


    def SetStartState(self, state):
        self.view.start_check.setEnabled(not state)
        self.view.remove_string_check.setEnabled(not state)
        self.view.remove_string_text.setEnabled(not state)


    def UseExactString(self, state):
        self.view.chars_to_remove.setEnabled(not state)
        self.view.start_check.setEnabled(not state)
        self.view.start_check.setChecked(False)
        self.view.end_check.setEnabled(not state)
        self.view.end_check.setChecked(False)
        self.view.chars_to_remove.clear()




    def OpenFiles(self):
        if self.view.use_files_check.isChecked():
            files, _ = QFileDialog.getOpenFileNames(self.view, 'Select Files to rename')
            if files:
                self.view.files_preview.clear()
                for file in files:
                    self.view.files_preview.addItem(file)


    def openLog(self):
        path = str(LOG_PATH)
        if not Path(path).exists():
            QMessageBox.information(self.view, "Log not found", f"No log file at:\n{path}")
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(path))


    def ClearFiles(self):
        self.view.files_preview.clear()
        self.view.output_view.clear()


    def ClearFile(self):
        item = self.view.files_preview.currentItem()
        if item is not None:
            row = self.view.files_preview.row(item)
            self.view.files_preview.takeItem(row)


    def ResetSettings(self):
        self.view.start_check.setChecked(False)
        self.view.end_check.setChecked(False)
        self.view.remove_spaces_check.setChecked(False)
        self.view.remove_string_check.setChecked(False)
        self.view.chars_to_remove.clear()
        self.view.remove_string_text.clear()


    def Undo(self):
        while self.view.rename_history:
            old_path, new_path = self.view.rename_history.pop()
            dirname, fname = os.path.split(old_path)
            ndirname, nfname = os.path.split(new_path)
            try:
                os.rename(new_path, old_path)
                self.view.output_view.addItem(f'Undo Complete for {nfname} ❯❯❯❯ {fname}')
            except Exception as e:
                self.view.output_view.addItem(f'Undo failed for {nfname}: {e}')


    def TransformName(self, name: str, chars: int = 0, from_start: bool = False, from_end: bool = False,
                      remove_spaces: bool = False, exact_str: str = '') -> str:
        if chars > 0:
            if from_start:
                name = name[chars:]

            if from_end:
                name = name[:-chars]

        if exact_str:
            name = name.replace(exact_str, '')

        if remove_spaces:
            name = name.replace(' ', '')
        return name


    def OnPreview(self):
        chars = 0

        if not self.view.remove_string_check.isChecked():
            chars_text = self.view.chars_to_remove.text().strip()
            if chars_text.isdigit():
                chars = int(chars_text)

        from_start = self.view.start_check.isChecked()
        from_end = self.view.end_check.isChecked()
        remove_spaces = self.view.remove_spaces_check.isChecked()
        exact_string = self.view.remove_string_text.text() if self.view.remove_string_check.isChecked() else ''

        for idx in range(self.view.files_preview.count()):
            item = self.view.files_preview.item(idx)
            full_path = item.data(Qt.ItemDataRole.UserRole)
            dirname, fname = os.path.split(full_path)
            base, ext = os.path.splitext(fname)

            new_base = self.TransformName(base, chars, from_start, from_end, remove_spaces, exact_string)

            self.view.output_view.addItem(f'{fname} ❯❯❯❯ {new_base + ext}')


    def OnApply(self):
        self.view.output_view.clear()

        changes_applied = False

        chars = 0  # default

        if not self.view.remove_string_check.isChecked():
            chars_text = self.view.chars_to_remove.text().strip()
            if chars_text.isdigit():
                chars = int(chars_text)

        from_start = self.view.start_check.isChecked()
        from_end = self.view.end_check.isChecked()
        remove_spaces = self.view.remove_spaces_check.isChecked()
        exact_string = self.view.remove_string_text.text() if self.view.remove_string_check.isChecked() else ''

        for idx in range(self.view.files_preview.count()):
            item = self.view.files_preview.item(idx)
            full_path = item.data(Qt.ItemDataRole.UserRole)
            dirname, fname = os.path.split(full_path)
            base, ext = os.path.splitext(fname)

            new_base = self.TransformName(base, chars, from_start, from_end, remove_spaces, exact_string)
            new_path = os.path.join(dirname, new_base + ext)
            self.view.rename_history.append((full_path, new_path))

            try:
                os.rename(full_path, new_path)
                logger.info(f'"{full_path}" → "{new_path}"')
                changes_applied = True

            except Exception as e:
                self.view.output_view.addItem(f'Failed to rename {fname}: Error: {e}')

        if changes_applied:
            self.OnPreview()
            self.view.output_view.addItem(f'Changes Applied!')


    def showInvalidTooltip(self):
        pos = self.view.chars_to_remove.mapToGlobal(
            QPoint(0, self.view.chars_to_remove.height())
        )
        QToolTip.showText(
            pos,
            "Only whole numbers allowed",
            self.view.chars_to_remove,
            self.view.chars_to_remove.rect(),
            1325
        )