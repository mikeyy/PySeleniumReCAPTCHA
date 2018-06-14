import time
import random
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from user_agent import generate_user_agent

resp = requests.get("https://proxysource")
proxies = resp.text.split("\n")
print len(proxies),'proxies'

def wait_between(a,b):
    rand=random.uniform(a, b)
    print 'Delaying',rand,'seconds'
    time.sleep(rand)

class Emulate(object):
    def __init__(self):
        self.domain = 'https://www.google.com/recaptcha/api2/demo'
        self.sitekey = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'
        self.page_submit = 'https://fuckonthe.net/return_response.php'
        self.htmlcode = """<html>
<meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'>

<head>
    <script src="https://recaptcha.net/recaptcha/api.js" async></script>
    <title>reCaptcha Solver</title>
    <style type='text/css'>
        body{margin: 1em 5em 0 5em; font-family: sans-serif;}fieldset{display: inline; padding: 1em;}
    </style>
</head>

<body>
    <center>
        <form action='%s' method='post'>
            <fieldset>
                <div class='g-recaptcha' data-sitekey='%s' data-callback='sub'></div>
                <p>
                    <input type='submit' value='Submit' id='submit'>
                </p>
            </fieldset>
        </form>
    </center>
    <script>
        function sub(){document.getElementById('submit').click();}
    </script>
</body>

</html>"""% (self.page_submit, self.sitekey)

    def new_browser(self, proxy=False):
        proxy = random.choice(proxies)

        user_agent = generate_user_agent(navigator='chrome')
        options = Options()
        #options.add_argument('--proxy-server=http://%s'% proxy)
        options.add_argument('--user-agent=%s'% user_agent)
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-bundled-ppapi-flash")
        options.add_argument("--incognito")
        options.add_argument("--disable-plugins-discovery")

        self.chrome = webdriver.Chrome(chrome_options=options)
        self.chrome.delete_all_cookies()

    def solve(self):
            print 'Loading',self.domain
            self.chrome.get(self.domain)
            print 'Injecting code' 
            self.chrome.execute_script('document.write("{}")'.format(self.htmlcode.replace("\n", "")))
            print 'Checking if injected'
            while True:
                if 'reCaptcha Solver' in self.chrome.page_source:
                    break
                time.sleep(1)
            print 'Executing code'
            self.chrome.execute_script("var evt = document.createEvent('Event');evt.initEvent('load', false, false);window.dispatchEvent(evt);")
            print self.chrome.page_source.encode('latin-1', 'ignore')
            print 'Locating iframe'
            captcha_iframe = WebDriverWait(self.chrome, 10).until(
                ec.presence_of_element_located(
                    (
                        By.TAG_NAME, 'iframe'
                    )
                )
            )

            ActionChains(self.chrome).move_to_element(captcha_iframe).click().perform()

            self.chrome.switch_to_frame(captcha_iframe)

            captcha_box = WebDriverWait(self.chrome, 10).until(
                ec.presence_of_element_located(
                    (
                        By.ID, 'recaptcha-anchor'
                    )
                )
            )
            
            wait_between(0.5, 0.7)
            print 'Clicking checkbox'
            captcha_box.click()
            #self.chrome.execute_script("arguments[0].click()", captcha_box)
            print 'Switch to main frame'
            self.chrome.switch_to.default_content()
            print self.chrome.page_source.encode('latin-1', 'ignore')
            wait_between(2.0, 2.5)
                
            solved = False
            timeout = time.time()+60
            print 'Checking if solved'
            while not solved:
                self.chrome.switch_to_frame(captcha_iframe)
                try:
                    self.chrome.find_element_by_xpath('//span[@aria-checked="true"]')
                    solved = True
                except:
                    pass
                wait_between(1.0, 2.0)
                self.chrome.switch_to.default_content()

            print 'Solved!'
            self.chrome.switch_to.default_content()

            submit = WebDriverWait(self.chrome, 10).until(
                    ec.presence_of_element_located((By.ID, 'submit')))
            submit.click()

            while True:
                print self.chrome.page_source.encode('latin-1', 'ignore') 
                if 'OK|' in self.chrome.page_source:
                    print self.chrome.page_source.split('|')[1]
                    break
                time.sleep(1)

    
e=Emulate()
while True:
    try:
        e.new_browser()               
        e.solve()
    except KeyboardInterrupt:
        e.chrome.quit()
        break
