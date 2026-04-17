from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://tol.njoyn.com/CL3/xweb/Xweb.asp?tbtoken=bFhRRxMXCG91FHV5RFJTCCNKcRFEcCVbe0hZJysPE2NcWzJpWzEfchd9BQkbURNUTncqWA%3D%3D&chk=ZVpaShw%3D&CLID=56677&page=joblisting")

# Wait for element to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "NjnSectionTable"))
)

html = driver.page_source
driver.quit()

print(html)
