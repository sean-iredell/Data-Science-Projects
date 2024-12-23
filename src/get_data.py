import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# CANNOT BE HEADLESS OR SITE WILL REJECT THE REQUEST
chrome_options = Options()
chromedriver_path = '/usr/local/bin/chromedriver' # Replace with your chromedriver path
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)


try:
    driver.get("https://stats.ncaa.org/")
    print("Website loaded successfully.")

 # Change division, days, and sport
    division_dropdown = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="season_division_id_select_chosen"]'))
    )
    division_dropdown.click()

    division_one_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="season_division_id_select_chosen"]/div/ul/li[2]'))
    )
    division_one_option.click()
    print("Division One selected successfully.")

    sport_code_dropdown = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="sport_code_select_chosen"]'))
    )
    sport_code_dropdown.click()

    specific_sport_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="sport_code_select_chosen"]/div/ul/li[5]'))
    )
    specific_sport_option.click()
    print("Specific sport selected successfully.")

    # Xpaths for teams (full xpaths are for away teams because the site handles away teams as a subpath of the home team)
    games = {
        "11/27/2024": [
            '//*[@id="contest_5729841"]/td[2]/a',  # Gonzaga
            '/html/body/div[2]/div/div/div/div/div[20]/div[2]/div/div/div/table/tbody/tr[4]/td[2]/a',  # Auburn
            '/html/body/div[2]/div/div/div/div/div[13]/div[1]/div/div/div/table/tbody/tr[4]/td[2]/a',  # Iowa State
            '/html/body/div[2]/div/div/div/div/div[21]/div[1]/div/div/div/table/tbody/tr[4]/td[2]/a',  # Oklahoma
            '/html/body/div[2]/div/div/div/div/div[15]/div[1]/div/div/div/table/tbody/tr[3]/td[2]/a',  # Tennessee
            '/html/body/div[2]/div/div/div/div/div[34]/div[1]/div/div/div/table/tbody/tr[3]/td[2]/a',  # Marquette
            '/html/body/div[2]/div/div/div/div/div[26]/div[2]/div/div/div/table/tbody/tr[3]/td[2]/a'   # Cincinnati
        ],
        "12/14/2024": [
            '/html/body/div[2]/div/div/div/div/div[23]/div[2]/div/div/div/table/tbody/tr[4]/td[2]/a',  # Florida
            '//*[@id="contest_5729195"]/td[2]/a',  # UCLA
            '/html/body/div[2]/div/div/div/div/div[36]/div[1]/div/div/div/table/tbody/tr[3]/td[2]/a'   # Kentucky
        ]
    }

# Xpath for data for every team

    game_by_game_xpath = '/html/body/div[2]/div/div/div/div/div/nav/ul/li[4]/a' 

    all_data = []
    def extract_game_by_game_data():
        try:
            table = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div/div[5]/div/div/div/div[2]/table')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                row_data = [cell.text.strip() for cell in cells]
                if row_data:  # Avoid empty rows
                    data.append(row_data)
            headers = [header.text.strip() for header in rows[0].find_elements(By.TAG_NAME, 'th')]
            return headers, data
        except Exception as e:
            print(f"Error while extracting game by game data: {e}")
            return [], []

    # For loop to get all the teams
    for game_date, contest_xpaths in games.items():
        game_date_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div/input'))
        )
        driver.execute_script("arguments[0].value = arguments[1];", game_date_input, game_date)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", game_date_input)
        print(f"Game date set to {game_date}.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, contest_xpaths[0]))
        )

        for contest_xpath in contest_xpaths:
            contest_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, contest_xpath))
            )
            team_name = contest_link.text.strip()
            contest_link.click()
            print(f"Clicked on contest: {team_name}")

            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2)) 
            current_window = driver.current_window_handle
            all_windows = driver.window_handles

            # Handle new tabs opening
            for window in all_windows:
                if window != current_window:
                    driver.switch_to.window(window)
                    print(f"Switched to new tab for {team_name}")
                    break

            game_by_game_tab = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, game_by_game_xpath))
            )

            action = ActionChains(driver)
            action.move_to_element(game_by_game_tab).click().perform()
            print(f"Clicked on 'Game by Game' tab for {team_name}")

            # Table that contains the html data to be parsed
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div/div/div[5]/div/div/div/div[2]/table'))
            )

            headers, data = extract_game_by_game_data()
            if headers and data:
                for row in data:
                    row.insert(0, team_name)
                all_data.extend(data)

            driver.close()
            driver.switch_to.window(current_window)

    # Scrape data into a dataframe and export as a csv
    if all_data:
        expected_columns = len(headers)
        for i, row in enumerate(all_data):
            if len(row) < expected_columns:
                # Handle exceptions
                row.extend(["MISSING"] * (expected_columns - len(row)))
            elif len(row) > expected_columns:
                all_data[i] = row[:expected_columns]

        df = pd.DataFrame(all_data, columns=headers)
        desktop_path = os.path.expanduser("~/Desktop") # Define desired csv path
        file_path = os.path.join(desktop_path, "extracted_data.csv")
        df.to_csv(file_path, index=False)
        print(f"Data saved successfully to {file_path}")
    else:
        print("No data was extracted.")

finally:
    driver.quit()
