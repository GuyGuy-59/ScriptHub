import requests, hashlib, re, getpass, json

def parsejson(json_obj, p):
    _json = json.loads(json_obj)
    return _json[f"{p}"]

def check_pwned_password():
    print("Request api pwnedpassword.com")
    passwd = getpass.getpass("Your password: ")
    mdp_sha1 = hashlib.sha1(passwd.encode()).hexdigest()
    regex = re.compile(rf"{mdp_sha1[5:].upper()}:\d*")
    url_pwnedpasswords = f"https://api.pwnedpasswords.com/range/{mdp_sha1[0:5]}"
    print(f"Request {url_pwnedpasswords}")
    rqst_pwnedpasswords = requests.get(url_pwnedpasswords)
    if rqst_pwnedpasswords.status_code == 200:
        try:
            found_passwd = re.search(regex, rqst_pwnedpasswords.text)[0]
            print(f"Your password {mdp_sha1} is pwned {found_passwd.split(':')[1]} times")
        except:
            print("No found")

def requests_breachdirectory():
    print("\nRequest api pwnedpassword.com\n More https://breachdirectory.org/")
    info_user = input("username,email or phone: ")
    url_pwned = "https://breachdirectory.p.rapidapi.com/"
    querystring = {"func":"auto","term":info_user}
    headers = {
        "X-RapidAPI-Key": "",
        "X-RapidAPI-Host": "breachdirectory.p.rapidapi.com"
    }
    response = requests.get(url_pwned, headers=headers, params=querystring)
    print(json.dumps(response.json(), indent=4, sort_keys=True))

def request_proxynova():
    print("\nRequest api proxynova")
    info_user = input("username, email, domain: ")
    url = f"https://api.proxynova.com/comb?query={info_user}"
    response = requests.get(url)
    _json = parsejson(response.text, "lines")
    for line in _json:
        print(line)

# Example usage of the functions
check_pwned_password()
requests_breachdirectory()
request_proxynova()
