import sqlite3
import os
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
    

def return_users(con):

    cur = con.cursor()

    sql_c = """
    SELECT name FROM sqlite_master WHERE type='table';
    """
    
    res = cur.execute(sql_c)
    values = res.fetchall()
    final_values = []
    for entry in values:
        final_values.append(entry[0])
    
    return final_values