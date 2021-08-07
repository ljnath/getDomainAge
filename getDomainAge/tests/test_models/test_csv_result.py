from getDomainAge.models.csv_result import CsvResult


def test_csv_result_with_custom_value():
    csv_result = CsvResult('https://domain.com/index.html', 'domain.com', 99)

    assert csv_result.url == 'https://domain.com/index.html'
    assert csv_result.domain_name == 'domain.com'
    assert csv_result.age == 99


def test_csv_result_with_defaultvalue():
    csv_result = CsvResult('https://domain.com/index.html')

    assert csv_result.url == 'https://domain.com/index.html'
    assert csv_result.domain_name == ''
    assert csv_result.age == 0
