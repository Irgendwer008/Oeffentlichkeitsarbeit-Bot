


# Facebook:
# "https://www.youtube.com/watch?v=nPOgLZuuURs

import sys
import time
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from helper import Veranstaltungsdetails, PluginInfo, step
from credentials import _Logindaten

plugininfo = PluginInfo(FRIENDLYNAME="Meta Business Suite",
                        DEFAULTCATEGORY_KEY=None,
                        KATEGORIEN={})

def run(details: Veranstaltungsdetails, credentials: _Logindaten, plugins: list[str], driver: Firefox):
    
    driver.get('https://business.facebook.com/latest/home')
    
    step("Declining cookies")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title=\"Only allow essential cookies\"]"))).click()
    
    step("Clicking \"Login with Instagram\"")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/div/div[1]/div/div/div/div[2]/div/div/div/div[4]/div/div/div"))).click()
        
    step("Declining Instagram Cookies")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Decline optional cookies')]"))).click()
    
    step("Logging into Instagram")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys(credentials.INSTAGRAM_USERNAME)
    driver.find_element(By.NAME, "password").send_keys(credentials.INSTAGRAM_PASSWORD)
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, "button[type=\"submit\"] div"))
    
    step("Clicking \"Dont save login info\"")
    time.sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Not now')]"))).click()
    
    step("Clicking \"Create post\"")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Create post')]"))).click()
    
    step("Adding photo")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Add photo')]"))).click()
    
    step("Selecting File Manager")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Add from file manager')]"))).click()
    
    time.sleep(1)
    step("Selecting file from Desktop")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Desktop')]"))).click()
    '''
    JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
    """
    drop_target = driver.find_element(By.XPATH, "/html/body/div[5]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div/div")
    driver2 = drop_target.parent
    file_input = driver2.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(details.BILD_DATEIPFAD)'''