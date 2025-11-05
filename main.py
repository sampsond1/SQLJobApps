import sqlite3
from blessed import Terminal
from datetime import date

class Display:

    def __init__(self, terminal: Terminal):
        self.height = term.height
        self.width = term.width
        self.t = terminal
        # curr_ind dictionary will be used to map display id to actual database id
        self.curr_ind = {}
        # status_dict is the Python-side key for display status to database status. (SQL side done through CASE)
        self.status_dict = {'Lead' : 1, 'Applied' : 2, 'Followed Up' : 3, 'Heard Back' : 4, 'Interview' : 5, 'Second Interview' : 6, 'Hired' : 7, 'Rejected' : 0}
        # update_dict is the Python-side key for display field to database column
        self.update_dict = {'1': 'date', '2': 'company', '3':'job_title', '4':'status', '5':'source','6':'url', '7':'note', '8':'resolve'}

        with self.t.hidden_cursor():
            print(self.t.clear + self.t.home, end = '')
            # Checks to make sure screen is wide enough and tall enough
            # TODO fix this so it pauses before displaying
            while (self.t.height < 26 or self.t.width < 128):
                print(self.t.home + "Please resize your window to at least 26 height and 128 width.")
                print(f"Current Height: {self.t.height}  Current Width: {self.t.width}")
                
            # Writes the table to the screen
            self.offset = (self.t.width - 128) // 2
            
        # Main screen loop
        shouldQuit = False
        while not shouldQuit:
            self.display_table()
            p = self.prompt().lower()
            if len(p.split()) == 0: # Catches when no command is given
                shouldQuit = False
            if p == 'q' or p == 'quit': # Quit
                shouldQuit = True
                print(self.t.clear + self.t.home)
            elif p == 'a' or p == 'add': # Add
                self.add_entry()
            elif p.split()[0] in ['d', 'del', 'delete']: # Delete
                if len(p.split()) == 1:
                    self.error('ERR: Please indicate entry to delete')
                else:
                    self.del_entry(p.split()[1])
            elif p.split()[0] in ['s', 'sel', 'select']: # Select
                if len(p.split()) == 1:
                    self.error('ERR: Please indicate entry to select')
                else:
                    self.sel_entry(p.split()[1])
    
    def display_table(self):
        # Displays the table, populates info from the database
        # TODO: Implement page system, where only 25 pages show up
        print(self.t.clear + self.t.home, end = '')
        print(self.t.move_x(self.offset) + '+' + 3*'—' + '+' + 10*'—' + '+' + 30*'—' + '+' + 40*'—' + '+' + 16*'—' + '+' + 16*'—' + '+' + 5*'—' + '+')
        print(self.t.move_x(self.offset) + '|' + f'{'ID':^3}' + '|' + f'{'Date':^10}' + '|' + f'{'Company':^30}' + '|' + f'{'Position Title':^40}' + '|' + f'{'Status':^16}' + '|' + f'{'Source':^16}' + '|' + 'Done?' + '|')
        print(self.t.move_x(self.offset) + '+' + 3*'—' + '+' + 10*'—' + '+' + 30*'—' + '+' + 40*'—' + '+' + 16*'—' + '+' + 16*'—' + '+' + 5*'—' + '+')
        
        with sqlite3.connect('data.db') as connection:
            c=connection.cursor()
            query = '''
            SELECT id,date,company,job_title,
            CASE
                WHEN status = 1 THEN 'Lead'
                WHEN status = 2 THEN 'Applied'
                WHEN status = 3 THEN 'Followed Up'
                WHEN status = 4 THEN 'Heard Back'
                WHEN status = 5 THEN 'Interview'
                WHEN status = 6 THEN 'Second Interview'
                WHEN status = 7 THEN 'Hired'
                WHEN status = 0 THEN 'Rejected'
                ELSE 'CODE ERR'
            END,source,resolved
            FROM applications
            ORDER BY status DESC, date DESC;
            '''

            c.execute(query)
            rows = c.fetchall()        

        for i in range(len(rows)):
            # TODO: Loop total_string so that I can switch colors every other line
            row = rows[i]
            total_string = '|'+ f'{i+1:>3}'+ '|' + f'{row[1]:>10}' + '|' + f'{row[2]:<30}' + '|' + f'{row[3]:<40}' + '|' + f'{row[4]:<16}' + '|' + f'{row[5]:<16}' + '|' + f'{'✔' if row[6] == 'T' else '✖':^5}' + '|'
            if i % 2 == 0:
                # Add in colors here?
                print(self.t.move_x(self.offset) + total_string)
            elif i % 2 == 1:
                # Add in colors here?
                print(self.t.move_x(self.offset) + total_string)
            # Creates a dictionary of display IDs to actual database ids
            self.curr_ind[f'{i+1}'] = row[0]
        print(self.t.move_x(self.offset) + '+' + 3*'—' + '+' + 10*'—' + '+' + 30*'—' + '+' + 40*'—' + '+' + 16*'—' + '+' + 16*'—' + '+' + 5*'—' + '+')
        return
    
    def display_entry(self, ind : str):
        # Displays one specific entry at display index 'ind'
        if ind in self.curr_ind:
            # Gets the entry from the data base
            with sqlite3.connect('data.db') as connection:
                c = connection.cursor()
                query = f'''
                SELECT date, company, job_title,
                CASE
                    WHEN status = 1 THEN 'Lead'
                    WHEN status = 2 THEN 'Applied'
                    WHEN status = 3 THEN 'Followed Up'
                    WHEN status = 4 THEN 'Heard Back'
                    WHEN status = 5 THEN 'Interview'
                    WHEN status = 6 THEN 'Second Interview'
                    WHEN status = 7 THEN 'Hired'
                    WHEN status = 0 THEN 'Rejected'
                    ELSE 'CODE ERR'
                END, source, url, note,
                CASE
                    WHEN resolved = 'T' THEN 'True'
                    WHEN resolved = 'F' THEN 'False'
                    ELSE 'CODE ERR'
                END
                FROM applications
                WHERE id = {self.curr_ind[ind]};
                '''
                c.execute(query)
                row = c.fetchone()
            
            # Displays the entry
            print(self.t.clear + self.t.home)
            print(self.t.move_x(self.offset) + '+' + 126*'—' + '+')
            print(self.t.move_x(self.offset) + f'{'| ENTRY':<127}' + '|')
            print(self.t.move_x(self.offset) + '+' + 126*'—' + '+')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 1. Date: {row[0]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 2. Company: {row[1]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 3. Position Title: {row[2]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 4. Status: {row[3]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 5. Source: {row[4]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 6. URL: {row[5]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 7. Note: {row[6]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + f'{f'| 8. Resolved: {row[7]}':<127}' + '|')
            print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
            print(self.t.move_x(self.offset) + '+' + 126*'—' + '+')
            return

    def prompt(self):
        # Wrapper function that just puts an input() two lines up from the bottom
        print(self.t.move_xy(self.offset, self.height - 2) + self.t.clear_line(), end='')
        return input()
    
    def error(self, string):
        # Wrapper function that prints a message two lines up from the bottom
        print(self.t.move_xy(self.offset, self.t.height - 2) + string, end='')
        input()
        return

    def add_entry(self):
        # Function to add an entry

        # Displays the "ADD ENTRY" UI
        print(self.t.clear + self.t.home)
        print(self.t.move_x(self.offset) + '+' + 126*'—' + '+')
        print(self.t.move_x(self.offset) + f'{'| ADD ENTRY':<127}' + '|')
        print(self.t.move_x(self.offset) + '+' + 126*'—' + '+')
        print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
        print(self.t.move_x(self.offset) + f'{'| Company:':<127}' + '|')
        print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
        print(self.t.move_x(self.offset) + f'{'| Position Title:':<127}' + '|')
        print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
        print(self.t.move_x(self.offset) + f'{'| Status:':<127}' + '|')
        print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
        print(self.t.move_x(self.offset) + f'{'| Source:':<127}' + '|')
        print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
        print(self.t.move_x(self.offset) + f'{'| URL:':<127}' + '|')
        print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
        print(self.t.move_x(self.offset) + f'{'| Note:':<127}' + '|')
        print(self.t.move_x(self.offset) + '|' + 126*' ' + '|')
        print(self.t.move_x(self.offset) + '+' + 126*'—' + '+')

        # Moves the cursor to each field and gets input
        print(self.t.move_xy(self.offset + 12, 5), end='')
        company = input()
        print(self.t.move_xy(self.offset + 19, 7), end='')
        position = input()
        print(self.t.move_xy(self.offset + 11, 9), end='')
        try:
            status = self.status_dict[input()]
        except:
            status = -1
        print(self.t.move_xy(self.offset + 11, 11), end='')
        source = input()
        print(self.t.move_xy(self.offset + 8, 13), end='')
        url = input()
        print(self.t.move_xy(self.offset + 9, 15), end='')
        note = input()
        datee = str(date.today())

        # Inserts the entry in the database
        with sqlite3.connect('data.db') as connection:
            c=connection.cursor()
            query = '''
            INSERT INTO applications (date, company, job_title, status, source, url, note, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'F')
            '''

            c.execute(query, (datee, company, position, status, source, url, note))
            connection.commit()
    
    def del_entry(self, ind : str):
        # Function to delete an entry with a certain display id 'ind'
        # TODO: Add confirmation for deleting a record
        if ind in self.curr_ind:
            with sqlite3.connect('data.db') as connection:
                c = connection.cursor()
                query = f'''
                DELETE FROM applications
                WHERE id = {self.curr_ind[ind]};
                '''
                c.execute(query)
                connection.commit()
        else:
            self.error('ERR: Invalid argument')
            input()
    
    def sel_entry(self, ind : str):
            # Function to select an entry

            # Entry screen loop            
            shouldQuit2 = False
            while shouldQuit2 == False:
                self.display_entry(ind)
                p = self.prompt()
                if len(p.split()) == 0: # Catches no command given
                    shouldQuit2 = False
                elif p in ['q', 'quit', 'b', 'back']: # Exits the lop and goes to the main screen
                    shouldQuit2 = True
                elif p.split()[0] in ['u', 'upd', 'update']: # Updates a field in the entry
                    if len(p.split()) <= 2:
                        self.error('ERR: Please indicate field to update and new value')
                    elif p.split()[1] not in self.update_dict:
                        self.error('ERR: Invalid field')
                    else:
                        field = self.update_dict[p.split()[1]]
                        value =" ".join(p.split()[2:])
                        with sqlite3.connect('data.db') as connection:
                            c = connection.cursor()
                            query = f'''
                            UPDATE applications
                            SET {field} = ?
                            WHERE id = ?
                            '''
                            c.execute(query, (value, self.curr_ind[ind]))
                            connection.commit()
        


if __name__ == "__main__":
    term = Terminal()
    frame = Display(term)