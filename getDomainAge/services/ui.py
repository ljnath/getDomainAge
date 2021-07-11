class UIService:
    """
    Class with helper method related to UI
    """

    @staticmethod
    def get_prev_next_page_number(max_page, current_page) -> tuple:
        """ To calculate the previous and next page number for the pagination system, maximum number of page number shown is 3
            :param max_page : max_page as integer is the maximum number of available pages
            :param current_page : current_page as integer is the current page number
            :return previous_page, next_page : previous and next page numbers as integers
        """
        previous_page, next_page = 1, max_page
        if current_page == previous_page:       # if first page is selected, then the previous page number is 1
            previous_page = 1
        elif current_page == max_page:          # if last page is selected, then previous page number is last page - 1 if only 2 pages are there else last page - 3
            previous_page = current_page - 1 if max_page == 2 else 2
        else:
            previous_page = current_page - 1    # previous page is current page - 1 if current page is neither first nor last

        if current_page < max_page - 1:         # if next page is possible, then it is set to previous page + 2
            next_page = previous_page + 2
        else:
            next_page = max_page

        return (previous_page, next_page)
