import os
import time
import json
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BatchMethods:

    def __init__(self):
        try:
            self.service = ChromeService(executable_path=ChromeDriverManager().install())
        except ValueError:
            self.service = ChromeService(executable_path=ChromeDriverManager(driver_version='114.0.5735.90').install())
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.project_scraper_driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.project_scraper_driver.implicitly_wait(10)
        self.selected_project = ""
        self.login_to_trieste()
        self.wait = WebDriverWait(self.project_scraper_driver, 15)

    def scrape_projects(self):
        all_projects = self.project_scraper_driver.find_elements(By.XPATH, '//*[@id="listSites"]/tbody/tr/td[1]')
        all_create_batch_links = self.project_scraper_driver.find_elements(By.XPATH, '//*[@id="listSites"]/tbody/tr/td[3]/a[1]')

        project_list = [project.text.split(".")[0] for project in all_projects]
        create_batch_link_list = [link.get_attribute("href") for link in all_create_batch_links]

        project_dict = {project_list[i]: create_batch_link_list[i] for i in range(0, len(project_list))}
        return project_dict

    def login_to_trieste(self):
        print("Logging in to Trieste...")
        self.project_scraper_driver.get("http://trieste.io")
        trieste_username = self.project_scraper_driver.find_element(By.ID, "user_email")
        trieste_password = self.project_scraper_driver.find_element(By.ID, "user_password")
        login_submit_button = self.project_scraper_driver.find_element(By.NAME, "commit")

        trieste_username.send_keys(os.environ.get("TRIESTE_USERNAME"))
        trieste_password.send_keys(os.environ.get("TRIESTE_PASSWORD"))
        login_submit_button.click()
        time.sleep(2)

        if self.project_scraper_driver.current_url == "http://trieste.io/companies/dashboard/14":
            print("Log in successful..")

    def create_batches(self, create_batch_url, kagebunshin, keyword_strings, batch_keyword):
        while len(keyword_strings) > 0:
            self.project_scraper_driver.get(create_batch_url)

            batch_name_textbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="link_leads_batch_description"]')
            legal_kagebunshin_tickbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="link_leads_batch_discard_company_site_links"]')
            web_search_query_radio_button = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="batch_type_google_simple_query_v2"]')
            web_search_query_radio_button.click()
            keywords_textbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="google_google_simple_query"]')
            create_button = self.project_scraper_driver.find_element(By.NAME, "commit")

            # set "discard previously discovered site links in company" tickbox based on setting
            if kagebunshin == "off":
                if legal_kagebunshin_tickbox.is_selected():
                    legal_kagebunshin_tickbox.click()
            if kagebunshin == "on":
                if not legal_kagebunshin_tickbox.is_selected():
                    legal_kagebunshin_tickbox.click()

            batch_name_textbox.send_keys(f".{self.selected_project} - {batch_keyword}")

            for string in keyword_strings[:10]:
                keywords_textbox.send_keys(f"{string}")

            keywords_textbox.send_keys(f"{Keys.TAB}10")

            create_button.click()
            print(f"{self.selected_project} batch created using keyword(s) '{batch_keyword}'")

            del keyword_strings[:10]

    def select_project(self, all_projects):

        if self.selected_project in all_projects:
            return all_projects[self.selected_project]
        else:
            input("No such project. Press enter to continue.")
            exit()

    def dedupe_rerun(self, batch_url):
        self.project_scraper_driver.get(batch_url)
        batch_number = batch_url.split("/")[-1]
        self.project_scraper_driver.get(f"http://trieste.io/link_leads_batches/dedupe_domains_link_leads/{batch_number}")
        time.sleep(0.2)
        self.project_scraper_driver.get(f"http://trieste.io/link_leads_batches/rerun_batch_filters/{batch_number}")
        time.sleep(0.2)
        print(f"{batch_url} has been deduped, and filters has been rerun")

    def create_special_batches(self, json_dir, batch_keyword, batch_name, string_gen_dir, is_bing):


        with open(json_dir, mode="r", encoding="UTF-8") as batch_config_file:
            batch_config = json.load(batch_config_file)

        with open(string_gen_dir, mode="r", encoding="UTF-8") as string_gen_file:
            keyword_strings = string_gen_file.read().splitlines()

        if is_bing:

            current_date = datetime.now().strftime('%m/%d/%Y')

            self.project_scraper_driver.get(batch_config["batch_url"])

            batch_name_textbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="link_leads_batch_description"]')
            legal_kagebunshin_tickbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="link_leads_batch_discard_company_site_links"]')
            min_trust_flow_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_tf')
            min_refdomains_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_rd')
            min_semrush_keyword_volume_score_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_volume_score')
            min_semrush_organic_score_us_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_traffic_score')
            min_semrush_organic_score_uk_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_traffic_score_uk')
            min_semrush_organic_score_global_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_traffic_score_global')
            min_ahrefs_domain_rating_score = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_ahrefs_domain_rating')
            min_ahrefs_global_traffic_score = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_ahrefs_traffic_score_global')
            min_host_trust_flow = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_host_tf')
            create_button = self.wait.until(EC.element_to_be_clickable((By.NAME, "commit")))
            bing_query_radio_button = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="batch_type_bing_search_api"]')
            bing_keyword_textbox = self.project_scraper_driver.find_element(By.ID, 'bing_search_api_google_simple_query')

            # set "discard previously discovered site links in company" tickbox based on setting
            if batch_config['discard_previously_discovered'] == "on":
                if legal_kagebunshin_tickbox.is_selected():
                    legal_kagebunshin_tickbox.click()
            elif batch_config['discard_previously_discovered'] == "off":
                if not legal_kagebunshin_tickbox.is_selected():
                    legal_kagebunshin_tickbox.click()

            if 'min_trust_flow' in batch_config:
                if not batch_config['min_trust_flow'] == "default":
                    min_trust_flow_textbox.clear()
                    min_trust_flow_textbox.send_keys(batch_config['min_trust_flow'])

            if 'min_refdomains' in batch_config:
                if not batch_config['min_refdomains'] == "default" or 'min_trust_flow' in batch_config.values():
                    min_refdomains_textbox.clear()
                    min_refdomains_textbox.send_keys(batch_config['min_refdomains'])

            if 'min_semrush_keyword_vol' in batch_config:
                if not batch_config['min_semrush_keyword_vol'] == "default":
                    min_semrush_keyword_volume_score_textbox.clear()
                    min_semrush_keyword_volume_score_textbox.send_keys(batch_config['min_semrush_keyword_vol'])

            if 'min_semrush_organic_traffic_US' in batch_config:
                if not batch_config['min_semrush_organic_traffic_US'] == "default":
                    min_semrush_organic_score_us_textbox.clear()
                    min_semrush_organic_score_us_textbox.send_keys(batch_config['min_semrush_organic_traffic_US'])

            if 'min_semrush_organic_traffic_UK' in batch_config:
                if not batch_config['min_semrush_organic_traffic_UK'] == "default":
                    min_semrush_organic_score_uk_textbox.clear()
                    min_semrush_organic_score_uk_textbox.send_keys(batch_config['min_semrush_organic_traffic_UK'])

            if 'min_semrush_organic_traffic_Global' in batch_config:
                if not batch_config['min_semrush_organic_traffic_Global'] == "default":
                    min_semrush_organic_score_global_textbox.clear()
                    min_semrush_organic_score_global_textbox.send_keys(
                        batch_config['min_semrush_organic_traffic_Global'])

            if "min_ahrefs_domain_rating_score" in batch_config:
                if not batch_config["min_ahrefs_domain_rating_score"] == 'default':
                    min_ahrefs_domain_rating_score.clear()
                    min_ahrefs_domain_rating_score.send_keys(batch_config["min_ahrefs_domain_rating_score"])

            if "min_ahrefs_global_traffic_score" in batch_config:
                if not batch_config["min_ahrefs_global_traffic_score"] == 'default':
                    min_ahrefs_global_traffic_score.clear()
                    min_ahrefs_global_traffic_score.send_keys(batch_config["min_ahrefs_global_traffic_score"])

            if "min_host_trust_flow" in batch_config:
                if not batch_config["min_host_trust_flow"] == 'default':
                    min_host_trust_flow.clear()
                    min_host_trust_flow.send_keys(batch_config["min_host_trust_flow"])

            bing_query_radio_button.click()

            batch_name_textbox.send_keys(f".{batch_name} - {batch_keyword} {current_date}")

            for string in keyword_strings:
                bing_keyword_textbox.send_keys(f"{string.replace('<<keyword>>', batch_keyword)}\n")

            bing_keyword_textbox.send_keys(f"{Keys.TAB}10")
            create_button.click()
            print(f"{batch_name} batch created using keyword(s) '{batch_keyword}'")


        elif not is_bing:

            current_date = datetime.now().strftime('%m/%d/%Y')

            self.project_scraper_driver.get(batch_config["batch_url"])

            batch_name_textbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="link_leads_batch_description"]')
            legal_kagebunshin_tickbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="link_leads_batch_discard_company_site_links"]')
            min_trust_flow_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_tf')
            min_refdomains_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_rd')
            min_semrush_keyword_volume_score_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_volume_score')
            min_semrush_organic_score_us_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_traffic_score')
            min_semrush_organic_score_uk_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_traffic_score_uk')
            min_semrush_organic_score_global_textbox = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_semrush_traffic_score_global')
            web_search_query_radio_button = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="batch_type_google_simple_query_v2"]')
            min_ahrefs_domain_rating_score = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_ahrefs_domain_rating')
            min_ahrefs_global_traffic_score = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_ahrefs_traffic_score_global')
            min_host_trust_flow = self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_filter_host_tf')
            keywords_textbox = self.project_scraper_driver.find_element(By.XPATH, '//*[@id="google_google_simple_query"]')
            create_button = self.wait.until(EC.element_to_be_clickable((By.NAME, "commit")))

            # set "discard previously discovered site links in company" tickbox based on setting
            if batch_config['discard_previously_discovered'] == "on":
                if legal_kagebunshin_tickbox.is_selected():
                    legal_kagebunshin_tickbox.click()
            elif batch_config['discard_previously_discovered'] == "off":
                if not legal_kagebunshin_tickbox.is_selected():
                    legal_kagebunshin_tickbox.click()

            if 'min_trust_flow' in batch_config:
                if not batch_config['min_trust_flow'] == "default":
                    min_trust_flow_textbox.clear()
                    min_trust_flow_textbox.send_keys(batch_config['min_trust_flow'])

            if 'min_refdomains' in batch_config:
                if not batch_config['min_refdomains'] == "default" or 'min_trust_flow' in batch_config.values():
                    min_refdomains_textbox.clear()
                    min_refdomains_textbox.send_keys(batch_config['min_refdomains'])

            if 'min_semrush_keyword_vol' in batch_config:
                if not batch_config['min_semrush_keyword_vol'] == "default":
                    min_semrush_keyword_volume_score_textbox.clear()
                    min_semrush_keyword_volume_score_textbox.send_keys(batch_config['min_semrush_keyword_vol'])

            if 'min_semrush_organic_traffic_US' in batch_config:
                if not batch_config['min_semrush_organic_traffic_US'] == "default":
                    min_semrush_organic_score_us_textbox.clear()
                    min_semrush_organic_score_us_textbox.send_keys(batch_config['min_semrush_organic_traffic_US'])

            if 'min_semrush_organic_traffic_UK' in batch_config:
                if not batch_config['min_semrush_organic_traffic_UK'] == "default":
                    min_semrush_organic_score_uk_textbox.clear()
                    min_semrush_organic_score_uk_textbox.send_keys(batch_config['min_semrush_organic_traffic_UK'])

            if 'min_semrush_organic_traffic_Global' in batch_config:
                if not batch_config['min_semrush_organic_traffic_Global'] == "default":
                    min_semrush_organic_score_global_textbox.clear()
                    min_semrush_organic_score_global_textbox.send_keys(
                        batch_config['min_semrush_organic_traffic_Global'])

            if "min_ahrefs_domain_rating_score" in batch_config:
                if not batch_config["min_ahrefs_domain_rating_score"] == 'default':
                    min_ahrefs_domain_rating_score.clear()
                    min_ahrefs_domain_rating_score.send_keys(batch_config["min_ahrefs_domain_rating_score"])

            if "min_ahrefs_global_traffic_score" in batch_config:
                if not batch_config["min_ahrefs_global_traffic_score"] == 'default':
                    min_ahrefs_global_traffic_score.clear()
                    min_ahrefs_global_traffic_score.send_keys(batch_config["min_ahrefs_global_traffic_score"])

            if "min_host_trust_flow" in batch_config:
                if not batch_config["min_host_trust_flow"] == 'default':
                    min_host_trust_flow.clear()
                    min_host_trust_flow.send_keys(batch_config["min_host_trust_flow"])

            web_search_query_radio_button.click()

            if 'search_engine' in batch_config:
                if not batch_config['search_engine'] == "default":
                    search_engine_select = Select(self.project_scraper_driver.find_element(By.ID, 'link_leads_batch_search_engine_google_simple'))
                    search_engine_select.select_by_visible_text(batch_config['search_engine'])

            batch_name_textbox.send_keys(f".{batch_name} - {batch_keyword} {current_date}")

            for string in keyword_strings:
                keywords_textbox.send_keys(f"{string.replace('<<keyword>>', batch_keyword)}\n")

            keywords_textbox.send_keys(f"{Keys.TAB}10")

            create_button.click()

            print(f"{batch_name} batch created using keyword(s) '{batch_keyword}'")

