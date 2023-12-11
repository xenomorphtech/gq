from selenium.webdriver.common.by import By
import seleniumwire.undetected_chromedriver.v2 as uc
import undetected_chromedriver as uc_local
import sys, time, json, subprocess
import warnings, logging, requests
from xvfbwrapper import Xvfb
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

redirect_uri = "com.googleusercontent.apps.14578396089-bc5a3sb7d2qm4snl13f4askmk0e3gq0g"
version_main = int(
    str(subprocess.run(["chromedriver", "-v"], stdout=subprocess.PIPE).stdout).split(" ")[1].split(".")[0])


def driver_arguments(chrome_options):
    chrome_options.add_argument(f'--no-first-run --no-service-autorun --password-store=basic')
    chrome_options.add_argument(f'--disable-gpu')
    chrome_options.add_argument(f'--no-sandbox')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(f'--disable-dev-shm-usage')
    return chrome_options


vdisplay = None
driver = None

def run_chrome(proxy):
    global driver, vdisplay
    vdisplay = Xvfb(width=800, height=1200)
    vdisplay.start()

    proxy = json.loads(proxy)
    if proxy and proxy.get('username') and proxy['type'] in ['socks5', 'http']:
        if proxy['type'] == 'socks5':
            proxy_http = "%s://%s:%s@%s:%s" % (
                proxy['type'], proxy['username'], proxy['password'], proxy['ip'], proxy['port'])
            proxy_https = proxy_http
        else:
            proxy_http = "%s://%s:%s@%s:%s" % ('http', proxy['username'], proxy['password'], proxy['ip'], proxy['port'])
            proxy_https = "%s://%s:%s@%s:%s" % (
                'https', proxy['username'], proxy['password'], proxy['ip'], proxy['port'])

        sel_options = {'proxy': {'http': proxy_http, 'https': proxy_https}}
        chrome_options = uc.ChromeOptions()
        opts = driver_arguments(chrome_options)
        driver = uc.Chrome(seleniumwire_options=sel_options, options=opts, headless=False, version_main=version_main,
                           enable_cdp_events=True)
        return driver, vdisplay

    elif proxy:
        chrome_options = uc_local.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s://%s:%s' % (proxy['type'], proxy['ip'], proxy['port']))
        chrome_options.add_argument("--host-resolver-rules='MAP * 0.0.0.0 , EXCLUDE 127.0.0.1'")
        opts = driver_arguments(chrome_options)
        driver = uc_local.Chrome(options=opts, headless=False, version_main=version_main, enable_cdp_events=True)
        return driver, vdisplay
    else:
        chrome_options = uc_local.ChromeOptions()
        opts = driver_arguments(chrome_options)
        driver = uc_local.Chrome(options=opts, headless=False, version_main=version_main, enable_cdp_events=True)
        return driver, vdisplay


def mylousyprintfunction(message):
    doc_url = message['params']['documentURL']
    if doc_url.startswith(redirect_uri):
        print("$RESULT$:" + doc_url)
        print("killing display")
        vdisplay.stop()
        print("killing driver")
        driver.quit()
        print("done")
        exit()


def login(driver, url, email, password, emailh):
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'identifierId')))
    except:
        print("proxy_timeout 1")
        driver.save_screenshot('gmail_error/proxy_timeout1_.png')
    else:
        res(driver, email, password, emailh, 0)

def result_error(res):
    print("$ERROR$" + res)
    print("killing display")
    vdisplay.stop()
    print("killing driver")
    driver.quit()
    print("done")
    exit()

def check_errors(url, driver):
    if url.startswith("https://accounts.google.com/o/oauth2/v2/auth/deniedsigninrejected?"):
        if driver.find_elements(By.XPATH, "//div[@class='PrDSKc']") != []:
            text = driver.find_element(By.XPATH, "//div[@class='PrDSKc']").text
            if text == "Your sign-in settings don’t meet your organization’s 2-Step Verification policy.":
                result_error("gmail_verify")
            else:
                driver.save_screenshot('gmail_error/unknow_proxy_timeout5_' + email + '.png')
                result_error("proxy_timeout")
        else:
            driver.save_screenshot('gmail_error/unknow_deniedsigninrejected2_' + email + '.png')
            result_error("gmail_error")

    elif url.startswith("https://accounts.google.com/v3/signin/deletedaccount?"):
        result_error("gmail_not_exist")

    elif url.startswith("https://accounts.google.com/signin/v2/identifier?") and driver.find_element(
            By.XPATH, "//div[@class='o6cuMc']").text:
        result_error("gmail_not_exist")

    elif url.startswith("https://accounts.google.com/signin/oauth/deniedsigninrejected?"):
        result_error("gmail_verify")
    elif url.startswith("https://accounts.google.com/v3/signin/rejected?"):
        result_error("gmail_verify")
    elif url.startswith("https://accounts.google.com/signin/v2/challenge/dp?"):
        result_error("gmail_verify")
    elif url.startswith("https://accounts.google.com/signin/v2/challenge/ootp?"):
        result_error("gmail_verify")
    elif url.startswith("https://accounts.google.com/signin/v2/challenge/ipp?"):
        result_error("gmail_verify")
    elif url.startswith("https://accounts.google.com/signin/v2/challenge/kpp?"):
        result_error("new_phone_verify")
    elif url.startswith("https://accounts.google.com/signin/v2/challenge/iap?"):
        result_error("new_phone_verify")
    elif url.startswith("https://accounts.google.com/speedbump/idvreenable?"):
        result_error("new_phone_verify")
    elif url.find("/signin/v2/disabled/explanation") != -1:
        result_error("gmail_blocked")

