import base64

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# load html in headless chrome
data    = '<a href="https://google.rs/">google.rs</a>'
b64data = base64.b64encode(data.encode('utf-8')).decode('utf-8')
uridata = f'data:text/html;base64,{b64data}'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service()
driver  = webdriver.Chrome(
  service = service, 
  options = chrome_options)

driver.get(uridata)

pdfdata = driver.execute_cdp_cmd(
  "Page.printToPDF", 
  { 
   'printBackground': True 
  })

pdf = base64.b64decode(pdfdata['data'])

with open('out.pdf', 'wb') as f:
  f.write(pdf)

driver.quit()

