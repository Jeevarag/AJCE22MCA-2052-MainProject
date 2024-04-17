# Test 1: Login test
# from django.test import LiveServerTestCase
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# class LoginformTest(LiveServerTestCase):

#     def testloginpage(self):
#         driver = webdriver.Firefox()

#         driver.get('http://127.0.0.1:8000/login/')

#         username_input = driver.find_element(By.NAME, 'username')
#         password_input = driver.find_element(By.NAME, 'password')
#         login_button = driver.find_element(By.NAME, 'submit')
#         username_input.send_keys('testuser1')
#         password_input.send_keys('Tes123@')
#         login_button.click()  # Use click() instead of send_keys(Keys.RETURN) for the button click event

#         # Wait for the URL to contain '/home/' after successful login
#         WebDriverWait(driver, 10).until(EC.url_contains('/home/'))

#         # Assert specific elements or texts to ensure proper login
#         assert 'Welcome to SkillSwap' in driver.page_source

#         # Close the WebDriver instance
#         driver.quit()


#Test 2: Add Skill
# from django.test import LiveServerTestCase
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# class AddSkillTest(LiveServerTestCase):

#     def test_add_skill(self):
#         # Initialize WebDriver
#         driver = webdriver.Firefox()

#         try:
#             # Login
#             self.login(driver)

#             # Navigate to profile page
#             self.navigate_to_profile(driver)

#             # Click on "Add Skill" button
#             self.click_add_skill(driver)

#             # Fill in skill details
#             self.fill_skill_details(driver, category='Art and Design', skill_name='Drawing', description='Oil paint artist')

#             # Submit the form
#             self.submit_skill_form(driver)

#             # Check redirection to profile page
#             self.check_redirection_to_profile(driver)
#         finally:
#             # Close the WebDriver instance
#             driver.quit()

#     def login(self, driver):
#         # Navigate to login page
#         driver.get('http://127.0.0.1:8000/login/')

#         # Fill in login details
#         username_input = driver.find_element(By.NAME, 'username')
#         password_input = driver.find_element(By.NAME, 'password')
#         login_button = driver.find_element(By.NAME, 'submit')
#         username_input.send_keys('testuser1')
#         password_input.send_keys('Tes123@')
#         login_button.click()

#         # Wait for redirection to home page
#         WebDriverWait(driver, 10).until(EC.url_contains('/home/'))

#     def navigate_to_profile(self, driver):
#         # Click on "My Profile" link
#         my_profile_link = driver.find_element(By.XPATH, '//a[text()="My profile"]')
#         my_profile_link.click()

#         # Wait for redirection to profile page
#         WebDriverWait(driver, 10).until(EC.url_contains('/profile/'))

#     def click_add_skill(self, driver):
#         # Click on "Add Skill" button
#         add_skill_button = driver.find_element(By.ID, 'skill_add')
#         add_skill_button.click()

#         # Wait for redirection to add skill page
#         WebDriverWait(driver, 10).until(EC.url_contains('/add_skill/'))

#     def fill_skill_details(self, driver, category, skill_name, description):
#         # Select category from dropdown
#         category_dropdown = driver.find_element(By.ID, 'id_category')
#         category_dropdown.send_keys(category)

#         # Fill in skill name
#         skill_name_input = driver.find_element(By.ID, 'id_name')
#         skill_name_input.send_keys(skill_name)

#         # Fill in skill description
#         description_input = driver.find_element(By.ID, 'id_description')
#         description_input.send_keys(description)

#     def submit_skill_form(self, driver):
#         # Submit the form
#         submit_button = driver.find_element(By.XPATH, '//button[text()="Add Skill"]')
#         submit_button.click()

#     def check_redirection_to_profile(self, driver):
#         # Wait for redirection to profile page
#         WebDriverWait(driver, 10).until(EC.url_contains('/profile/'))

#         # Assert presence of expected elements on profile page
#         assert 'About Me' in driver.page_source


#Test 3: Follow and Unfollow feature
# from django.test import LiveServerTestCase
# from selenium import webdriver
# import time
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# class FollowUnfollowTest(LiveServerTestCase):

#     def test_follow_unfollow(self):
#         driver = webdriver.Firefox()

#         try:
#             self.login_and_navigate_to_home(driver)
#             self.navigate_to_user_list_page(driver)
#             self.select_user(driver)
#             self.follow_unfollow_user(driver)

#         finally:
#             driver.quit()

#     def login_and_navigate_to_home(self, driver):
#         driver.get('http://127.0.0.1:8000/login/')
#         username_input = driver.find_element(By.NAME, 'username')
#         password_input = driver.find_element(By.NAME, 'password')
#         login_button = driver.find_element(By.NAME, 'submit')
#         username_input.send_keys('testuser1')
#         password_input.send_keys('Tes123@')
#         login_button.click()

