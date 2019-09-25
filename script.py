import platform
import sys
from io import StringIO

import eel

from stratification import (
    get_selection_number_range,
    init_categories_people,
    read_in_cats,
    run_stratification,
    write_selected_people_to_file,
    initialise_settings
)


class FileContents():

    def __init__(self):
        self.category_raw_content = ''
        self.selection_raw_content = ''
        self.categories = None
        self.columns_data = None
        self.people = None
        self.number_people_to_select = 0
        # mins and maxs (from category data) for number of people one can select
        self.min_max_people = {}
        self.id_column, self.columns_to_keep, self.check_same_address, self.check_same_address_columns, self.max_attempts = initialise_settings()

    def add_category_content(self, file_contents):
        csv_files.category_raw_content = file_contents
        category_file = StringIO(file_contents)
        try:
            self.categories, self.min_max_people = read_in_cats(category_file)
        except Exception as error:
            # TODO: put error in the GUI box
            print("Error reading in categories: {}".format(error))
        eel.update_categories_output_area("Number of categories: {}".format(len(self.categories.keys())))
        self.update_selection_content()
        min_selection, max_selection = get_selection_number_range(self.min_max_people)
        eel.update_selection_range(min_selection, max_selection)
        self.update_run_button()

    def add_selection_content(self, file_contents):
        csv_files.selection_raw_content = file_contents
        people_file = StringIO(file_contents)
        try:
            self.people, self.columns_data, msg_list = init_categories_people(people_file, self.id_column, self.categories, self.columns_to_keep)
            msg = " ".join(msg_list)
        except Exception as error:
            msg = "Number of people: {}".format(error)
        eel.update_selection_output_area(msg)
        self.update_run_button()

    def update_selection_content(self):
        if self.category_raw_content:
            eel.enable_selection_content()

    def update_run_button(self):
        if self.category_raw_content and self.selection_raw_content and self.number_people_to_select > 0:
            eel.enable_run_button()

    def update_number_people(self, number_people):
        if number_people == '':
            self.number_people_to_select = 0
        else:
            self.number_people_to_select = int(number_people)
        self.update_run_button()

    def run_selection(self):
        success, tries, people_selected, output_lines = run_stratification(
            self.categories, self.people, self.columns_data, self.number_people_to_select,
            self.min_max_people, self.max_attempts, self.check_same_address,
            self.check_same_address_columns
        )
        if success:
            selectfile = StringIO()
            remainfile = StringIO()
            output_lines += write_selected_people_to_file(self.people, people_selected, self.id_column, self.categories, self.columns_to_keep, self.columns_data, self.check_same_address, self.check_same_address_columns, selectfile, remainfile)
            eel.enable_selected_download(selectfile.getvalue(), 'selected.csv')
            eel.enable_remaining_download(remainfile.getvalue(), 'remaining.csv')
        # print output_lines to the App:
        eel.update_selection_output_messages_area("<br />".join(output_lines))


# global to hold contents uploaded from JS
csv_files = FileContents()


@eel.expose
def handle_category_contents(file_contents):
    csv_files.add_category_content(file_contents)


@eel.expose
def handle_selection_contents(file_contents):
    csv_files.add_selection_content(file_contents)


@eel.expose
def update_number_people(number_people):
    csv_files.update_number_people(number_people)


@eel.expose
def run_selection():
    csv_files.run_selection()


def main():
    default_size = (800, 800)
    eel.init('web')  # Give folder containing web files
    try:
        eel.start('main.html', size=default_size)
    except EnvironmentError:
        # on Windows 10 try Edge if Chrome not available
        if sys.platform in ('win32', 'win64') and int(platform.release()) >= 10:
            eel.start('main.html', mode='edge', size=default_size)
        else:
            raise


if __name__ == '__main__':
    main()
