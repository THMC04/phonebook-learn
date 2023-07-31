import sqlite3
import os
import sys
from colorama import Fore, Style
import tabulate
import string
import math


class NoResultFoundException(Exception):
    "Raised when return given by the SQL command"
    pass


class User():
    def __init__(self, name, con):
        self.name = name
        self.con = con
    

    def create_table(self):

        cur = self.con.cursor()
        
        sql_c = f"""
        CREATE TABLE IF NOT EXISTS [{self.name}] (
        Number VARCHAR(12),
        Name TEXT,
        CountryCode VARCHAR(4),
        PRIMARY KEY (Number)
        );
        """ 
        cur.execute(sql_c)
        self.con.commit()


    def delete_table(self):

        cur = self.con.cursor()
        
        sql_c = f"DROP TABLE [{self.name}];"

        cur.execute(sql_c)
        self.con.commit()
    

    def add_entry(self, number, name, code):
        
        cur = self.con.cursor()

        sql_c = f"""
        INSERT INTO [{self.name}] VALUES (?, ?, ?);
        """   
        cur.execute(sql_c,(number,name,code))
        
        self.con.commit()
    

    def remove_entry(self, number):
        
        cur = self.con.cursor()

        sql_c = f"""
        DELETE FROM [{self.name}] WHERE Number = ?;
        """
        cur.execute(sql_c, (number,))
        
        self.con.commit()
    

    def replace_entry(self, number, code, new_name):

        self.remove_entry(number)
        self.add_entry(number, new_name, code)
    

    def import_data(self, file):
       
        with open(file, "r", encoding="utf-8") as f:
            
            for line in f.readlines():
                
                code, number, name = line.split(" ").strip()
                
                self.add_entry(number, name, code)

    
    def look_up(self, number = None, name = None):

        cur = self.con.cursor()       
        
        if number != None:
            number = f"%{number}%"
            sql_c = f"""SELECT Name, CountryCode, Number FROM [{self.name}] WHERE Number LIKE ?;"""
            res = cur.execute(sql_c, (number,))
        
        elif name != None:
            name = f"%{name}%"
            sql_c = f"""SELECT Name, CountryCode, Number FROM [{self.name}] WHERE Name LIKE ?;"""
            res = cur.execute(sql_c, (name,))
        
        values = res.fetchall()

        final_values = tpl_lst_to_lst(values)
        
        if len(final_values) == 0:
            raise NoResultFoundException
        
        return final_values


    def get_all(self):

        cur = self.con.cursor()

        sql_c = f"""SELECT Name, CountryCode, Number FROM [{self.name}] ORDER BY Name;"""

        res = cur.execute(sql_c)
        values = res.fetchall()
        
        final_values = tpl_lst_to_lst(values)
        
        if len(final_values) == 0:
            raise NoResultFoundException
        
        return final_values


def stop(con):
    
    con.close()
    sys.exit()


def tpl_lst_to_lst(tuple_list):
    
    final_values = []

    for elem in tuple_list:
        inter_values = []
        for value in elem:
            inter_values.append(value)
        final_values.append(inter_values)
        
    return final_values


def input_check(choice, final_inp):
    
    try:
                
        choice = int(choice)
            
    except ValueError:

        error_txt(f"\{choice} is not a valid option - (1 - {final_inp}\n")
        return False, None                            
            
    if choice not in range(1, final_inp + 1):
        error_txt(f"\n{choice} is not a valid option - (1 - {final_inp})\n")
        return False, None

    return True, choice


