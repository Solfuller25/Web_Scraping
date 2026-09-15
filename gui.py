import tkinter as tk
import getpass
import threading
from tkinter import filedialog
from tkinter import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pandas import DataFrame

# Global variables
baseURL = ''
searchURL = ''
numberList = []
visitedSites = []

# Initialize tkinter window
progressText = ''
window = tk.Tk()
progressLabel = tk.Label(fg='red')
progressLabel.place(relx=0.39, rely=0.9)
window.iconbitmap('icon_hd.ico')
t1 = threading

# My company search GUI class
class GUI:

    def __init__(self, name):
        self.name = name
        self.startTK()

    def startTK(self):
        # Create main window
        window.geometry("650x275")
        window.title("Company Search")

        # Create a label
        label = tk.Label(window, text="Enter the required info below, then press 'Search'", font='Helvetica 12 bold')
        label.place(relx=0.2, rely=0.1)

        # Create company entry label
        companyLabel = tk.Label(window, text="Company type")
        companyLabel.place(relx=0.25, rely=0.3)

        # Create company type entry box
        companyTypeEntry = tk.Entry(window, width=50)
        companyTypeEntry.place(relx=0.25, rely=0.4)

        # Create state entry label
        stateLabel = tk.Label(window, text="State abbreviation")
        stateLabel.place(relx=0.25, rely=0.5)

        # Create state to search in box
        stateEntry = tk.Entry(window, width=50)
        stateEntry.place(relx=0.25, rely=0.6)

        # Create a button
        button = tk.Button(window, text="Search", command=lambda: self.startSearchThread(companyTypeEntry.get(), stateEntry.get()))
        button.place(relx=0.46, rely=0.8)

        # Start the GUI
        window.mainloop()


    # Method to start threading
    def startSearchThread(self, companyType, state):
        # Execute the search on a thread
        t1 = threading.Thread(target=self.executeBBBSearch, args=(companyType, state))
        t1.start()
        t1.join()

    
    # This method retrieves company information from the BBB website
    def executeBBBSearch(self, companyType, state):
        pageNumber = 1
        name_array = []
        number_array = []
        address_array = []
        while(pageNumber <= 15):
            progressText = "Page number: " + str(pageNumber)
            print(progressText)
            # Web access setup
            options = Options()
            options.add_argument("--headless=new")
            # User Agent to avoid looking like a bot
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            dr = webdriver.Chrome(options=options)

            # Set the base URL for the search
            url = f"https://www.bbb.org/search?page={pageNumber}&sort=Relevance&touched=1&find_country=USA"
            if companyType != '':
                url += '&find_text=' + companyType.replace(' ', '%20')
            if state != '':
                url += '&filter_state=' + state

            print(url)

            # Try to access the site, if failure exit loop
            try:
                dr.get(url)
            except:
                break

            # Use selenium to find company css cards
            divs = dr.find_elements(By.CLASS_NAME, 'result-card')

            # Loop through identified company css cards
            for div in divs:
                try:
                    name = div.find_element(By.CLASS_NAME, 'result-business-name')
                    number = div.find_element(By.CLASS_NAME, 'text-black')
                    address = div.find_element(By.CSS_SELECTOR, 'p.bds-body.text-size-5.text-gray-70')
                    if (name.text not in name_array) and ('advertisement' not in name.text) and (name.text != '') and (number.text != '') and (address.text != ''):
                        name_array.append(name.text)
                        number_array.append(number.text)
                        try:
                            address_array.append(address.text.split("\n")[1])
                        except:
                            address_array.append(address.text)
                except:
                    print("There was an error")
                    print(div.text)
        
            # Increment page number before next iteration
            pageNumber += 1

        try:
            # Set up excel sheet
            df = DataFrame({'Company Name': name_array, 'Phone Number': number_array, 'Address': address_array})
            print('Saving file in downloads for ' + getpass.getuser())
            with filedialog.asksaveasfile(
                mode='w', 
                initialdir=f'C:\\users\\{getpass.getuser()}\\downloads\\',
                initialfile=f'{companyType.replace(' ','_')}_{state}.xlsx',
                defaultextension='.xlsx', 
                filetypes=[('Excel Files', '*.xlsx'), ('CSV Files', '*.csv')]
            ) as file:
                #writer = ExcelWriter(file.name, engine='xlsxwriter')
                df.to_excel(file.name)

            # Set progress to 'finished'
            progressLabel.config(text='Your file has been saved')
        except:
            # Alert of error
            progressLabel.config(text='There was an error when saving your file.')

