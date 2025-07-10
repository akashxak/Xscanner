#!/usr/bin/env python3

import scanner
from requests import session


url = "http://target_url/"
data= {"username":"admin", "password":"password", "Login":"submit"}
linkstoignore=["http://target_url/logout.php"]
scanner = scanner.Scanner(url,linkstoignore)
scanner.session.post("http://target_url/login.php", data=data)


scanner.crawl(url)
print("******compelete links list on given url***********")
for i in scanner.links:
    print(i)

scanner.run_scanner()