import requests, time, json
from collections import OrderedDict
from bs4 import BeautifulSoup

header_default = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"}

def scanssl(victim):
    ssl_file = f"ssl_{victim}.json"
    url = f'https://api.ssllabs.com/api/v3/analyze?host={victim}&ignoreMismatch=on&all=done'
    print(f"\n Request {url}")
    
    while True:
        response = requests.get(url, headers=header_default)
        j = response.json()
        status = j.get('status')
        
        if status == 'READY':
            print('Analyze is ready\n')
            break
        elif status == 'ERROR':
            print(f"host {victim}, status {j['statusMessage']}, Message from API {url}")
            return
        else:
            print('Analyze waiting for reports to be finished\n')
            time.sleep(15)

    with open(ssl_file, 'w') as outfile:
        json.dump(j, outfile, indent=4)
        print(f'writing to file {ssl_file} created by sslabs')

    # Initialize data structure with default values
    data = {
        'hostname': victim,
        'serverName': victim,
        'grade': '',
        'hasWarnings': '',
        'isExceptional': '',
        'heartbleed': '',
        'vulnBeast': '',
        'poodle': '',
        'freak': '',
        'logjam': '',
        'supportsRc4': '',
        'TLS': []
    }

    # Get first endpoint and its details
    if not j.get('endpoints'):
        return data
        
    endpoint = j['endpoints'][0]
    details = endpoint.get('details', {})

    # Update data with endpoint info
    data.update({
        'grade': endpoint.get('grade', ''),
        'serverName': endpoint.get('serverName', victim),
        'hasWarnings': endpoint.get('hasWarnings', ''),
        'isExceptional': endpoint.get('isExceptional', ''),
        'heartbleed': details.get('heartbleed', ''),
        'vulnBeast': details.get('vulnBeast', ''),
        'poodle': details.get('poodle', ''),
        'freak': details.get('freak', ''),
        'logjam': details.get('logjam', ''),
        'supportsRc4': details.get('supportsRc4', ''),
        'TLS': [p['version'] for p in details.get('protocols', [])]
    })

    return data


def requests_analyze_TLS(victim):
    data = {}
    base_url = "https://tls.imirhil.fr/https/"
    domains = [victim, f"www.{victim}"]

    for domain in domains:
        api_url = f"{base_url}{domain}"
        print(f"\n Request {api_url}")
        response = requests.get(api_url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        if "TLS seems not supported on this server" not in soup.text:
            # Get score
            data["score"] = soup.find("span", class_="badge").text
            
            # Get TLS versions more efficiently with a single find_all
            data["v_tls"] = [version.text for version in soup.find_all("span", class_=["badge badge-state-default", "badge badge-state-error"])]
            
            # Get table data more efficiently
            if table := soup.find("table", class_="table table-bordered table-condensed table-striped center"):
                rows = table.find_all("tr")
                data["table_data"] = [[cell.text.strip() for cell in row.find_all(["th", "td"])]for row in rows]
            return data
    return data



def analyze_Transport_Layer_Security(victim):
    data_tls_imirhil = requests_analyze_TLS(victim)
    print(json.dumps(data_tls_imirhil, indent=4))
    data_ssllabs = scanssl(victim)
    print(json.dumps(data_ssllabs,indent=4))

if __name__ == "__main__":
    analyze_Transport_Layer_Security("example.com")