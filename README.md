This small scraping project was created to collect data Booking.com on offers through scraping techniques. The script utilises Selenium and Beautifulsoup.

The main part of the script is written in the twitterScraper.py file. The project consists additionally of modules for creating log files (logic stored in loggingSettings.py) and for sharing the scrape results in a .csv file with a selected e-mail address (twitterEmailSender.py). Settings file (settings.txt) was created to store various information (eg. e-mails, search and save back settings) and to enhance general reusability. The enhance portability there is a possibility to compile an .exe file of the script via pyInstaller (necessary tweak of the file paths is added via portability.py).


0. settings.txt
Setting file (under name settings.txt in Settings folder) needs to provide following information in JSON format:
"destination" - destination place, eg. city (str)
"checkin_date" - start date presented in "YYYY-MM-DD" format (str)
"checkout_date" - leave date presented in "YYYY-MM-DD" format (str)
"group_adults" - number of visiting adults (int)
"no_rooms" - number of rented rooms (int)
"group_children" - number of visiting children (int)
"expected_screen_scrolls" - approximate number of windows to collect via script (int)
"user_agent" - user agent settings (str)


3. bookingScraper.py
After loading the setting file the script creates the basic elements of the result table in the form of lists. A chromedriver instance is created with a user-agent setting (headless options are hardcoded in the function). The script creates a url link based on the entered settings in the settings.txt file. The script enters the site via the created url, and omits the cookies window and potential advert. The script proceeds with scraping loops fetching single offer boxes and extracting information on names, prices (regular price, potential discounted price, and normalised price for a single adult), rate of the location, number of votes on which the rate was calculated, and links (to the offer and to the map location). Fetched results are cleaned via regex patterns, and then are feeding the result list. The result list and the header list are passed to the prep_results function that creates a Pandas DataFrame, clears duplicates, and saves the results to a .csv file with a name based on the destination name.


4. portability.py
The stored here resource_path function enables creating portable .exe files via pyInstaller. Th function controls the path of the files, to enable accessing them through temporary folders created by pyInstaller, when the project is compiled. Suggested pyInstaller settings to ensure adjustments of settings and basic self-maintenance of chromedriver file:
pyinstaller main.py -w --onedir --add-data=./Settings/settings.txt:./Settings --add-data=./ChromeDriver/chromedriver.exe:./ChromeDriver --add-data=./Settings/log_file.log:./Settings --add-data=./SaveBacks/Manchester.csv:./SaveBacks
Alternativelly the /ChromeDriver and /SaveBacks locations can be created manually in ./dist/main/_internal after the compile.


Hope you'll enjoy reading the code.

Regards,
jp

jakubpoplawski@live.com