def res(driver, email, password, emailh, times):
    time.sleep(1)
    url = driver.current_url
    print(url)

    check_errors(url, driver)

    if url.startswith("https://accounts.google.com/o/oauth2/v2/auth/identifier?") or url.startswith(
            "https://accounts.google.com/v3/signin/identifier?"):
        driver.find_element(By.ID, "identifierId").send_keys(email)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'identifierNext')))
        driver.find_element(By.ID, "identifierNext").click()
        time.sleep(7)
        
        res_1(driver, email, password, emailh, 0)
    if times > 20:
        result_error("timeout_identifier")
    else:
        res(driver, email, password, emailh, times + 1)


def res_1(driver, email, password, emailh, times):
    time.sleep(1)
    url = driver.current_url
    print(url)

    check_errors(url, driver)

    if url.startswith("https://accounts.google.com/o/oauth2/v2/auth/identifier?") or url.startswith(
            "https://accounts.google.com/v3/signin/identifier?"):
        driver.save_screenshot('gmail_error/catpcha_' + str(time.time()) + '.png')
        result_error("probably_captcha")

    if url.startswith("https://accounts.google.com/signin/v2/challenge/selection?"):
        helper = driver.find_elements(By.XPATH, "//li[@class='JDAKTe cd29Sd zpCp3 SmR8']")
        if emailh != "" and helper != []:
            try:
                helper[-2].click()
            except:
                driver.save_screenshot('gmail_error/unknow_proxy_timeout1_' + email + '.png')
                result_error("proxy_timeout")
            else:
                time.sleep(4)
                res_1(driver, email, password, emailh, 0)
        else:
            result_error("gmail_verify")
    elif url.startswith("https://accounts.google.com/signin/v2/challenge/kpe?"):
        driver.find_element(By.ID, "knowledge-preregistered-email-response").send_keys(emailh)
        time.sleep(4)
        driver.find_element(By.XPATH, "//div[@class='FliLIb DL0QTb']").click()
        time.sleep(4)
        res_1(driver, email, password, emailh, 0)
    elif url.startswith("https://accounts.google.com/info/unknownerror?"):
        driver.save_screenshot('gmail_error/unknow_proxy_timeout2_' + email + '.png')
        result_error("proxy_timeout")

    elif url.startswith("https://accounts.google.com/speedbump/gaplustos?") and driver.find_elements(
            By.ID, "accept") != []:
        driver.find_element(By.ID, "accept").click()
        res_1(driver, email, password, emailh, 0)
    elif url.startswith("https://accounts.google.com/speedbump/gaplustos?") and driver.find_elements(
            By.ID, "confirm") != []:
        driver.find_element(By.ID, "confirm").click()
        res_1(driver, email, password, emailh, 0)
    elif url.startswith("https://accounts.google.com/speedbump/gaplustos?") and driver.find_elements(
            By.TAG_NAME, 'button') != []:
        driver.find_element(By.TAG_NAME, 'button').click()
        res_1(driver, email, password, emailh, 0)
    elif url.startswith("https://accounts.google.com/signin/oauth/consent?"):
        time.sleep(4)
    elif url.startswith("https://accounts.google.com/v3/signin/challenge/pwd?") and driver.find_elements(
            By.XPATH, "//div[@jsname='B34EJ']") != []:
        text = driver.find_element(By.XPATH, "//div[@jsname='B34EJ']").text
        if text == '':
            try:
                driver.find_element(By.CSS_SELECTOR, "input[type=password]").send_keys(password)
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'passwordNext')))
            except:
                driver.save_screenshot('gmail_error/unknow_proxy_timeout3_' + email + '.png')
                result_error("proxy_timeout")
            else:
                driver.find_element(By.ID, "passwordNext").click()
                driver.add_cdp_listener('Network.requestWillBeSent', mylousyprintfunction)
                time.sleep(4)
                res_1(driver, email, password, emailh, 0)
        elif text:
            result_error("gmail_password_changed")
        else:
            res_1(driver, email, password, emailh, 0)

    elif times > 5:
        err_url = str.replace(str.split(url, '?')[0], '/', '_')
        driver.save_screenshot('gmail_error/unknow_' + err_url + '_' + email + '.png')
        result_error("gmail_error")
    else:
        times = times + 1
        res_1(driver, email, password, emailh, times)


def spoof(driver):
    #with open('./stealth.min.js/stealth.min.js') as f:
    #   driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #    "source": f.read()
    #   })
    print("Default UserAgent is: "+driver.execute_script("return navigator.userAgent;"))
    
    #driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 10; Generic Android-x86_64 Build/QD1A.190821.014.C2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/79.0.3945.36 Safari/537.36'})
    #print(driver.execute_script("return navigator.userAgent;"))


if __name__ == '__main__':
    print("hello world")
    warnings.filterwarnings("ignore")
    logging.getLogger(requests.packages.urllib3.__package__).setLevel(logging.ERROR)
    url = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    email_helper = sys.argv[4]
    proxy = sys.argv[5]
    #driver, vdisplay = 
    run_chrome(proxy)
    #spoof(driver)
    try:
        login(driver, url, email, password, email_helper)
    except Exception as e:
        print("Something went wrong", e)
    finally:
        vdisplay.stop()
        driver.quit()