#         WebDriverWait(driver, 10).until(EC.url_contains('/home/'))

#     def navigate_to_user_list_page(self, driver):
#         teach_action_container = driver.find_element(By.ID, 'teach')
#         teach_action_container.click()
#         WebDriverWait(driver, 10).until(EC.url_contains('/learn/'))

#     def select_user(self, driver):
#         user_links = driver.find_elements(By.XPATH, '//a[@id="users_name"]')
#         user_links[0].click()
#         WebDriverWait(driver, 10).until(EC.url_contains('/profile/'))
#         time.sleep(1)

#     def follow_unfollow_user(self, driver):
#         try:
#             unfollow_button = driver.find_element(By.ID, 'unfollow')
#             unfollow_button.click()
#             time.sleep(3) 
#             return 
#         except NoSuchElementException:
#             pass

#         try:
#             follow_button = driver.find_element(By.ID, 'follow_af')
#             follow_button.click()
#             time.sleep(3) 
#             return 
#         except NoSuchElementException:
#             raise NoSuchElementException("Neither follow nor unfollow button found")


#Test 4: Send Skill request.
# from django.test import LiveServerTestCase
# from selenium import webdriver
# import time
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# class SkillRequestTest(LiveServerTestCase):

#     def test_send_skill_request(self):
#         driver = webdriver.Firefox()

#         try:
#             self.login_and_navigate_to_home(driver)
#             self.navigate_to_user_list_page(driver)
#             self.select_user(driver)
#             self.send_skill_request(driver)

#         finally:
#             driver.quit()

#     def login_and_navigate_to_home(self, driver):
#         # Login with credentials
#         driver.get('http://127.0.0.1:8000/login/')
#         username_input = driver.find_element(By.NAME, 'username')
#         password_input = driver.find_element(By.NAME, 'password')
#         login_button = driver.find_element(By.NAME, 'submit')
#         username_input.send_keys('testuser1')
#         password_input.send_keys('Tes123@')
#         login_button.click()

#         # Wait for redirection to home page
#         WebDriverWait(driver, 10).until(EC.url_contains('/home/'))

#     def navigate_to_user_list_page(self, driver):
#         # Navigate to user list page
#         teach_action_container = driver.find_element(By.ID, 'teach')
#         teach_action_container.click()
#         WebDriverWait(driver, 10).until(EC.url_contains('/learn/'))

#     def select_user(self, driver):
#         # Select a user from the list
#         user_links = driver.find_elements(By.XPATH, '//a[@id="users_name"]')
#         user_links[0].click()
#         WebDriverWait(driver, 10).until(EC.url_contains('/profile/'))
#         time.sleep(1)

#     def send_skill_request(self, driver):
#         # Click the send request button
#         send_request_button = driver.find_element(By.ID, 'send_request')
#         send_request_button.click()
#         time.sleep(1)


#Test 5: Admin controls
from django.test import LiveServerTestCase
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AdminPanelTest(LiveServerTestCase):
    def test_block_unblock_user(self):
        # Initialize WebDriver
        driver = webdriver.Firefox()

        try:
            # Login as admin
            self.login(driver)

            # # Assert presence of "Admin Dashboard" on the page
            # assert "Admin Dashboard" in driver.page_source

            # Click deactivate button if user is active
            self.click_deactivate_button(driver)

            # Click activate button to bring user to active state
            self.click_activate_button(driver)

            # Wait for user to be activated
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "deactivate")))

        finally:
            # Close the WebDriver instance
            driver.quit()

    def login(self, driver):
        driver.get('http://127.0.0.1:8000/login/')
        username_input = driver.find_element(By.NAME, 'username')
        password_input = driver.find_element(By.NAME, 'password')
        login_button = driver.find_element(By.NAME, 'submit')
        username_input.send_keys('jeejay')
        password_input.send_keys('jee123')
        login_button.click()

        # Wait for redirection to admin page
        WebDriverWait(driver, 10).until(EC.url_contains('/admin_index/'))

    def click_deactivate_button(self, driver):
        # Click deactivate button if user is active
        try:
            deactivate_button = driver.find_element(By.ID, 'deactivate')
            deactivate_button.click()
            time.sleep(1)
        except NoSuchElementException:
            pass

    def click_activate_button(self, driver):
        # Click activate button to bring user to active state
        try:
            activate_button = driver.find_element(By.ID, 'activate')
            activate_button.click()
            time.sleep(1)
        except NoSuchElementException:
            pass

