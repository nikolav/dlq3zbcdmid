import base64

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from utils.text_to_uri_data import text_to_uri_data


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

params = { 
  'printBackground' : True ,
  'landscape'       : False,
  # a4
  'paperWidth'      : 8.26,
  'paperHeight'     : 11.68,  
}

def printHtmlToPDF(text = ''):
  service = Service()
  driver  = webdriver.Chrome(
    service = service, 
    options = chrome_options)
    
  driver.get(text_to_uri_data(text))
  
  pdfdata = driver.execute_cdp_cmd("Page.printToPDF", params)
  pdf     = base64.b64decode(pdfdata['data'])
  
  driver.quit()

  return pdf
