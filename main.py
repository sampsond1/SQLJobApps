import sqlite3
from blessed import Terminal
from datetime import date

class Display:

    def __init__(self, terminal: Terminal):
        self.height = term.height
        self.width = term.width
        self.t = terminal
        self.curr_ind = {}
        self.status_dict = {'Lead' : 1, 'Applied' : 2, 'Followed Up' : 3, 'Heard Back' : 4, 'Interview' : 5, 'Second Interview' : 6, 'Hired' : 7, 'Rejected' : 0}

        with self.t.hidden_cursor():
            print(self.t.clear + self.t.home, end = '')
            # Checks to make sure screen is wide enough and tall enough
            while (self.t.height < 26 or self.t.width < 128):
                print(self.t.home + "Please resize your window to at least 26 height and 128 width.")
                print(f"Current Height: {self.t.height}  Current Width: {self.t.width}")
            # Writes the table to the screen
            self.offset = (self.t.width - 128) // 2
            

        shouldQuit = False
        while not shouldQuit:
            self.display_table(self.t)
            p = self.prompt().lower()
            if p == 'q' or p == 'quit':
                shouldQuit = True
                print(self.t.clear + self.t.home)
            elif p == 'a' or p == 'add':
                self.add_entry()
            elif len(p.split()) != 0 and p.split()[0] in ['d', 'del', 'delete']:
                if len(p.split()) == 1:
                    print(self.t.move_xy(self.offset, self.t.height - 1) + 'ERR: Please indicate entry to delete')
                    input()
                else:
                    self.del_entry(p.split()[1])
    
    def display_table(self, t):
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
            # TO DO: Loop this so that I can switch colors every other line
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
    
    def prompt(self):
        print(self.t.move_xy(self.offset, self.height - 2), end='')
        return input()
    
    def add_entry(self):
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
        with sqlite3.connect('data.db') as connection:
            c=connection.cursor()
            query = '''
            INSERT INTO applications (date, company, job_title, status, source, url, note, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'F')
            '''

            c.execute(query, (datee, company, position, status, source, url, note))
            connection.commit()
    
    def del_entry(self, ind : str):
        # TO DO: Add confirmation for deleting a record
        if ind in self.curr_ind:
            with sqlite3.connect('data.db') as connection:
                c = connection.cursor()
                query = f'''
                DELETE FROM applications
                WHERE id = {self.curr_ind[ind]};
                '''
                c.execute(query)
                connection.commit()
        
        
        



if __name__ == "__main__":
    term = Terminal()
    frame = Display(term)