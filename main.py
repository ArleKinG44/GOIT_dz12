from collections import UserDict
from datetime import datetime
import pickle
import os


class Field:
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value

    def __str__(self):
        return str(self.__value)

    def is_valid(self, value):
        return True
    
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid value")
        self.__value = value


class Name(Field):
    pass


class Phone(Field):
    def is_valid(self, value):
        return len(value) == 10 and value.isdigit()


class Birthday(Field):
    def is_valid(self, value):
        return isinstance(value, datetime)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                break

    def edit_phone(self, old_phone_number, new_phone_number):
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number
                break
        else:
            raise ValueError("The old phone number does not exist.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone

    def days_to_birthday(self):
        if not self.birthday:
            return None
        next_birthday = datetime(datetime.now().year, self.birthday.value.month,
                                 self.birthday.value.day)
        if datetime.now() > next_birthday:
            next_birthday = datetime(datetime.now().year + 1, self.birthday.value.month,
                                     self.birthday.value.day)
        return (next_birthday - datetime.now()).days

    def __str__(self):
        return f"""Contact name: {self.name.value},
                    phones: {'; '.join(p.value for p in self.phones)}"""


class AddressBook(UserDict):
    
    def __init__(self):
        super().__init__()
        self.current_page = 0

    def input_error(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError:
                return "KeyError: The key you provided does not exist."
            except ValueError:
                return "ValueError: The value you provided is not valid."
            except TypeError:
                return "TypeError: The function you called is missing required arguments."
            except FileNotFoundError:
                return "FileNotFoundError: File with this name was not found."
        return inner 

    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record

    @input_error
    def find(self, name):
        if name in self.data:
            return self.data.get(name)
        else:
            return f"Contact {name} not found"

    @input_error
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        return f"Contact {name} deleted"

    @input_error
    def iterator(self, n):
        self.current_page = 0
        self.page_size = int(n)
        while self.current_page < len(self.data):
            yield [(name, [phone.value for phone in record.phones])
                   for name, record in list(self.data.items())
                   [self.current_page:self.current_page + self.page_size]]
            self.current_page += self.page_size

    @input_error
    def save_to_file(self):
        filename = 'address_book.pkl'
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)
        return f"Data saved to {filename}"

    @input_error
    def load_from_file(self):
        filename = 'address_book.pkl'
        with open(filename, 'rb') as file:
            self.data = pickle.load(file)
        return f"Downloaded from {filename}"

    @input_error
    def search(self, query):
        result = []
        for name, record in self.data.items():
            if query in name or any(query in phone.value for phone in record.phones):
                result.append((name, [phone.value for phone in record.phones]))
        return result

    @input_error
    def add_record_str(self, data):
        name, phone = data.split()
        record = Record(name)
        record.add_phone(phone)
        self.add_record(record)
        return f"Contact {name} added"

    @input_error
    def edit_phone(self, data):
        name, old_phone, new_phone = data.split()
        record = self.find(name)
        if record:
            record.edit_phone(old_phone, new_phone)
            return f"Phone number for {name} changed."
        else:
            return "The contact does not exist."

    @input_error
    def good_bye(self):
        self.save_to_file()
        return "Good bye!"

    @input_error
    def start_iterator(self, n):
        self.iterator_instance = self.iterator(int(n))
        return next(self.iterator_instance, "No more records.")

    @input_error
    def next_page(self):
        return next(self.iterator_instance, "No more records.")

    @input_error
    def choice_action(self, data):
        parts = data.split()
        if not parts:
            return "No command given", None
        command = parts[0]
        args = ' '.join(parts[1:])
        if command in self.ACTIONS:
            return self.ACTIONS[command], args
        else:
            return "Give me a correct command please", None


def main(address_book):

    filename = 'address_book.pkl'
    if os.path.exists(filename):
        ab.load_from_file()
    else:
        open(filename, 'a').close()

    ACTIONS = {
        'add': address_book.add_record_str,
        'delete': address_book.delete,
        'edit_phone': address_book.edit_phone,
        'find': address_book.find,
        'show_all': address_book.start_iterator,
        'next': address_book.next_page,
        'search': address_book.search,
        'save': address_book.save_to_file,
        'exit': address_book.good_bye,
        'close': address_book.good_bye,
        '.': address_book.good_bye}
    
    while True:
        data = input()
        func, args = choice_action(data, ACTIONS)
        if isinstance(func, str):
            print(func)
            if func == "Good bye!":
                break
        else:
            result = func(args) if args else func()
            print(result)
            if result == "Good bye!":
                break

def choice_action(data, ACTIONS):
    parts = data.split()
    if not parts:
        return "No command given", None
    command = parts[0]
    args = ' '.join(parts[1:])
    if command in ACTIONS:
        return ACTIONS[command], args
    else:
        return "Give me a correct command please", None

if __name__ == "__main__":
    ab = AddressBook()
    main(ab)
