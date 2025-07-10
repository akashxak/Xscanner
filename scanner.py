import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from requests import Session

class Scanner:
    def __init__(self, linkstoignore = []):
        self.session = Session()
        self.links=[]
        self.linkstoignore = linkstoignore

    def webrequest(self, url):
        print("Checking:" + url)
        try:
            response = self.session.get(url, timeout=4)
            print(response.status_code)
            if response.status_code == 200:
                return response.content
            else:
                return b'dummy'           
        except Exception:
            pass
    
    def filtering(self, content):
        if isinstance(content, bytes):
            content_str = content.decode('utf-8', errors= "ignore")
        else:
            content_str = content
        self.output = re.findall(r'href=[\'"]?([^\'" >]+)', content_str)
        return self.output


    def crawl(self, url):
        response = self.webrequest(url)
        output = self.filtering(response)
        for i in output:
            i = urljoin(url, i)
            if i not in self.links and url in i and all(ignore not in i for ignore in self.linkstoignore) and ".png" not in i and ".css" not in i:
                self.links.append(i)
                self.crawl(i)

    def extract_forms(self, url):
        content = self.webrequest(url)
        parsed_html = BeautifulSoup(content, features="lxml")
        return parsed_html.find_all("form")
    
    def submit_forms(self, url, value, form):
        action = form.get("action")
        parsed_action = urljoin(url, action)
        method = form.get("method")
            
        print("*****Action field******")
        print(parsed_action)
        print(method)

        inp_element = form.find_all("input")
        print("*****Input box name******")
        postdata_dict= {}

        for content in inp_element:
            input_name = content.get("name")
            print(input_name)
            input_type = content.get("type")
            print(input_type)
            input_value = content.get("value")
            if input_type == "text":
                input_value = value
            else :
                input_value = content.get("value", "")
                
            postdata_dict[input_name] = input_value
            print(postdata_dict)
            if method == "post":
                response = self.session.post(parsed_action, data = postdata_dict)
                
            else : response = self.session.get(parsed_action, params = postdata_dict)

            response = response.content
            response = response.decode()
            return response
       
            
            
    def run_scanner(self):
        for link in self.links:
            forms = self.extract_forms(link)
            for form in forms:
                print("Testing form in: "+ link)
                response = self.xss_vuln_in_form(form, link)
                print(response)
                if response:
                    print("\n[+] xss vulnerability in the "+link+ " found\n")
                    print(form)

                if "=" in link:
                    print("[+]Testing :" + link)
                    response = self.xss_vuln_in_link(link)
                    if response:
                        print("\n[+] xss vulnerability in the "+link+ " found\n")


    def xss_vuln_in_link(self, url):
        script = "<sCript>alert('XSS')</scriPt>"
        url = url.replace("=", "="+ script)
        response = self.session.get(url)
        return script.encode() in response.content


    def xss_vuln_in_form(self, form, url):
        script = "<sCript>alert('XSS')</scriPt>"
        response = self.submit_forms(url,script, form)
        print("test")
        if response is None:
            return False
        else : return script in response