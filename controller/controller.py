import os
from pathlib import Path

from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtGui import QDesktopServices, QAction, QIntValidator
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QMenu, QListWidgetItem

from custom_widgets.logger import LOG_PATH, logger
from data.settings import get_saved_rm_strings, add_saved_rm_string, reset_setting, remove_saved_rm_string
from ui.about import About
from ui.shortcuts import Shortcuts


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
        self.view.replace_string_check.setChecked(False)
        self.view.replace_string_check.setEnabled(not state)
        self.view.replace_string_text.setEnabled(not state)
        self.view.replace_string_replace_text.setEnabled(not state)
        self.view.replace_string_replace_text.clear()
        self.view.replace_string_text.clear()
        self.view.chars_to_remove.clear()

    def replace_string(self, state):
        self.view.chars_to_remove.setEnabled(not state)
        self.view.start_check.setEnabled(not state)
        self.view.start_check.setChecked(False)
        self.view.end_check.setEnabled(not state)
        self.view.end_check.setChecked(False)
        self.view.chars_to_remove.clear()
        self.view.remove_string_check.setChecked(False)
        self.view.remove_string_check.setEnabled(not state)
        self.view.remove_string_text.setEnabled(not state)
        self.view.remove_string_text.clear()

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self.view, 'Select Files to rename')
        if files:
            self.view.files_preview.clear()
            for file in files:
                item = QListWidgetItem(os.path.basename(file))
                item.setData(Qt.ItemDataRole.UserRole, file)
                self.view.files_preview.addItem(item)

    def open_log(self):
        path = str(LOG_PATH)
        if not Path(path).exists():
            QMessageBox.information(self.view, "Log not found", f"No log file at:\n{path}")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def clear_files(self):
        self.view.files_preview.clear()
        self.view.output_view.clear()
        self.clear_rename_history()

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

        batch = self.view.rename_history['undo'].pop()
        redo_batch = []
        undone, skipped, failed = 0, 0, 0
        directory_for_refresh = None

        for old_path, new_path in reversed(batch):
            ndirname, nfname = os.path.split(new_path)
            dirname, fname = os.path.split(old_path)

            if not os.path.exists(new_path):
                skipped += 1
                continue

            if os.path.exists(old_path):
                failed += 1
                self.view.output_view.addItem(f'Undo skipped for {nfname}: target already exists')
                continue

            try:
                os.rename(new_path, old_path)
                redo_batch.append((old_path, new_path))
                self.view.output_view.addItem(f'Undo: {nfname} ❮❮❮❮ {fname}')
                self._apply_rename_in_list(new_path, old_path)
                undone += 1
                if directory_for_refresh is None:
                    directory_for_refresh = os.path.dirname(new_path)
            except Exception as e:
                self.view.output_view.addItem(f'Undo failed for {nfname}: {e}')
                failed += 1

        if undone == 0:
            self.view.rename_history['undo'].append(batch)

        if redo_batch and undone > 0:
            self.view.rename_history['redo'].append(redo_batch)
            if directory_for_refresh:
                self._refresh_file_list(directory_for_refresh)

        summary = f'Undo Complete! {undone} undone, {skipped} skipped, {failed} failed.'
        self.view.output_view.addItem(summary)
        self.view.output_view.scrollToBottom()
        self.view.toasts.show_toast(summary, location='general', theme='info')

    def redo(self):
        if not self.view.rename_history['redo']:
            self.view.output_view.addItem('Nothing to redo!')
            return

        batch = self.view.rename_history['redo'].pop()
        undo_batch = []
        redone, failed = 0, 0
        directory_for_refresh = None

        for old_path, new_path in batch:
            dirname, fname = os.path.split(old_path)
            ndirname, nfname = os.path.split(new_path)

            try:
                if not os.path.exists(old_path):
                    raise FileNotFoundError(f'File not found: {old_path}')
                if os.path.exists(new_path):
                    raise FileExistsError(f'File already exists: {new_path}')

                os.rename(old_path, new_path)
                undo_batch.append((old_path, new_path))
                self.view.output_view.addItem(f'Redo: {fname} ❯❯❯❯ {nfname}')
                self._apply_rename_in_list(old_path, new_path)
                redone += 1
                if directory_for_refresh is None:
                    directory_for_refresh = os.path.dirname(old_path)
            except Exception as e:
                self.view.output_view.addItem(f'Redo failed for {fname}: {e}')
                failed += 1

        if undo_batch:
            self.view.rename_history['undo'].append(undo_batch)
            if directory_for_refresh:
                self._refresh_file_list(directory_for_refresh)

        summary = f'Redo Complete! {redone} files redone, {failed} files failed.'
        self.view.output_view.addItem(summary)
        self.view.toasts.show_toast(summary, location='general', theme='info')

    def transform_name(self, name: str, chars: int = 0, from_start: bool = False, from_end: bool = False,
                       remove_spaces: bool = False, exact_str: str = '', replace: bool = False, replace_str: str = '',
                       replace_with: str = '') -> str:
        if chars > 0:
            if from_start:
                name = name[chars:]
            if from_end:
                name = name[:-chars]

        if exact_str:
            name = name.replace(exact_str, '')

        if remove_spaces:
            name = name.replace(' ', '')

        if replace and replace_str and replace_with:
            name = name.replace(replace_str, replace_with)

        return name

    def on_preview(self, rolling_history: bool = False, is_preview: bool = False, ):
        chars = 0
        if not rolling_history:
            self.view.output_view.clear()
        else:
            self.view.output_view.addItem('------------------------')

        if not self.view.remove_string_check.isChecked():
            chars_text = self.view.chars_to_remove.text().strip()
            if chars_text.isdigit():
                chars = int(chars_text)

        from_start, from_end, remove_spaces, exact_string, replace, replace_str, replace_with = self._gather_config()

        for idx in range(self.view.files_preview.count()):
            item = self.view.files_preview.item(idx)
            full_path = item.data(Qt.ItemDataRole.UserRole)
            dirname, fname = os.path.split(full_path)
            base, ext = os.path.splitext(fname)

            new_base = self.transform_name(base, chars, from_start, from_end, remove_spaces, exact_string, replace, replace_str, replace_with)
            self.view.output_view.addItem(f"{fname:<20} ❯❯❯❯ | {new_base + ext}")

        if is_preview:
            self.view.output_view.addItem('(Preview)')
        self.view.output_view.scrollToBottom()

    def on_apply(self):
        self.view.output_view.clear()
        failed = 0
        updated_paths = []
        undo_batch = []
        file_paths = [
            self.view.files_preview.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.view.files_preview.count())
        ]
        chars = 0

        if not self.view.remove_string_check.isChecked():
            chars_text = self.view.chars_to_remove.text().strip()
            if chars_text.isdigit():
                chars = int(chars_text)

        from_start, from_end, remove_spaces, exact_string, replace, replace_str, replace_with = self._gather_config()
        total_files = self.view.files_preview.count()

        for idx in range(total_files):
            item = self.view.files_preview.item(idx)
            full_path = item.data(Qt.ItemDataRole.UserRole)
            dirname, fname = os.path.split(full_path)
            base, ext = os.path.splitext(fname)

            new_base = self.transform_name(base, chars, from_start, from_end, remove_spaces, exact_string, replace, replace_str, replace_with)
            new_path = os.path.join(dirname, new_base + ext)

            if full_path == new_path:
                continue

            if os.path.exists(new_path):
                continue

            try:
                os.rename(full_path, new_path)
                logger.info(f'"{full_path}" → "{new_path}"')
                updated_paths.append(new_path)
                undo_batch.append((full_path, new_path))
            except Exception as e:
                self.view.output_view.addItem(f'Failed to rename {fname}: Error: {e}')
                failed += 1

        if undo_batch:
            self.view.rename_history['undo'].append(undo_batch)
            self.view.rename_history['redo'].clear()

            if updated_paths:
                refreshed_paths = []
                for old_path in file_paths:
                    for src, dst in undo_batch:
                        if old_path == src:
                            refreshed_paths.append(dst)
                            break
                    else:
                        refreshed_paths.append(old_path)

                self._refresh_file_list(refreshed_paths)

            count = len(updated_paths)
            self.view.output_view.addItem("Changes Applied! See preview below.")
            self.on_preview(self.view.rolling_history)

            msg = f"Changes applied! Renamed {count}/{total_files} files, {failed} failed."
            self.view.toasts.show_toast(msg, location='general', theme='success')
            self.view.output_view.addItem(msg)
        else:
            self.view.output_view.addItem("No changes were made.")
            self.view.toasts.show_toast("No files were modified.", location='general', theme='warning')

    def show_tooltip(self, msg, location, theme):
        self.view.toasts.show_toast(msg, location=location, theme=theme)

    def clear_rename_history(self):
        self.view.rename_history = {'undo': [], 'redo': []}




    def show_rm_str_context_menu(self, pos):
        menu = self.view.remove_string_text.createStandardContextMenu()

        menu.addSeparator()

        saved_strings = self._get_saved_rm_strings() or []
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

        suggestions = self._get_suggested_rm_strings()
        if suggestions:
            submenu = QMenu("Suggested Strings", self.view)
            submenu.clear()
            for s in suggestions:
                act = QAction(s, self.view)
                act.triggered.connect(lambda _, text=s: self.insert_rm_str(text))
                submenu.addAction(act)
            menu.addMenu(submenu)

        else:
            act = QAction("(no suggested strings)", self.view)
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




    def _get_suggested_rm_strings(self) -> list[str]:
        # filenames = [self.view.files_preview.item(i).data(Qt.ItemDataRole.UserRole)
        #              for i in range(self.view.files_preview.count())]
        total_files = self.view.files_preview.count()
        if total_files == 0:
            return []

        base_names = []
        potential_suggestions = []

        for idx in range(total_files):
            item = self.view.files_preview.item(idx)
            full_path = item.data(Qt.ItemDataRole.UserRole)
            dirname, fname = os.path.split(full_path)
            base, ext = os.path.splitext(fname)

            base_names.append(base)

        for base in base_names:

            if ' - rev' in base.lower():
                base, cut = base.split('-', 1)
                cut = f' -{cut}'
                potential_suggestions.append(cut)

            elif '-rev' in base.lower():
                base, cut = base.split('-', 1)
                cut = f'-{cut}'
                potential_suggestions.append(cut)

            elif '_rev' in base.lower():
                base, cut = base.split('_', 1)
                cut = f'_{cut}'
                potential_suggestions.append(cut)

            elif '-' in base.lower():
                base, cut = base.split('-', 1)
                potential_suggestions.append(cut)

            elif '_' in base.lower():
                base, cut = base.split('_', 1)
                potential_suggestions.append(cut)

        suggestions = set(potential_suggestions)
        final_suggestions = [s for s in suggestions]
        return sorted(final_suggestions)





    def _get_saved_rm_strings(self):
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
        self.view.remove_string_text.setFocus()
        self.view.remove_string_check.setChecked(True)

    def drop_event(self, event):
        if not event.mimeData().hasUrls():
            return

        urls = [url.toLocalFile() for url in event.mimeData().urls()]
        if not urls:
            return

        if self.view.stack_files_check.isChecked():
            existing_paths = {
                self.view.files_preview.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.view.files_preview.count())
            }

            skipped = 0
            for file_path in urls:
                if not os.path.isfile(file_path):
                    self.view.toasts.show_toast('Invalid file path', location='general', theme='error')
                    skipped += 1
                    continue

                if file_path in existing_paths:
                    skipped += 1
                    continue

                fname = os.path.basename(file_path)
                item = QListWidgetItem(fname)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.view.files_preview.addItem(item)
                existing_paths.add(file_path)

            if skipped:
                self.view.toasts.show_toast(f'Skipped {skipped} duplicate files', location='general', theme='warning')

        else:
            new_items = []
            skipped = 0

            for file_path in urls:
                if not os.path.isfile(file_path):
                    self.view.toasts.show_toast('Invalid file path', location='general', theme='error')
                    skipped += 1
                    continue

                fname = os.path.basename(file_path)
                item = QListWidgetItem(fname)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                new_items.append(item)

            if self.view.files_preview.count() > 0:
                self.view.controller.clear_files()

            for item in sorted(new_items, key=lambda itm: itm.text().lower()):
                self.view.files_preview.addItem(item)
            self.view.toasts.show_toast(f'Added {len(new_items)} files', location='general', theme='success')

            if skipped:
                self.view.toasts.show_toast(f'Skipped {skipped} invalid files', location='general', theme='warning')

    def shortcuts(self):
        shortcuts_window = Shortcuts('dark', self.view)
        shortcuts_window.show()

    def help(self):
        self.view.help_menu.toggle()
        self.view.menu.toggle()

    def about(self):
        about_window = About('dark', self.view)
        about_window.show()

    def validate_chars_input(self, text):
        if not text:
            return

        if not text.isdigit():
            self.view.toasts.show_toast("Only whole numbers allowed", location="general", theme="warning")
            return

        value = int(text)
        if value > 9999:
            self.view.toasts.show_toast("Max number: 9999", location="general", theme="warning")

    def _gather_config(self):
        from_start = self.view.start_check.isChecked()
        from_end = self.view.end_check.isChecked()
        remove_spaces = self.view.remove_spaces_check.isChecked()
        exact_string = self.view.remove_string_text.text() if self.view.remove_string_check.isChecked() else ''
        replace = self.view.replace_string_check.isChecked()
        replace_str = self.view.replace_string_text.text() if replace else ''
        replace_with = self.view.replace_string_replace_text.text() if replace else ''
        return from_start, from_end, remove_spaces, exact_string, replace, replace_str, replace_with

    def _apply_rename_in_list(self, src_path: str, dst_path: str):
        for i in range(self.view.files_preview.count()):
            item = self.view.files_preview.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == src_path:
                item.setData(Qt.ItemDataRole.UserRole, dst_path)
                item.setText(os.path.basename(dst_path))
                break

    def _refresh_file_list(self, source):

        self.view.files_preview.clear()

        if isinstance(source, (list, tuple)):
            for fpath in sorted(source, key=lambda p: os.path.basename(p).lower()):
                if os.path.isfile(fpath):
                    item = QListWidgetItem(os.path.basename(fpath))
                    item.setData(Qt.ItemDataRole.UserRole, fpath)
                    self.view.files_preview.addItem(item)
            self.view.files_preview.scrollToBottom()
            return

        if isinstance(source, str):
            if not os.path.isdir(source):
                return
            for fname in sorted(os.listdir(source)):
                fpath = os.path.join(source, fname)
                if os.path.isfile(fpath):
                    item = QListWidgetItem(fname)
                    item.setData(Qt.ItemDataRole.UserRole, fpath)
                    self.view.files_preview.addItem(item)
            self.view.files_preview.scrollToBottom()