def error_txt(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")


def header_txt(text):
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")


def gen_table(res):

        headers = ["Name", "Country Code", "Number"]

        print(tabulate.tabulate(res, headers, tablefmt="pretty")) 


def return_users(con):

    cur = con.cursor()

    sql_c = """
    SELECT name FROM sqlite_master WHERE type='table';
    """
    
    res = cur.execute(sql_c)
    values = res.fetchall()
    
    final_values = []
    31
    for elem in values:
        final = elem[0].replace("_sp_", " ")
        final_values.append(final)
    
    return final_values
    

def new_user(con):
    
    blacklist = list(string.punctuation)
    blacklist.pop(13)
    blacklist.pop(-6)
    
    
    while True:
        name = input("What is the new user's name?\n")
        
        
        for letter in name:
            if letter in blacklist:
                error_txt("\nUnsupported name. Please try again.\n")
                failed = True
                break
            else:
                failed = False    
        
        if failed:
            continue
        
        if len(name) >= 14:
            
            error_txt("\nThat name is too long. PLease input a new one\n")
            continue  
        else:
            
            name = name.replace(" ", "_sp_")
            current_user = User(name, con)
            
            try:
                current_user.create_table()
            except sqlite3.OperationalError:
                error_txt("\nA error occurred. Please try again.\n")
                continue
            
            return current_user


def boot_up(con):
    
    users = return_users(con)

    if len(users) == 0:
        
        print(f"\n{Fore.BLUE}Welcome!\n{Style.RESET_ALL}\n{Fore.YELLOW}No Users found. Please create a new user{Style.RESET_ALL}\n")       
        current_user = new_user(con)
        return current_user
    
    else:
        
        while True:
            
            true_size = len(users)
            total_size = true_size + 3
            
            print(total_size)

            print(f"\n{Fore.BLUE}Welcome back!{Style.RESET_ALL}\n")
            header_txt(f"Please choose a user (1 - {total_size}):\n")
            
            for i in range(true_size):
                print(str(i + 1) + f" - {users[i]}\n")
            print(str(total_size - 2) + " - Create new user\n")
            print(str(total_size - 1) + " - Delete a user\n")
            print(str(total_size) + " - Exit\n")

            choice = input().strip()
            
            flag, choice = input_check(choice, total_size)

            if flag == False:
                continue
            
            if choice == total_size:
                stop(con)    
            elif choice == total_size - 1:
                delete_user(users, con)
            elif choice == total_size - 2:
                current_user = new_user(con)
                return current_user 
            else:
                usr = users[choice - 1].replace(" ", "_sp_")
                current_user = User(usr, con)
                return current_user


def delete_user(users, con):
    
    true_size = len(users)
    total_size = true_size + 1
    
    while True:
        header_txt(f"Choose a user to delete (1 - {total_size}):\n")     
                
        for i in range(true_size):
            print(str(i + 1) + f" - {users[i]}\n")
        print(f"{total_size} - Return")
    
        del_user = input("\n")

        flag, del_user = input_check(del_user, total_size)

        if flag == False:
            continue

        if del_user == true_size + 1:
            main()
        else:
            usr = users[del_user - 1].replace(" ", "_sp_")
            sel_user = User(usr, con)
            sel_user.delete_table()
            main()


def operations(user):

    while True:
        
        header_txt(f"\nPlease choose an operation (1 - 7):\n")
        print("1 - Show full phonebook")
        print("2 - Look up a number or name")
        print("3 - Add a new number")
        print("4 - Remove a number")
        print("5 - Change a number's associated name")
        print("6 - Insert large amount of numbers")
        print("7 - Return\n")

        choice = input().strip()
        
        if choice == "res_11037":
            user.con.close()
            os.remove("phonebook_data.db")
            main()
        
        if choice[:10] == "test_11037":
            amt = choice[11:]
            gen_test_cases(int(amt), user)
            operations(user)

        flag, choice = input_check(choice, 7)
        
        if flag == False:
            continue
        
        match choice:
            case 1:
                show_phonebook(user)
            case 2:
                search_phonebook(user)
            case 3:
                add_number(user)
            case 4:
                remove_number(user)
            case 5:
                pass
            case 6:
                pass
            case 7:
                return


def show_phonebook(user):

    max_per_page = 25
    try:
        res = user.get_all()
    except NoResultFoundException:
        print("\nNo numbers saved in phonebook.\n")
        input("Press ENTER to continue\n")
        return
    else:
        total_pages = math.ceil(len(res)/max_per_page)
        last_page = len(res)%max_per_page
        page = 1
        while True:
            if page == total_pages:
                page_res = res[(page-1)*max_per_page:(page-1)*max_per_page+last_page]
            else:
                page_res = res[(page-1)*max_per_page:page*max_per_page]

            gen_table(page_res)

            print(f"\nPage {page} out of {total_pages}\n")
            
            if total_pages == 1:
                print("1 - Return")
            elif page == 1:
                print("1 - Next Page")
                print("2 - Return")
            elif page == total_pages:
                print("1 - Previous Page")
                print("2 - Return")
            else:
                print("1 - Next Page")
                print("2 - Previous Page")
                print("3 - Return")

            choice = input().strip()

            if page == 1 or page == total_pages:
                flag, choice = input_check(choice, 2)
            else:
                flag, choice = input_check(choice, 3)
            
            if flag == False:   
                continue
            
            if total_pages == 1:
                return
            elif page == 1:
                if choice == 1:
                    page += 1
                else:
                    return
            elif page == total_pages:
                if choice == 1:
                    page -= 1
                else:
                    return
            else:
                if choice == 1:
                    page += 1
                elif choice == 2:
                    page -= 1
                else:
                    return
           

def search_phonebook(user):

    number = True
    header_txt(f"\nPlease input a name or a number:\n")

    choice = input().strip()
    
    try:
        int(choice)
    except ValueError:
        number = False
    
    no_res = False

    if number:
        try:
            res = user.look_up(number = choice)
        except NoResultFoundException:
            print("\nNo users found.")
            no_res = True
    else:
        try: 
            res = user.look_up(name = choice)
        except NoResultFoundException:
            print("\nNo users found.")
            no_res = True
    
    if no_res == False:
        
        gen_table(res)

    input("\nPress ENTER to continue\n")


def add_number(user):

    while True:

        error_txt("\nPlease input the name:\n")
        
        name = input().strip()

        if len(name) == 0 or len(name) >= 20:
            error_txt("\nPlease input a name of valid size.")
            continue
        if name.isdigit() == True:
            error_txt("\nName cannot be composed of only digits. Please try again.")
            continue
        break
    
    while True:

        header_txt("\nPlease input the code and number separated by a space:")

        data = list(input().strip().split(" "))

        if len(data) == 1:
            
            error_txt("\nPlease make sure the code and number are separated.")
            continue
        
        if len(data) > 2 or len(data) == 0:
            
            error_txt("\nPlease input a valid code and number.")
            continue
        
        if data[1].isdigit() == False:

            error_txt("\nNumber can only contain digits. Please try again.")
            continue
        elif len(data[1]) > 12 or len(data[1]) < 4:
            
            error_txt("\nPlease input a valid number size.")
            continue
        else:
            number = data[1]
        
        if data[0][0] != "+":
            code = "+" + data[0]
        else:
            code = data[0]

        if code[1:].isdigit() == False:
            error_txt("\nCode can only contain a + symbol followed by numbers. Please try again.")
            continue
        
        if len(code) > 4 or len(code) < 2:
            error_txt("\nPlease input a valid code size.")
            continue
        
        break
    try:
        user.add_entry(number, name, code)
    except sqlite3.IntegrityError:
        error_txt(f"Failed to add {number} to list.\nCAUSE: Already added.")
        

def remove_number(user):

    header_txt("\nPlease input the number to remove:")

    number = input().strip()
    
    try:
        res = user.look_up(number)  
    except NoResultFoundException:
        print("\nUser not Found.\n")
    else:
        if len(res) != 1:
            error_txt("\nMultiple users found please try again.\n")
        elif len(number) < 4 or len(number) > 12:
            error_txt("\nPlease input a valid number.\n")
        else:
            user.remove_entry(number)
            print(f"\n{res[0][0]} (nº{res[0][2]}) was deleted.\n")

    input("Press ENTER to continue")


def main():
    
    con = sqlite3.connect("phonebook_data.db")
    
    while True:
    
        current_user = boot_up(con)
        operations(current_user)
    

def gen_test_cases(amount, user):
    
    con = sqlite3.connect("phonebook_data.db")
    letters = list(string.ascii_lowercase)
    a = 0
    b = 0
    c = 0
    for i in range(amount):
        
        try:
            user.add_entry(str(100000000 + i),f"test_{letters[a]}{letters[b]}{letters[c]}", "+404")
        except sqlite3.IntegrityError:
            error_txt(f"Failed test_{letters[a]}{letters[b]}{letters[c]}")
        
        c += 1
        
        if c >= len(letters):
            c = 0
            b += 1
        if b >= len(letters):
            b = 0 
            a += 1
        
    
    con.close()


if __name__ == "__main__":

    main()
