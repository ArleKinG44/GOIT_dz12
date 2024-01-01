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
        next_birthday = datetime(datetime.now().year, self.birthday.month, self.birthday.day)
        if datetime.now() > next_birthday:
            next_birthday = datetime(datetime.now().year + 1, self.birthday.month, self.birthday.day)
        return (next_birthday - datetime.now()).days



    def __str__(self):
        return f"""Contact name: {self.name.value},
                    phones: {'; '.join(str(p.value) for p in self.phones)}"""



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
    def add_record(self):
        name = input("Enter a name: ")
        if not name:
            return "Error: Name cannot be empty"
        if name in self.data:
            return f"Contact {name} already exists"
        phone_str = input("Enter a (10-digit) phone number: ")
        phone = Phone(phone_str)
        birthday_str = input("Enter your date of birth in yyyy-mm-dd format or leave the field blank: ")
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d') if birthday_str else None
        record = Record(name, birthday)
        record.add_phone(phone.value)
        self.data[name] = record
        return f"User {name} has been added to the contact list"

    @input_error
    def delete(self):
        name = input("Enter the name of the user to be deleted: ")
        if name in self.data:
            del self.data[name]
            return f"Contact {name} deleted"
        else:
            return f"Contact {name} does not exist"

    @input_error
    def edit_phone(self):
        name = input("Enter the name whose number needs to be changed: ")
        if name not in self.data:
            return f"Contact {name} dont found"
        old_phone = input("Enter your old phone number: ")
        record = self.data[name]
        if old_phone not in [phone.value for phone in record.phones]:
            return f"This phone {old_phone} dont found"
        new_phone = input("Enter a new phone number: ")
        record.edit_phone(old_phone, new_phone)
        return f"Phone number for {name} changed."

    @input_error
    def find(self):
        name = input("Enter a name: ")
        if name in self.data:
            return self.data.get(name)
        else:
            return f"Contact {name} not found"

    @input_error
    def add_phone(self):
        name = input("Enter the name of the person whose phone number you want to add: ")
        if name not in self.data:
            return f"Contact {name} dont found"
        phone_str = input("Enter an additional phone number: ")
        phone = Phone(phone_str)
        record = self.data[name]
        record.add_phone(phone.value)
        return f"Added phone number {phone.value} to contact {name}."

    @input_error
    def birthday_change(self):
        name = input("Enter the name of the person who needs the date of birth: ")
        if name not in self.data:
            return f"Contact {name} dont found"
        birthday_str = input("Enter your date of birth in the format yyyy-mm-dd: ")
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
        record = self.data[name]
        record.birthday = birthday
        return f"Added birthday to {name}"

    @input_error
    def days_to_birthday(self):
        name = input("Enter the name of the contact: ")
        if name not in self.data:
            return f"Contact {name} not found"
        record = self.data[name]
        days = record.days_to_birthday()
        if days is None:
            return f"{name} has no birthday information"
        else:
            return f"There are {days} days left until {name} birthday"

    @input_error
    def days_to_birthday(self):
        name = input("Enter the name of the contact: ")
        if name in self.data:
            record = self.data[name]
            return record.days_to_birthday()
        else:
            return "The contact does not exist."

    @input_error
    def search(self):
        query = input("Enter what you remember about the contact: ")
        if not query:
            return "Error: Please enter at least some search information"
        result = []
        for name, record in self.data.items():
            if query in name or any(query in phone.value for phone in record.phones):
                result.append(f"{name}: {', '.join(phone.value for phone in record.phones)}")
        return result

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
    def start_iterator(self):
        n = input("Enter how many contacts to show: ")
        self.iterator_instance = self.iterator(int(n))
        return next(self.iterator_instance, "No more records.")

    @input_error
    def next_page(self):
        if not hasattr(self, 'iterator_instance') or self.iterator_instance is None:
            return "Error: call first comand -- show all"
        try:
            return next(self.iterator_instance)
        except StopIteration:
            self.iterator_instance = None
            return "No more records."

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
    def good_bye(self):
        self.save_to_file()
        return "Good bye!"


def main(address_book):

    filename = 'address_book.pkl'
    if os.path.exists(filename):
        ab.load_from_file()
    else:
        open(filename, 'a').close()

    ACTIONS = {
        'add contact': address_book.add_record,
        'add phone': address_book.add_phone,
        'edit phone': address_book.edit_phone,
        'birthday change': address_book.birthday_change,
        'delete contact': address_book.delete,
        'find phone': address_book.find,
        'search': address_book.search,
        'days to birthday': address_book.days_to_birthday,
        'show all': address_book.start_iterator,
        'next page': address_book.next_page,
        'exit': address_book.good_bye,
        'close': address_book.good_bye,
        '.': address_book.good_bye}

    print_commands(ACTIONS)


    while True:
        data = input()
        func, _ = choice_action(data, ACTIONS)
        if isinstance(func, str):
            print(func)
            if func == "Good bye!":
                break
        else:
            result = func()
            print(result)
            if result == "Good bye!":
                break


def choice_action(data, ACTIONS):
    command = data.strip()
    if not command:
        return "No command given", None
    for action in ACTIONS:
        if command.startswith(action):
            return ACTIONS[action], None
    return "Give me a correct command please", None



def print_commands(ACTIONS):
    print("Available commands:")
    for command in ACTIONS.keys():
        print(command)


if __name__ == "__main__":
    ab = AddressBook()
    main(ab)
