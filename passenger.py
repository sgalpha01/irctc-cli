import json
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select


from journey import JourneyManager

from login import LoginManager


class PassengerManager:
    def __init__(self, driver):
        if driver is None:
            raise ValueError("A webdriver instance is required filling passenger details.")
        
        self.driver = driver
        self.passenger_details = self.load_passenger_details()

    def load_passenger_details(self):
        with open("journey_details.json", 'r') as file:
            data = json.load(file)
            passengers = data['passengers']
            if len(passengers) == 0:
                raise ValueError("There must be at least one passenger.")
            if len(passengers) > 6:
                raise ValueError("There can be a maximum of 6 passengers.")
            return data

    def fill_passenger_details(self):
        passengers = self.passenger_details['passengers']

        for _ in range(1, len(passengers)):
            add_passenger_button = WebDriverWait(self.driver, 180).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '+ Add Passenger')]")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", add_passenger_button)
            self.driver.execute_script("arguments[0].click();", add_passenger_button)

        passenger_names = self.driver.find_elements(By.CSS_SELECTOR, "[formcontrolname='passengerName']")
        passenger_ages = self.driver.find_elements(By.CSS_SELECTOR, "[formcontrolname='passengerAge']")
        passenger_genders = self.driver.find_elements(By.CSS_SELECTOR, "[formcontrolname='passengerGender']")
        passenger_berth_choices = self.driver.find_elements(By.CSS_SELECTOR, "[formcontrolname='passengerBerthChoice']")

        passenger_boxes = list(zip(passenger_names, passenger_ages, passenger_genders, passenger_berth_choices))
        print(f"Found {len(passenger_boxes)} passenger boxes.")

        for passenger, passenger_box in zip(passengers, passenger_boxes):
            self.fill_individual_passenger(passenger, passenger_box)


    def fill_individual_passenger(self, passenger, passenger_box):
        # Unpack the elements from the passenger_box tuple
        name_input, age_input, gender_select, berth_select = passenger_box

        try:
            name_input.click()
            # Fill in the passenger's name character by character to simulate human typing
            for char in passenger['name']:
                print(f"Sending {char} to name input")
                name_input.send_keys(char)
                time.sleep(10)
            name_input.send_keys(Keys.TAB)
        except Exception as e:
            print(e)
            print("Could not fill passenger name. Trying again...")
            self.fill_individual_passenger(passenger, passenger_box)


        # Fill in the passenger's age
        self.driver.execute_script("arguments[0].value = arguments[1];", age_input, passenger['age'])

        # Select the passenger's gender
        Select(gender_select).select_by_visible_text(passenger['gender'])

        # Select the passenger's berth preference
        Select(berth_select).select_by_value(passenger['berthPreference'])



    def close_browser(self):
        self.driver.close()

if __name__ == "__main__":
    driver = webdriver.Firefox()
    login_manager = LoginManager(driver=driver)
    login_manager.login()
    journey_manager = JourneyManager(driver=driver)
    journey_manager.fill_journey_details()
    journey_manager.fill_train_details()
    passenger_manager = PassengerManager(driver=driver)
    passenger_manager.fill_passenger_details()
    # Keep the browser open for a while to observe or close it
    input("Press Enter to close the browser...")
    journey_manager.close_browser()

