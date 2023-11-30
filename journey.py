import json
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class JourneyManager:
    def __init__(self, driver=None):
        self.url = "https://www.irctc.co.in/nget/train-search"
        self.driver = driver if driver else webdriver.Firefox()
        self.driver.maximize_window()

        with open("journey_details.json") as file:
            self.journey_details = json.load(file)

    def fill_journey_details(self):
        try:
            if self.driver.current_url == "about:blank":
                self.driver.get(self.url)

            # Wait for the 'From' field to be clickable
            WebDriverWait(self.driver, 180).until(
                EC.visibility_of_element_located((By.ID, "origin"))
            )

            # Fill the 'From' field
            self.fill_station(direction="from")

            # Fill the 'To' field
            self.fill_station(direction="to")

            # Select the quota
            self.select_quota()

            # Fill the 'Date' field
            self.fill_date()

        except TimeoutException:
            print("The form did not load within the expected time.")
        except Exception as e:
            print(f"An exception occurred: {e}")

    def fill_train_details(self):
        try:
            # Wait for the train list to load
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "app-train-avl-enq"))
            )

            # Get all the train boxes
            train_boxes = self.driver.find_elements(
                By.CSS_SELECTOR, "app-train-avl-enq"
            )

            # Loop through each train box to find the required train
            for box in train_boxes:
                # Check if the train heading matches the required train number
                train_heading = box.find_element(
                    By.CSS_SELECTOR, ".train-heading strong"
                ).text
                if self.journey_details["trainNumber"] in train_heading:
                    print(f"Train {self.journey_details['trainNumber']} found!")
                    break
            else:
                # This block executes if the train was not found in any of the train boxes
                raise Exception(
                    f"Train {self.journey_details['trainNumber']} not found!"
                )

            # Refresh the seat availability for the required class
            availability_box = self.refresh_seat_availability(box)
            availability_box.click()

            # Locate the 'Book Now' button
            book_now_button = self.driver.find_element(
                By.XPATH,
                "//button[contains(@class, 'btnDefault') and contains(@class, 'train_Search') and not(contains(@class, 'disable-book'))]",
            )

            # Click the "Book Now" button
            book_now_button.click()

        except TimeoutException:
            print("Timed out waiting for train details to load.")

    def fill_station(self, direction="from"):
        if direction == "from":
            station_field = self.driver.find_element(By.ID, "origin")
        elif direction == "to":
            station_field = self.driver.find_element(By.ID, "destination")
        else:
            raise Exception("Invalid station direction specified")

        actions = ActionChains(self.driver)
        actions.send_keys_to_element(
            station_field, self.journey_details[f"{direction}Station"]
        )
        actions.send_keys(Keys.ARROW_DOWN)
        actions.send_keys(Keys.RETURN)
        actions.perform()

    def select_quota(self):
        # Click the quota dropdown to open it
        quota_dropdown = self.driver.find_element(By.ID, "journeyQuota")

        # Choose the quota by simulating keypresses
        ActionChains(self.driver).click(quota_dropdown).perform()
        selected_quota = self.driver.find_elements(
            By.CSS_SELECTOR,
            "span.ui-dropdown-label.ui-inputtext.ui-corner-all.ng-star-inserted",
        )[1].text
        while selected_quota != self.journey_details["quota"]:
            ActionChains(self.driver).click(quota_dropdown).send_keys(
                Keys.ARROW_DOWN
            ).perform()
            selected_quota = self.driver.find_elements(
                By.CSS_SELECTOR,
                "span.ui-dropdown-label.ui-inputtext.ui-corner-all.ng-star-inserted",
            )[1].text

            try:
                confirm_button = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "button.ui-confirmdialog-acceptbutton.ui-button.ui-widget.ui-state-default",
                )
                ActionChains(self.driver).click(confirm_button).perform()
            except NoSuchElementException:
                continue

    def fill_date(self):
        date_field = self.driver.find_element(By.ID, "jDate")

        # Enter the date using simulated keypresses
        actions = ActionChains(self.driver)
        actions.click(date_field)
        actions.key_down(Keys.CONTROL)
        actions.send_keys("a")
        actions.key_up(Keys.CONTROL)
        actions.send_keys(Keys.BACKSPACE)
        actions.send_keys_to_element(date_field, self.journey_details["journeyDate"])
        actions.send_keys(Keys.RETURN)
        actions.perform()

    def refresh_seat_availability(self, train_box):
        # Convert the journey date from string to a datetime object
        journey_date_str = self.journey_details["journeyDate"]
        journey_date = datetime.strptime(journey_date_str, "%d/%m/%Y").strftime(
            "%a, %d %b"
        )

        # Find the refresh link for the desired class and click it
        class_name = self.journey_details["class"].upper()
        try:
            class_element = WebDriverWait(train_box, 60).until(
                EC.presence_of_element_located(
                    (By.XPATH, f".//td/div[contains(., '{class_name}')]")
                )
            )
            refresh_link = class_element.find_element(
                By.XPATH, ".//div[contains(@class, 'link')]"
            )
            refresh_link.click()

            # Wait for the table containing the class and availability info to be visible
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f".//div[contains(@class, 'pre-avl')][.//strong[contains(text(), '{journey_date}')]]",
                    )
                )
            )

            availability_box = train_box.find_element(
                By.XPATH,
                f".//div[contains(@class, 'pre-avl')][.//strong[contains(text(), '{journey_date}')]]",
            )
            availability_status = availability_box.find_element(
                By.XPATH,
                ".//div[contains(@class, 'AVAILABLE') or contains(@class, 'WL') or contains(@class, 'REGRET')]",
            ).text
            print(
                f"For the class {class_name}, the availability status is: {availability_status}"
            )
            return availability_box

        except TimeoutException:
            print("Timed out waiting for the seat availability to refresh.")

    def close_browser(self):
        self.driver.close()


# Usage example
if __name__ == "__main__":
    journey_manager = JourneyManager()
    journey_manager.fill_journey_details()
    journey_manager.fill_train_details()
    # Keep the browser open for a while to observe or close it
    input("Press Enter to close the browser...")
    journey_manager.close_browser()
