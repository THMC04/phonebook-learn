import sqlite3
import os
import sys
from colorama import Fore, Style


class User():
    def __init__(self, name, con):
        self.name = name
        self.con = con
    

    def create_table(self):

        cur = self.con.cursor()
        
        sql_c = f"""
        CREATE TABLE IF NOT EXISTS {self.name} (
        Number VARCHAR(12),
        Name TEXT,
        CountryCode VARCHAR(4),
        PRIMARY KEY (Number)
        );
        """ 
        cur.execute(sql_c)
        self.con.commit()

    
    def add_entry(self, number, name, code):
        
        cur = self.con.cursor()

        sql_c = f"""
        INSERT INTO {self.name} VALUES (?, ?, ?);
        """
        
        try:
            cur.execute(sql_c,(number,name,code))
        except sqlite3.IntegrityError:
            print(f"{Fore.RED}Failed to add {number} to list.\nCAUSE: Already added{Style.RESET_ALL}")
            return False
        
        self.con.commit()
    

    def remove_entry(self, number):
        
        cur = self.con.cursor()

        sql_c = f"""
        DELETE FROM {self.name} WHERE Number = ?;
        """

        cur.execute(sql_c, (number,))
        self.con.commit()
    
    def replace_entry(self, number, code, new_name):

        self.remove_entry(number)
        self.add_entry(number, new_name, code)
    

    def import_data(self, file):
       
        with open(file, "r", encoding="utf-8") as f:
            
            # Amount of entries successfully added
            total = 0
            
            for line in f.readlines():
                check = True
                
                code, number, name = line.split(" ").strip()
                
                check = self.add_entry(number, name, code)
                
                if check:
                    total += 1
        
        return total
    
    def look_up(self, number = None, name = None):

        cur = self.con.cursor()       
        
        if number != None:
            sql_c = f"""SELECT Name FROM {self.name} Where Number ==  ?;"""
            res = cur.execute(sql_c, (number,))
        elif name != None:
            sql_c = f"""SELECT Number FROM {self.name} Where Name ==  ?;"""
            res = cur.execute(sql_c, (name,))

        values = res.fetchall()
        final_values = tpl_lst_to_lst(values)
        return final_values

    def get_all(self):

        cur = self.con.cursor()

        sql_c = f"""SELECT Name, CountryCode, Number FROM {self.name} ORDER BY Name;"""

        res = cur.execute(sql_c)
        values = res.fetchall()
        
        final_values = []
        for elem in values:
            inter_values = []
            for value in elem:
                inter_values.append(value)
            final_values.append(inter_values)
        
        return final_values
        
def stop(con):
    
    con.close()
    sys.exit()


def return_users(con):

    cur = con.cursor()

    sql_c = """
    SELECT name FROM sqlite_master WHERE type='table';
    """
    
    res = cur.execute(sql_c)
    values = res.fetchall()
    final_values = tpl_lst_to_lst(values)
    
    return final_values


def tpl_lst_to_lst(tuple_list):
    
    final_values = []
    
    for elem in tuple_list:
        final_values.append(elem[0])
    
    return final_values


def new_user(con):
    
    while True:
        name = input("What is the new user's name?\n")
        
        if len(name) == 15:
            
            print(f"{Fore.RED}That name is too long. PLease input a new one{Style.RESET_ALL}")
            continue  
        else:
            
            current_user = User(name, con)
            current_user.create_table()
            return current_user


def boot_up(con):
    
    users = return_users(con)

    if len(users) == 0:
        
        print(f"{Fore.BLUE}Welcome new user!\n{Style.RESET_ALL}\nPlease create a new user")
        current_user = new_user(con)
        return current_user
    
    else:
        
        while True:
            
            true_size = len(users)
            total_size = true_size + 2
            
            print(total_size)

            print(f"\n{Fore.BLUE}Welcome back!{Style.RESET_ALL}\n")
            print(f"{Fore.CYAN}Please choose an user (1 - {total_size}):{Style.RESET_ALL}\n")
            
            for i in range(true_size):
                print(str(i + 1) + f" - {users[i]}\n")
            print(str(total_size - 1) + " - Create new user\n")
            print(str(total_size) + " - Exit\n")

            choice = input()
            
            try:
                
                choice = int(choice)
            
            except ValueError:

                print(f"{Fore.RED}{choice} is not a valid option - (1 - {total_size}){Style.RESET_ALL}\n")
                continue                               
            
            if choice not in range(1, total_size + 1):

                print(f"{Fore.RED}{choice} is not a valid option - (1 - {total_size}){Style.RESET_ALL}\n")
                continue 
            else:
                
                if choice == total_size:
                    stop(con)
                
                elif choice == total_size - 1:
                    current_user = new_user(con)
                    return current_user
                else:
                    current_user = User(users[choice - 1], con)
                    return current_user


def main():
    con = sqlite3.connect("test.db")
    
    current_user = boot_up(con)

    con.close()

if __name__ == "__main__":

    main()
    