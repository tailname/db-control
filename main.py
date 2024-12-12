
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import file_database
import shutil
import os
import struct
class FileDatabase:
    def __init__(self, file_name):
        self.file_name = file_name
        # Define record structure: ID (int, 4 bytes), Name (20 bytes), Age (int, 4 bytes), Email (30 bytes)
        self.record_format = 'i20si30s'
        self.record_size = struct.calcsize(self.record_format)

    def create_db(self):
        with open(self.file_name, 'wb') as f:
            pass  # Create an empty file.

    def delete_db(self):
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

    def clear_db(self):
        with open(self.file_name, 'wb') as f:
            pass  # Clear the database.

    def add_record(self, record):
        with open(self.file_name, 'r+b') as f:
            low, high = 0, os.path.getsize(self.file_name) // self.record_size - 1
            while low <= high:
                mid = (low + high) // 2
                f.seek(mid * self.record_size)
                record_bytes = f.read(self.record_size)
                mid_record = self.unpack_record(record_bytes)

                if mid_record["ID"] == record["ID"]:
                    return False  # Key exists.
                elif mid_record["ID"] < record["ID"]:
                     low = mid + 1
                else:
                    high = mid - 1
            
          
            f.seek((low) * self.record_size)
            packed_record = self.pack_record(record)
            buffer = bytearray(self.record_size)
            while True:
                next_pos = f.tell()
                read_bytes = f.readinto(buffer)
                f.seek(next_pos)
                f.write(packed_record)
                if read_bytes == 0:
                    break
                packed_record = buffer[:read_bytes]
       
        return True
    

    def delete_record(self, field, value):
        temp_file = self.file_name + ".tmp"
        with open(self.file_name, 'rb') as fin, open(temp_file, 'wb') as fout:
            while True:
                record_bytes = fin.read(self.record_size)
                if not record_bytes:
                    break
                record = self.unpack_record(record_bytes)
                if str(record[field]) != str(value):
                    fout.write(record_bytes)
        shutil.move(temp_file, self.file_name)

    def find_record(self, value, field='ID'):
        with open(self.file_name, 'rb') as f:
            if field == 'ID':
                low, high = 0, os.path.getsize(self.file_name) // self.record_size - 1
                while low <= high:
                    mid = (low + high) // 2
                    f.seek(mid * self.record_size)
                    record_bytes = f.read(self.record_size)
                    record = self.unpack_record(record_bytes)

                    if record["ID"] == value:
                        return record
                    elif record["ID"] < value:
                         low = mid + 1
                    else:
                        high = mid - 1
                return None

            while True:
                record_bytes = f.read(self.record_size)
                if not record_bytes:
                    break
                record = self.unpack_record(record_bytes)
                if str(record[field]) == str(value):
                    return record
        return None

    def search_by_field(self, field, value):
        results = []
        with open(self.file_name, 'rb') as f:
            while True:
                record_bytes = f.read(self.record_size)
                if not record_bytes:
                    break
                record = self.unpack_record(record_bytes)
                if str(record[field]) == str(value):
                    results.append(record)
        return results

    def pack_record(self, record):
        """Pack a record into bytes."""
        return struct.pack(
            self.record_format,
            int(record['ID']),
            record['Name'].encode('utf-8').ljust(20),
            int(record['Age']),
            record['Email'].encode('utf-8').ljust(30)
        )

    def unpack_record(self, record_bytes):
        """Unpack bytes into a record."""
        unpacked = struct.unpack(self.record_format, record_bytes)
        return {
            'ID': unpacked[0],
            'Name': unpacked[1].decode('utf-8').strip(),
            'Age': unpacked[2],
            'Email': unpacked[3].decode('utf-8').strip()
        }

    def get_all_records(self):
        """Retrieve all records as a list of dictionaries."""
        records = []
        with open(self.file_name, 'rb') as f:
            while True:
                record_bytes = f.read(self.record_size)
                if not record_bytes:
                    break
                records.append(self.unpack_record(record_bytes))
        return records

    def create_backup(self, backup_file):
        shutil.copy(self.file_name, backup_file)

    def restore_from_backup(self, backup_file):
        shutil.copy(backup_file, self.file_name)
    def clear_db(self): 
        with open(self.file_name, 'wb') as f:
            pass

            



