import os
from batch_methods import BatchMethods
from file_reader_writer import StrGenFileWriter
import time
from trieste_account_methods import TriesteAccountMethods
from link_leads_scraper import LinkLeadScraper
from pick import pick

all_functions = ["Create Special Google Batches",
                 "Create Batches",
                 "Compile Link Leads to HTML file for review",
                 "Dedupe & Rerun Filters",
                 "Edit Trieste Account",
                 "Add New Bing String Gen Template",
                 "Set all Discard Previously Discovered tickbox to OFF",
                 "Set all Discard Previously Discovered tickbox to ON",
                 "Set all Discard Previously Discovered tickbox to Default"]


def create_batches():
    selected_project = input("client name: ")

    batch_maker = BatchMethods()
    batch_maker.selected_project = selected_project
    all_projects = batch_maker.scrape_projects()
    counter = 0
    keywords = []

    create_batch_url = batch_maker.select_project(all_projects=all_projects)

    print(create_batch_url)

    file_reader.read_templates_from_file()

    try:
        project_type_input = int(input("number: "))
    except ValueError:
        print("input error (ValueError)")
    else:
        user_keywords_input = input("Paste keywords here (1 keyword(s) per line): ")

        # allow user to input keywords, 1 line per keyword
        while user_keywords_input != '':
            keywords.append(user_keywords_input)
            user_keywords_input = input()

    for keyword in keywords:
        generated_strings = file_reader.add_bing_strings(keyword=keyword, user_choice=project_type_input)

        batch_maker.create_batches(
            create_batch_url=create_batch_url,
            keyword_strings=generated_strings,
            kagebunshin=kagebunshin_status,
            batch_keyword=keyword
        )
        time.sleep(0.5)
        counter += 1
    batch_maker.project_scraper_driver.close()
    print(f"{counter} batches for {batch_maker.selected_project} created successfully.")


def dedup_rerun():

    batch_links = []
    counter = 0
    user_keywords_input = input("Paste batch links here (1 batch link(s) per line): ")
    while user_keywords_input != '':
        batch_links.append(user_keywords_input)
        user_keywords_input = input()

    batch_maker = BatchMethods()
    for link in batch_links:
        batch_maker.dedupe_rerun(link)
        counter += 1

    batch_maker.project_scraper_driver.close()
    print(f"{counter} batches successfully deduped and filters rerun")


def create_special_batch(is_bing):

    file_reader.read_special_batch_config_files()
    batch_template_user_choice = int(input("Enter batch template index: "))

    keywords = []
    batch_template_dir = file_reader.files_dict[file_reader.special_batch_config_list[batch_template_user_choice]]
    batch_name = file_reader.special_batch_config_list[batch_template_user_choice].split('.')[0]

    file_reader.read_templates_from_file(is_bing=is_bing)

    user_keygen_template_choice = int(input("Enter keyword template index: "))

    if is_bing:
        string_gen_template_dir = file_reader.files_dict[file_reader.bing_string_gen_template_list[user_keygen_template_choice]]
    elif not is_bing:
        string_gen_template_dir = file_reader.files_dict[file_reader.google_string_gen_template_list[user_keygen_template_choice]]

    user_keywords_input = input("Paste keywords here (1 keyword(s) per line): ")

    # allow user to input keywords, 1 line per keyword
    while user_keywords_input != '':
        keywords.append(user_keywords_input)
        user_keywords_input = input()

    batch_maker = BatchMethods()

    for keyword in keywords:
        batch_maker.create_special_batches(json_dir=batch_template_dir,
                                           batch_keyword=keyword,
                                           batch_name=batch_name,
                                           string_gen_dir=string_gen_template_dir,
                                           is_bing=is_bing
                                           )



trieste_account_checker = TriesteAccountMethods()

# initiate script, check username, password, and ld name in environ variables
if trieste_account_checker.check_environ():

    file_reader = StrGenFileWriter()
    kagebunshin_status = file_reader.check_kagebunshin()

    # function selector.

    main_screen_question = f"Welcome, {os.environ.get('TRIESTE_USERNAME')}! \n" \
                           f"Discard previously discovered site links tickbox: {kagebunshin_status} \n\n" \
                           f"What would you like to do?"
    selected_function, index = pick(all_functions, main_screen_question, multiselect=False, indicator="-->")



    if selected_function in all_functions:
        if selected_function == "Dedupe & Rerun Filters": dedup_rerun()
        if selected_function == "Create Batches":
            StrGenFileWriter()
            create_batches()
        if selected_function == "Edit Trieste Account":
            trieste_account_checker.add_edit_account()
        if selected_function == "Add New Bing String Gen Template":
            file_reader.add_string_gen_template()
        if selected_function == "Set all Discard Previously Discovered tickbox to OFF":
            file_reader.set_kagebunshin(new_setting="off")
        if selected_function == "Set all Discard Previously Discovered tickbox to ON":
            file_reader.set_kagebunshin(new_setting="on")
        if selected_function == "Set all Discard Previously Discovered tickbox to DEFAULT":
            file_reader.set_kagebunshin(new_setting="default")
        if selected_function == "Compile Link Leads to HTML file for review":
            LinkLeadScraper()
        if selected_function == "Create Special Google Batches":
            create_special_batch(is_bing=False)
        if selected_function == "Create Special Bing Batches":
            create_special_batch(is_bing=True)


    else:
        print("Function do not exist")
        input("Press enter key to exit")

else:
    trieste_account_checker.add_edit_account()