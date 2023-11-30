import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import dotenv_values

from utils import CaptchaSolver


class LoginManager:
    def __init__(self, driver=None, captcha_method="manual"):
        config = dotenv_values(".env")
        self.driver = driver if driver else webdriver.Firefox()
        self.driver.maximize_window()
        self.url = "https://www.irctc.co.in/nget/train-search"
        self.username = config.get("USERNAME")
        self.password = config.get("PASSWORD")
        self.captcha_method = captcha_method

    def login(self):
        try:
            self.driver.get(self.url)
            # Click the login button
            self.driver.find_element(By.CLASS_NAME, "loginText").click()

            # Wait for the login modal to be displayed and the form inside it to be loaded
            WebDriverWait(self.driver, timeout=180).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input[formcontrolname='userid']")
                )
            )

            # Locate the username, password fields and the sign-in button
            username_field = self.driver.find_element(
                By.CSS_SELECTOR, "input[placeholder='User Name']"
            )
            password_field = self.driver.find_element(
                By.CSS_SELECTOR, "input[placeholder='Password']"
            )
            captcha_field = self.driver.find_element(
                By.CSS_SELECTOR, "input[placeholder='Enter Captcha']"
            )

            # Enter username and password
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)

            if self.captcha_method != "manual":
                captcha_solver = CaptchaSolver(method=self.captcha_method)

                # Wait for the captcha image to be present in the DOM
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img.captcha-img"))
                )
                
                # Get the captcha image source
                captcha_img = self.driver.find_element(
                    By.CSS_SELECTOR, "img.captcha-img"
                ).get_attribute("src")
                base64_image = captcha_img.split(",")[1]

                # Solve captcha automatically
                captcha_solution = captcha_solver.solve_captcha(base64_image)
                print(f"CAPTCHA solution: {captcha_solution}")
                captcha_field = self.driver.find_element(
                    By.CSS_SELECTOR, "input[placeholder='Enter Captcha']"
                )
                captcha_field.send_keys(captcha_solution)

                # Click the 'SIGN IN' button
                sign_in_button = self.driver.find_element(
                    By.XPATH, "//button[normalize-space()='SIGN IN']"
                )
                sign_in_button.click()

                # Check for invalid captcha message
                error_message = self.driver.find_element(
                    By.CSS_SELECTOR, ".loginError"
                ).text
                if "invalid captcha" in error_message.lower():
                    print("Invalid Captcha, falling back to manual mode...")
                    captcha_solver.method = "manual"

        except TimeoutException:
            print(
                "The login form did not load in time. Please check your internet connection or try again later."
            )
        except NoSuchElementException:
            print(
                "Could not find one of the elements on the page. The page structure might have changed."
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Add any additional steps post-login if necessary
        self.is_logged_in()

    def is_logged_in(self):
        try:
            WebDriverWait(self.driver, 180).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//a[@href='/nget/logout']/span[contains(text(), 'Logout')]",
                    )
                )
            )
            print("Login successful!")
            return True
        except TimeoutException:
            print("Login failed or timed out!")
            return False

    def close_browser(self):
        self.driver.quit()


# Usage example
if __name__ == "__main__":
    driver = webdriver.Firefox()
    login_manager = LoginManager(driver=driver)
    login_manager.login()
    # Keep the browser open for a while to observe or close it
    input("Press Enter to close the browser...")
    login_manager.close_browser()
