from getDomainAge.services.ui import UIService


def test_ui_serivce():
    ui_service = UIService()
    max_page = 100
    for i in range(1, max_page):
        if i == 1:
            assert ui_service.get_prev_next_page_number(max_page, i) == (1, i + 2)
        elif i == max_page:
            assert ui_service.get_prev_next_page_number(max_page, i) == (max_page - 2, max_page)
        else:
            assert ui_service.get_prev_next_page_number(max_page, i) == (i - 1, i + 1)
