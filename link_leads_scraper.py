import selenium.common.exceptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import os


class LinkLeadScraper:

    def __init__(self):
        batch_urls = []

        batch_url_user_input = input("Paste batch links here (1 batch link(s) per line): ")
        while batch_url_user_input != '':
            batch_urls.append(batch_url_user_input)
            batch_url_user_input = input()

        try:
            service = ChromeService(executable_path=ChromeDriverManager().install())
        except ValueError:
            service = ChromeService(executable_path=ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service)
        driver.get("http://trieste.io")
        driver.implicitly_wait(3)
        wait = WebDriverWait(driver, 10)
        max_pages = 100

        # Login to Trieste
        trieste_username = driver.find_element(By.ID, "user_email")
        trieste_password = driver.find_element(By.ID, "user_password")
        login_submit_button = driver.find_element(By.NAME, "commit")

        trieste_username.send_keys(os.environ.get("TRIESTE_USERNAME"))
        trieste_password.send_keys(os.environ.get("TRIESTE_PASSWORD"))
        login_submit_button.click()
        ##################################

        if not batch_urls:
        # Access batches page, select Linkdev name,  and select all that is completed
            batches_link = driver.find_element(By.XPATH, '//*[@id="MainTabs"]/li[2]/a')
            batches_link.click()

            batch_owner_selector = Select(driver.find_element(By.NAME, "batch_user_id"))
            batch_owner_selector.select_by_visible_text(os.environ.get("LINKDEV_NAME"))

            batch_status_selector = Select(driver.find_element(By.XPATH, '//*[@id="status"]'))
            batch_status_selector.select_by_visible_text("Completed")
            driver.get('http://trieste.io/company/14/link_leads_batches/list?page=1')
            #########################################################
            sleep(0.1)

            # Scrape batches that have period before batch name ex: .LHH
            batches_links = []
            batch_projects = []
            batches_for_scraping_list = []
            while True:
                batches_links_on_page = driver.find_elements(By.XPATH, '//*[@id="listSites"]/tbody/tr/td[1]/a')
                batch_projects_on_page = driver.find_elements(By.XPATH, '//*[@id="listSites"]/tbody/tr/td[4]')

                for url in batches_links_on_page:
                    batches_links.append(url.get_attribute('href'))

                for project in batch_projects_on_page:
                    batch_projects.append(project.text)

                # Find the 'Next' button and check if it exists or is disabled, break out of loop if so
                try:
                    next_button = driver.find_element(By.XPATH, '//a[@class="next_page"]')
                except selenium.common.exceptions.NoSuchElementException:
                    break


            # Click the 'Next' button to go to the next page
                next_button.click()

            batches_dict = {batches_links[i]: batch_projects[i] for i in range(0, len(batch_projects))}


            for key, value in batches_dict.items():
                if value[0] == '.':
                    batches_for_scraping_list.append(key)
        else:

            batches_for_scraping_list = [url for url in batch_urls]



        with open("for_farming1.html", "w", encoding="utf-8") as file_write:
            for batch_url in batches_for_scraping_list:
                driver.get(batch_url)

                status_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="status"]'))
                status_dropdown.select_by_visible_text("Not Reviewed")

                # Batch pagination
                pagination = driver.find_elements(By.CSS_SELECTOR, ".pagination a")
                pages_list = []
                if len(batch_urls) > 0:
                    file_write.write(f"<p>{batch_url}</p>")
                else:
                    file_write.write(f"<p>{batch_url} - {batches_dict[batch_url]}</p>")

                if len(pagination) > 0:
                    pages_list = [f"{batch_url}?page={n}" for n in range(1, int(pagination[-2].text) + 1)]
                else:
                    pages_list.append(batch_url)

                for url in pages_list:
                    driver.get(url)
                    link_leads_urls = driver.find_elements(By.XPATH, '//*[@id="listSites"]/tbody/tr/td[1]/a[1]')

                    for a in link_leads_urls:
                        file_write.write(f'<a href="{a.get_attribute("href")}">{a.get_attribute("href")}</a>\n')

                sleep(0.1)

        driver.quit()