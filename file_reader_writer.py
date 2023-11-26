import json
import os

class StrGenFileWriter:

    def __init__(self):

        self.files_dict = {}

        self.bing_string_gen_template_dir = "string_gen_templates_bing"
        self.bing_string_gen_template_list = os.listdir(self.bing_string_gen_template_dir)

        self.google_string_gen_template_dir = "string_gen_templates_google"
        self.google_string_gen_template_list = os.listdir(self.google_string_gen_template_dir)


        self.special_batch_config_dir = "special_batch_configs"
        self.special_batch_config_list = os.listdir(self.special_batch_config_dir)

        kagebunshin_dict = {}

    def add_bing_strings(self, user_choice, keyword):
        file_path = self.files_dict[self.google_string_gen_template_list[user_choice]]
        print(file_path)
        with open(file_path) as bing_strings:
            string_gen_lines = bing_strings.readlines()

        output = [f"{keyword} {single_string}" for single_string in string_gen_lines]

        return output

    def add_string_gen_template(self):
        string_gen_list = []
        new_template_filename = input("Template name: ")

        string_gen_input = input("Paste strings here:\n")

        while string_gen_input != '':
            string_gen_list.append(string_gen_input)
            string_gen_input = input()

        with open(file=f"string_gen_templates_google/{new_template_filename}.txt", mode="w", encoding="utf-8") as template_writer:
            for single_string in string_gen_list:
                template_writer.writelines(f"{single_string}\n")

        q = input("Would you like to add more?(y/n)\n")
        if q == "y" or "Y": self.add_string_gen_template()

    def read_templates_from_file(self, is_bing):
        # check string_gen_templates_google folder, list all files with .txt extension
        if is_bing:
            string_gen_template_list = self.bing_string_gen_template_list
            string_gen_template_dir = self.bing_string_gen_template_dir
        elif not is_bing:
            string_gen_template_list = self.google_string_gen_template_list
            string_gen_template_dir = self.google_string_gen_template_dir

        for filename in string_gen_template_list:
            if filename.endswith(".txt"):
                path = os.path.join(string_gen_template_dir, filename)
                self.files_dict[filename] = path

        for project in string_gen_template_list:
            print(f"{string_gen_template_list.index(project)} = {os.path.splitext(project)[0]}")

    def set_kagebunshin(self, new_setting):

        with open("files/config.json", "r") as json_file:
            config_data = json.load(json_file)

        config_data["kagebunshin"] = new_setting

        with open("files/config.json", "w") as json_file:
            json.dump(config_data, json_file)

    def check_kagebunshin(self):

        with open("files/config.json", "r") as json_file:
            config_data = json.load(json_file)

        return config_data["kagebunshin"]

    def read_special_batch_config_files(self):
        for filename in self.special_batch_config_list:
            if filename.endswith(".json"):
                path = os.path.join(self.special_batch_config_dir, filename)
                self.files_dict[filename] = path

        for project in self.special_batch_config_list:
            print(f"{self.special_batch_config_list.index(project)} = {project.split('.')[0]}")

        # print(self.files_dict[self.special_batch_config_list[5]])

