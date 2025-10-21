import os
from pathlib import Path

from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtGui import QDesktopServices, QAction
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QToolTip, QMenu

from custom_widgets.logger import LOG_PATH, logger
from data.settings import get_saved_rm_strings, add_saved_rm_string, reset_setting, remove_saved_rm_string


class MainController:
    def __init__(self, view):
        self.view = view

    def set_end_state(self, state):
        self.view.end_check.setEnabled(not state)
        self.view.remove_string_check.setEnabled(not state)
        self.view.remove_string_text.setEnabled(not state)


    def set_start_state(self, state):
        self.view.start_check.setEnabled(not state)
        self.view.remove_string_check.setEnabled(not state)
        self.view.remove_string_text.setEnabled(not state)


    def use_exact_string(self, state):
        self.view.chars_to_remove.setEnabled(not state)
        self.view.start_check.setEnabled(not state)
        self.view.start_check.setChecked(False)
        self.view.end_check.setEnabled(not state)
        self.view.end_check.setChecked(False)
        self.view.chars_to_remove.clear()




    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self.view, 'Select Files to rename')
        if files:
            self.view.files_preview.clear()
            for file in files:
                self.view.files_preview.addItem(file)


    def open_log(self):
        path = str(LOG_PATH)
        if not Path(path).exists():
            QMessageBox.information(self.view, "Log not found", f"No log file at:\n{path}")
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(path))


    def clear_files(self):
        self.view.files_preview.clear()
        self.view.output_view.clear()
        self.clear_undo_cache()


    def clear_file(self):
        items = self.view.files_preview.selectedItems()
        if items is not None:
            for item in items:
                row = self.view.files_preview.row(item)
                self.view.files_preview.takeItem(row)


    def reset_settings(self):
        self.view.start_check.setChecked(False)
        self.view.end_check.setChecked(False)
        self.view.remove_spaces_check.setChecked(False)
        self.view.remove_string_check.setChecked(False)
        self.view.chars_to_remove.clear()
        self.view.remove_string_text.clear()


    def undo(self):

        if not self.view.rename_history['undo']:
            self.view.output_view.addItem('Nothing to undo!')
            return

        undone, failed = 0, 0

        while self.view.rename_history['undo']:
            old_path, new_path = self.view.rename_history['undo'].pop()
            dirname, fname = os.path.split(old_path)
            ndirname, nfname = os.path.split(new_path)

            try:
                if not os.path.exists(new_path):
                    raise FileNotFoundError(f'File not found: {new_path}')

                if os.path.exists(old_path):
                    raise FileExistsError(f'File already exists: {old_path}')

                os.rename(new_path, old_path)
                self.view.rename_history['redo'].append((old_path, new_path))
                self.view.output_view.addItem(f'Undo Complete for {nfname} ❯❯❯❯ {fname}')
                undone += 1

            except Exception as e:
                self.view.output_view.addItem(f'Undo failed for {nfname}: {e}')
                failed += 1

        summary = f'Undo Complete! {undone} files undone, {failed} files failed.'
        self.view.output_view.addItem(summary)


    def redo(self):
        if not self.view.rename_history['redo']:
            self.view.output_view.addItem('Nothing to redo!')
            return

        redone, failed = 0, 0

        while self.view.rename_history['redo']:
            old_path, new_path = self.view.rename_history['redo'].pop()
            dirname, fname = os.path.split(old_path)
            ndirname, nfname = os.path.split(new_path)

            try:
                if not os.path.exists(old_path):
                    raise FileNotFoundError(f'File not found: {old_path}')
                if os.path.exists(new_path):
                    raise FileExistsError(f'File already exists: {new_path}')

                os.rename(old_path, new_path)
                self.view.rename_history['undo'].append((old_path, new_path))
                self.view.output_view.addItem(f'Redo Complete for {fname} ❯❯❯❯ {nfname}')
                redone += 1

            except Exception as e:
                self.view.output_view.addItem(f'Redo failed for {fname}: {e}')
                failed += 1
        summary = f'Redo Complete! {redone} files redone, {failed} files failed.'
        self.view.output_view.addItem(summary)


    def clear_rename_history(self):
        self.view.rename_history = {'undo': [],
                                    'redo': []}


    def transform_name(self, name: str, chars: int = 0, from_start: bool = False, from_end: bool = False,
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


    def on_preview(self):
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

            new_base = self.transform_name(base, chars, from_start, from_end, remove_spaces, exact_string)

            self.view.output_view.addItem(f'{fname} ❯❯❯❯ {new_base + ext}')


    def on_apply(self):
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

            new_base = self.transform_name(base, chars, from_start, from_end, remove_spaces, exact_string)
            new_path = os.path.join(dirname, new_base + ext)
            self.view.rename_history['undo'].append((full_path, new_path))
            self.view.rename_history['redo'].clear()

            try:
                os.rename(full_path, new_path)
                logger.info(f'"{full_path}" → "{new_path}"')
                changes_applied = True

            except Exception as e:
                self.view.output_view.addItem(f'Failed to rename {fname}: Error: {e}')

        if changes_applied:
            self.on_preview()
            self.view.output_view.addItem(f'Changes Applied!')


    def show_invalid_tooltip(self):
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

    def show_rm_str_context_menu(self, pos):
        menu = self.view.remove_string_text.createStandardContextMenu()

        menu.addSeparator()
        saved_strings = self._get_saved_rm_strngs() or []
        if saved_strings:
            submenu = QMenu("Insert Saved String", self.view)
            for s in saved_strings:
                act = QAction(s, self.view)
                act.triggered.connect(lambda _, text=s: self.insert_rm_str(text))
                submenu.addAction(act)
            menu.addMenu(submenu)
        else:
            act = QAction("(no saved strings)", self.view)
            act.setEnabled(False)
            menu.addAction(act)

        menu.addSeparator()
        add_current = QAction("Save Current Value", self.view)
        add_current.triggered.connect(lambda: self.add_remove_string(self.view.remove_string_text.text()))
        menu.addAction(add_current)

        clear_saved = QAction("Clear Saved Strings", self.view)
        clear_saved.triggered.connect(lambda: self.clear_saved_strings())
        menu.addAction(clear_saved)

        menu.exec(self.view.remove_string_text.mapToGlobal(pos))



    def _get_saved_rm_strngs(self):
        return get_saved_rm_strings()

    def add_remove_string(self, string):
        add_saved_rm_string(string)

    def save_remove_strings(self, strings):
        if strings:
            for s in strings:
                add_saved_rm_string(s)

    def remove_saved_string(self, string):
        remove_saved_rm_string(string)

    def clear_saved_strings(self):
        reset_setting('removeStringsSaved')

    def insert_rm_str(self, string):
        self.view.remove_string_text.clear()
        self.view.remove_string_text.insert(string)









