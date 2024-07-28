import requests, json
from collections import OrderedDict
from bs4 import BeautifulSoup

header_default = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"}


def fetch_soup(victim_url, headers):
    response = requests.get(victim_url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

def parse_table_data(soup, title):
    try:
        report_body = soup.find("div", class_="reportTitle", text=title).find_next_sibling("div")
        report_th = (x.text for x in report_body.select("table tbody tr th"))
        report_td = (x.text for x in report_body.select("table tbody tr td"))
        return zip(report_th, report_td)
    except AttributeError:
        return []

def extract_data(soup):
    data = {}
    data["ip"] = soup.find("th", class_="tableLabel", text="IP Address:").find_next_sibling("td").text.strip()
    data["site"] = soup.find("th", class_="tableLabel", text="Site:").find_next_sibling("td").text.strip()
    data["score"] = soup.find("div", class_="score").text.strip()
    return data

def parse_headers(soup):
    headers = OrderedDict()
    # Parse Raw Headers Report Table
    headers.update({header: {"rating": "info", "value": value} for header, value in parse_table_data(soup, "Raw Headers")})

    # Parse ratings from badges
    raw_headers = soup.find("th", class_="tableLabel", text="Headers:").find_next_sibling("td").find_all("li")
    for raw_header in raw_headers:
        headers.setdefault(raw_header.text, {})["rating"] = "good" if "pill-green" in raw_header["class"] else "bad"

    # Parse Missing Headers Report Table
    headers.update({header: {"description": value} for header, value in parse_table_data(soup, "Missing Headers")})

    # Parse Additional Information Report Table
    headers.update({header: {"description": value} for header, value in parse_table_data(soup, "Additional Information")})

    return headers

def requests_analyze_headers(victim):
    api_url = f"https://securityheaders.io/?q={victim}"
    soup = fetch_soup(api_url, header_default)
    if "Sorry about that..." in soup.find_all("div", "12u")[0].text.strip():
        api_url = f"https://securityheaders.io/?q=https://{victim}"
        soup = fetch_soup(api_url, header_default)

    data = extract_data(soup)
    data["headers"] = parse_headers(soup)
    return data

def analyze_headers(victim):
    data = requests_analyze_headers(victim)
    print(json.dumps(data, indent=4, sort_keys=True))

analyze_headers("example.org")