class DatabaseApp:
    def __init__(self, root):
        self.db = None
        self.root = root
        self.root.title("File Database GUI")
        self.setup_gui()

    def setup_gui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Database controls
        ttk.Label(frame, text="Database File:").grid(row=0, column=0, sticky=tk.W)
        self.db_file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.db_file_var, width=50).grid(row=0, column=1)
        ttk.Button(frame, text="Open", command=self.open_db).grid(row=0, column=2)
        ttk.Button(frame, text="New", command=self.create_new_db).grid(row=0, column=3)

        # Record controls
        ttk.Button(frame, text="Show All Records", command=self.show_table).grid(row=1, column=0, sticky=tk.W)
        ttk.Button(frame, text="Add Record", command=self.add_record).grid(row=1, column=1, sticky=tk.W)
        ttk.Button(frame, text="Search by Field", command=self.search_record).grid(row=1, column=2, sticky=tk.W)
        ttk.Button(frame, text="Create Backup", command=self.create_backup).grid(row=1, column=3, sticky=tk.W)
        ttk.Button(frame, text="Clear Database", command=self.clear_database).grid(row=2, column=0, sticky=tk.W)
        ttk.Button(frame, text="Delete Record", command=self.delete_record).grid(row=2, column=1, sticky=tk.W)
        ttk.Button(frame, text="Edit Record", command=self.edit_record).grid(row=2, column=2, sticky=tk.W)

        # Table display
        self.table = ttk.Treeview(self.root, columns=("ID", "Name", "Age", "Email"), show="headings")
        self.table.heading("ID", text="ID")
        self.table.heading("Name", text="Name")
        self.table.heading("Age", text="Age")
        self.table.heading("Email", text="Email")
        self.table.grid(row=1, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

    def delete_record(self):
        if not self.db:
            messagebox.showerror("Error", "No database loaded.")
            return

        def perform_deletion():
            field = field_var.get()
            value = value_var.get()
            if field not in ["ID", "Name", "Age", "Email"]:
                messagebox.showerror("Error", "Invalid field selected.")
                return
            if field == "ID" or field == "Age":
                try:
                    value = int(value)
                except ValueError:
                    messagebox.showerror("Error", f"{field} must be an integer.")
                    return

            self.db.delete_record(field, value)
            self.show_table()  # Refresh the table
            messagebox.showinfo("Success", "Record(s) deleted successfully.")
            delete_window.destroy()

        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Record")

        ttk.Label(delete_window, text="Field:").grid(row=0, column=0, sticky=tk.W)
        field_var = tk.StringVar(value="ID")
        ttk.Combobox(delete_window, textvariable=field_var, values=["ID", "Name", "Age", "Email"]).grid(row=0, column=1)

        ttk.Label(delete_window, text="Value:").grid(row=1, column=0, sticky=tk.W)
        value_var = tk.StringVar()
        ttk.Entry(delete_window, textvariable=value_var).grid(row=1, column=1)

        ttk.Button(delete_window, text="Delete", command=perform_deletion).grid(row=2, column=0, columnspan=2)

    def edit_record(self):
        if not self.db:
            messagebox.showerror("Error", "No database loaded.")
            return

        def load_record():
            try:
                record_id = int(id_var.get())
            except ValueError:
                messagebox.showerror("Error", "ID must be an integer.")
                return

            record = self.db.find_record(record_id)
            if not record:
                messagebox.showerror("Error", "Record not found.")
                return

            name_var.set(record['Name'])
            age_var.set(record['Age'])
            email_var.set(record['Email'])

        def save_changes():
            try:
                updated_record = {
                    "ID": int(id_var.get()),
                    "Name": name_var.get(),
                    "Age": int(age_var.get()),
                    "Email": email_var.get()
                }
                self.db.delete_record("ID", updated_record["ID"])
                self.db.add_record(updated_record)
                self.show_table()  # Refresh the table
                messagebox.showinfo("Success", "Record updated successfully.")
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please check the data types.")

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Record")

        ttk.Label(edit_window, text="ID:").grid(row=0, column=0, sticky=tk.W)
        id_var = tk.StringVar()
        ttk.Entry(edit_window, textvariable=id_var).grid(row=0, column=1)
        ttk.Button(edit_window, text="Load", command=load_record).grid(row=0, column=2)

        ttk.Label(edit_window, text="Name:").grid(row=1, column=0, sticky=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(edit_window, textvariable=name_var).grid(row=1, column=1)

        ttk.Label(edit_window, text="Age:").grid(row=2, column=0, sticky=tk.W)
        age_var = tk.StringVar()
        ttk.Entry(edit_window, textvariable=age_var).grid(row=2, column=1)

        ttk.Label(edit_window, text="Email:").grid(row=3, column=0, sticky=tk.W)
        email_var = tk.StringVar()
        ttk.Entry(edit_window, textvariable=email_var).grid(row=3, column=1)

        ttk.Button(edit_window, text="Save", command=save_changes).grid(row=4, column=0, columnspan=2)
    def clear_database(self):
        if not self.db:
            messagebox.showerror("Error", "No database loaded.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the database? This action cannot be undone."):
            self.db.clear_db()
            self.table.delete(*self.table.get_children())  # Clear the table view
            messagebox.showinfo("Success", "Database cleared successfully.")


    def open_db(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.db = FileDatabase(file_path)
            self.db_file_var.set(file_path)

    def create_new_db(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db")
        if file_path:
            self.db = FileDatabase(file_path)
            self.db.create_db()
            self.db_file_var.set(file_path)

    def show_table(self):
        if not self.db:
            messagebox.showerror("Error", "No database loaded.")
            return
        self.table.delete(*self.table.get_children())  # Clear the table
        records = self.db.get_all_records()
        for record in records:
            self.table.insert("", "end", values=(record['ID'], record['Name'], record['Age'], record['Email']))

    def add_record(self):
        if not self.db:
            messagebox.showerror("Error", "No database loaded.")
            return

        def save_record():
            try:
                record = {
                    "ID": int(id_var.get()),
                    "Name": name_var.get(),
                    "Age": int(age_var.get()),
                    "Email": email_var.get()
                }
                success = self.db.add_record(record)
                if success:
                    messagebox.showinfo("Success", "Record added successfully!")
                    record_window.destroy()
                else:
                    messagebox.showerror("Error", "Record with this ID already exists.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please check the data types.")

        record_window = tk.Toplevel(self.root)
        record_window.title("Add Record")

        ttk.Label(record_window, text="ID:").grid(row=0, column=0, sticky=tk.W)
        id_var = tk.StringVar()
        ttk.Entry(record_window, textvariable=id_var).grid(row=0, column=1)

        ttk.Label(record_window, text="Name:").grid(row=1, column=0, sticky=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(record_window, textvariable=name_var).grid(row=1, column=1)

        ttk.Label(record_window, text="Age:").grid(row=2, column=0, sticky=tk.W)
        age_var = tk.StringVar()
        ttk.Entry(record_window, textvariable=age_var).grid(row=2, column=1)

        ttk.Label(record_window, text="Email:").grid(row=3, column=0, sticky=tk.W)
        email_var = tk.StringVar()
        ttk.Entry(record_window, textvariable=email_var).grid(row=3, column=1)

        ttk.Button(record_window, text="Save", command=save_record).grid(row=4, column=0, columnspan=2)

    def search_record(self):
        if not self.db:
            messagebox.showerror("Error", "No database loaded.")
            return

        def perform_search():
            field = field_var.get()
            value = value_var.get()
            if field not in ["ID", "Name", "Age", "Email"]:
                messagebox.showerror("Error", "Invalid field selected.")
                return
            if field == "ID" or field == "Age":
                try:
                    value = int(value)
                except ValueError:
                    messagebox.showerror("Error", f"{field} must be an integer.")
                    return
            if field == "ID":
                results=[self.db.find_record(value)]
            else: results = self.db.search_by_field(field, value)
            self.table.delete(*self.table.get_children())  # Clear the table
            for record in results:
                self.table.insert("", "end", values=(record['ID'], record['Name'], record['Age'], record['Email']))
            search_window.destroy()

        search_window = tk.Toplevel(self.root)
        search_window.title("Search Record")

        ttk.Label(search_window, text="Field:").grid(row=0, column=0, sticky=tk.W)
        field_var = tk.StringVar(value="ID")
        ttk.Combobox(search_window, textvariable=field_var, values=["ID", "Name", "Age", "Email"]).grid(row=0, column=1)

        ttk.Label(search_window, text="Value:").grid(row=1, column=0, sticky=tk.W)
        value_var = tk.StringVar()
        ttk.Entry(search_window, textvariable=value_var).grid(row=1, column=1)

        ttk.Button(search_window, text="Search", command=perform_search).grid(row=2, column=0, columnspan=2)

    def create_backup(self):
        if not self.db:
            messagebox.showerror("Error", "No database loaded.")
            return
        backup_file = filedialog.asksaveasfilename(defaultextension=".bak")
        if backup_file:
            self.db.create_backup(backup_file)
            messagebox.showinfo("Success", f"Backup created: {backup_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
