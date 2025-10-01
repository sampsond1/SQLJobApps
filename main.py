import sqlite3
from blessed import Terminal

class Display:

    def __init__(self, terminal: Terminal):
        self.height = term.height
        self.width = term.width
        self.t = terminal
        self.curr_ind = {}

        with self.t.hidden_cursor():
            print(self.t.clear + self.t.home, end = '')
            # Checks to make sure screen is wide enough and tall enough
            while (self.t.height < 26 or self.t.width < 128):
                print(self.t.home + self.t.green + "Please resize your window to at least 26 height and 128 width.")
                print(f"Current Height: {self.t.height}  Current Width: {self.t.width}")
            # Writes the table to the screen
            self.offset = (self.t.width - 128) // 2
            

        shouldQuit = False
        while not shouldQuit:
            self.display_table(self.t)
            p = self.prompt().lower()
            if p == 'q' or p == 'quit':
                shouldQuit = True
    
    def display_table(self, t):
        print(self.t.clear + self.t.home, end = '')
        print(self.t.move_x(self.offset) + '+' + 3*'—' + '+' + 10*'—' + '+' + 30*'—' + '+' + 40*'—' + '+' + 16*'—' + '+' + 16*'—' + '+' + 5*'—' + '+')
        print(self.t.move_x(self.offset) + '|' + f'{'ID':^3}' + '|' + f'{'Date':^10}' + '|' + f'{'Company':^30}' + '|' + f'{'Position Title':^40}' + '|' + f'{'Status':^16}' + '|' + f'{'Source':^16}' + '|' + 'Done?' + '|')
        print(self.t.move_x(self.offset) + '+' + 3*'—' + '+' + 10*'—' + '+' + 30*'—' + '+' + 40*'—' + '+' + 16*'—' + '+' + 16*'—' + '+' + 5*'—' + '+')
        
        with sqlite3.connect('data.db') as connection:
            c=connection.cursor()
            query = f'''
            SELECT id,date,company,job_title,
            CASE
                WHEN status = 1 THEN 'Lead'
                WHEN status = 2 THEN 'Applied'
                WHEN status = 3 THEN 'Followed Up'
                WHEN status = 4 THEN 'Heard Back'
                WHEN status = 5 THEN 'Interview'
                WHEN status = 6 THEN 'Second Interview'
                WHEN status = 7 THEN 'Hired'
                ELSE 'CODE ERR'
            END,source,resolved
            FROM applications
            ORDER BY status DESC, date DESC;
            '''

            c.execute(query)
            rows = c.fetchall()

        for i in range(len(rows)):
            row = rows[i]
            total_string = '|'+ f'{i+1:>3}'+ '|' + f'{row[1]:>10}' + '|' + f'{row[2]:<30}' + '|' + f'{row[3]:<40}' + '|' + f'{row[4]:<16}' + '|' + f'{row[5]:<16}' + '|' + f'{'✔' if row[6] == 'T' else '✖':^5}' + '|'
            if i % 2 == 0:
                # Add in colors here?
                print(self.t.move_x(self.offset) + total_string)
            elif i % 2 == 1:
                # Add in colors here?
                print(self.t.move_x(self.offset) + total_string)
            # 
            self.curr_ind[f'{i+1}'] = row[0]
        print(self.t.move_x(self.offset) + '+' + 3*'—' + '+' + 10*'—' + '+' + 30*'—' + '+' + 40*'—' + '+' + 16*'—' + '+' + 16*'—' + '+' + 5*'—' + '+')
        return
    
    def prompt(self):
        print(self.t.move_xy(self.offset, self.height - 1), end='')
        return input()
        



if __name__ == "__main__":
    term = Terminal()
    frame = Display(term)