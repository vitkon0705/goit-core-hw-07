from collections import UserDict
from datetime import datetime, date, timedelta



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value_str: str):
        if Phone.is_number_correct(value_str):
            super().__init__(value_str)

    @staticmethod
    def is_number_correct(value: str):
        if len(value) != 10 or not value.isdigit():
            raise ValueError(
                f"Number '{value}' is wrong! Phone number must contain only digits and only ten ones")
        return True

class Birthday(Field):
    def __init__(self, value_str: str):
        try:
            value_obj = datetime.strptime(value_str, "%d.%m.%Y").date()
            super().__init__(value_str)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name_str: str):
        self.name = Name(name_str)
        self.phones = []
        self.birthday = None

    def __str__(self):
        phone_numbers_str = []
        for phone_obj in self.phones:
            phone_numbers_str.append(phone_obj.value)
        return f"Contact name: '{self.name.value}', phones: {', '.join(phone_numbers_str)}"

    def add_phone(self, phone_str: str):
        self.phones.append(Phone(phone_str))

    def find_phone(self, phone_str: str):
        for phone_obj in self.phones:
            if phone_obj.value == phone_str:
                return phone_obj
        return None

    def remove_phone(self, phone_str: str):
        found_phone_obj = self.find_phone(phone_str)
        self.phones.remove(found_phone_obj)

    def edit_phone(self, phone_old_str: str, phone_new_str: str):
        if Phone.is_number_correct(phone_old_str) and Phone.is_number_correct(phone_new_str):
            if not self.find_phone(phone_old_str):
                raise ValueError(
                    f"Phone number '{phone_old_str}' is not in the list!")
            else:
                self.remove_phone(phone_old_str)
                self.add_phone(phone_new_str)

    def add_birthday(self, birthday_str: str):
        self.birthday = Birthday(birthday_str)

class AddressBook(UserDict):
    def __str__(self):
        content = ""
        for value in self.data.values():
            content += f"{value};\n"
        return content.strip()

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name_str: str):
        if name_str in self.data:
            return self.data[name_str]
        return None

    def delete(self, name_str: str):
        if name_str in self.data:
            del self.data[name_str]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = date.today()
        dic_list = []
        for record in self.data.values():
            dic_list.append(
                {"name": record.name.value, "birthday": datetime.strptime(record.birthday.value, "%d.%m.%Y").date()})
        for contact in dic_list:
            contact["birthday"] = contact["birthday"].replace(year=today.year)
            if contact["birthday"] < today:
                contact["birthday"] = contact["birthday"].replace(year=today.year + 1)
            delta = (contact["birthday"] - today).days
            if delta >= 0 and delta <= 7:
                monday = 0
                days_ahead = monday - contact["birthday"].weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                delta = timedelta(days=days_ahead)
                next_monday = contact["birthday"] + delta
                weekday_of_birthday = contact["birthday"].weekday()
                if weekday_of_birthday >= 5:
                    contact["birthday"] = next_monday
                upcoming_birthdays.append(
                    {"name": contact["name"], "congratulation_date": contact["birthday"].strftime("%d.%m.%Y")})
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError as ie:
            return f"IndexError: {ie}"
        except KeyError as ke:
            return f"KeyError: {ke}"
        except ValueError as ve:
            return f"ValueError: {ve}"
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Contact '{name}' is not found")
    record.edit_phone(old_phone, new_phone)
    return "Contact updated"

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Contact '{name}' is not found")
    return record

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Contact '{name}' is not found")
    record.add_birthday(birthday_str)
    return f"Birthday added to '{name}'"

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Contact '{name}' is not found")
    return str(record.birthday)

@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()