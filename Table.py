import struct
import os

class Table:
    def __init__(self, file_name, data_format):
        """
        Initialize the table with a file name and data format.

        :param file_name: Name of the binary file to store the table.
        :param data_format: List of tuples defining the data format, e.g.,
                            [("ID", int), ("Name", str), ("Age", int), ("Email", str)].
        """
        self.file_name = file_name
        self.data_format = data_format  # List of tuples: [(field_name, field_type), ...]
        self.record_format = self.create_record_format()
        self.record_size = struct.calcsize(self.record_format)
    def __getitem__(self, key):
        with open(self.file_name, 'rb') as f:
            f.seek(key* self.record_size)
            record_bytes = f.read(self.record_size)
            return self.unpack_record(record_bytes)

    def create_record_format(self):
        """
        Create a struct format string based on the data format.
        """
        format_string = ''
        for field_name, field_type in self.data_format:
            if field_type == int:
                format_string += 'i'  # Integer (4 bytes)
            elif field_type == str:
                # Determine fixed size for strings (e.g., 20 bytes per string)
                max_size = 20  # Default max size for strings
                format_string += f'{max_size}s'
            else:
                raise ValueError(f"Unsupported field type: {field_type}")
        return format_string

    def add_record(self, record):
        """
        Add a record to the binary file, ensuring ID uniqueness.

        :param record: Dictionary containing the record fields.
        """
        if "ID" not in record:
            raise ValueError("Record must contain an 'ID' field.")

        if not isinstance(record["ID"], int):
            raise TypeError("ID must be an integer.")

        # Ensure record matches the data format
        for field_name, field_type in self.data_format:
            if field_name not in record:
                raise ValueError(f"Field '{field_name}' is missing in the record.")
            if not isinstance(record[field_name], field_type):
                raise TypeError(f"Field '{field_name}' must be of type {field_type}.")

        # Check for duplicate ID
        if self.find_by_id(record["ID"]):
            raise ValueError("A record with this ID already exists.")

        with open(self.file_name, 'ab') as f:
            packed_record = self.pack_record(record)
            f.write(packed_record)

    def find_by_id(self, search_id):
   
        """
        Find the index of the record with the given ID in the binary file using a binary search algorithm.

        :param search_id: ID of the record to search for.
        :return: Index of the record if found, otherwise the index at which the record should be inserted to maintain sorted order.
        """
        with open(self.file_name, 'rb') as f:
            low, high = 0, os.path.getsize(self.file_name) // self.record_size - 1

            while low <= high:
                mid = (low + high) // 2
                record = self[mid]

                if record["ID"] == search_id:
                    return mid
                elif record["ID"] < search_id:
                    low = mid + 1
                else:
                    high = mid - 1

        return low  # Not found

    def pack_record(self, record):
        """
        Pack a record into bytes based on the data format.
        """
        values = []
        for field_name, field_type in self.data_format:
            value = record[field_name]
            if field_type == str:
                value = value.encode('utf-8').ljust(20)[:20]  # Fixed size strings
            values.append(value)
        return struct.pack(self.record_format, *values)

    def unpack_record(self, record_bytes):
        """
        Unpack bytes into a record based on the data format.
        """
        unpacked = struct.unpack(self.record_format, record_bytes)
        record = {}
        for (field_name, field_type), value in zip(self.data_format, unpacked):
            if field_type == str:
                value = value.decode('utf-8').strip()  # Decode and strip padding
            record[field_name] = value
        return record

    def display_records(self):
        """
        Display all records in the table by reading from the file.
        """
        if not os.path.exists(self.file_name) or os.path.getsize(self.file_name) == 0:
            print(f"Table '{self.file_name}' is empty.")
            return

        headers = [field[0] for field in self.data_format]
        print(" | ".join(headers))
        print("-" * (len(headers) * 15))

        with open(self.file_name, 'rb') as f:
            while True:
                record_bytes = f.read(self.record_size)
                if not record_bytes:
                    break
                record = self.unpack_record(record_bytes)
                print(" | ".join(str(record[field[0]]) for field in self.data_format))

    
# Example usage
data_format = [("ID", int), ("Name", str), ("Age", int), ("Email", str)]
table = Table("users_table.db", data_format)

# Add records
table.add_record({"ID": 2, "Name": "Alice", "Age": 25, "Email": "alice@example.com"})
table.add_record({"ID": 1, "Name": "Bob", "Age": 30, "Email": "bob@example.com"})
table.add_record({"ID": 3, "Name": "Charlie", "Age": 35, "Email": "charlie@example.com"})

# Display records
table.display_records()

# Search by ID
record = table.find_by_id(2)
if record:
    print("Record found:", record)
else:
    print("Record not found.")
