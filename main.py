from collections import UserDict
from datetime import datetime
import pickle


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
        return inner 

    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record

    @input_error
    def find(self, name):
        return self.data.get(name)

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
    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)
        return f"Data saved to {filename}"

    @input_error
    def load_from_file(self, filename):
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

    def main(self):
        self.ACTIONS = {
            'add': self.add_record_str,
            'delete': self.delete,
            'edit_phone': self.edit_phone,
            'find': self.find,
            'show_all': self.start_iterator,
            'next': self.next_page,
            'search': self.search,
            'save': self.save_to_file,
            'load': self.load_from_file,
            'close': self.good_bye,
            'exit': self.good_bye,
            '.': self.good_bye
        }
        while True:
            data = input()
            func, args = self.choice_action(data)
            if isinstance(func, str):
                print(func)
                if func == "Good bye!":
                    break
            else:
                result = func(args) if args else func()
                print(result)
                if result == "Good bye!":
                    break


if __name__ == "__main__":
    ab = AddressBook()
    ab.main()
