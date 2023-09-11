import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import os
from PIL import Image

appHeight = 1000 + 219
appWidth = 750 + 12

marginLeft = 26
marginTop = 21
marginRight = 29
marginBottom = 11

def screenshot_all_page(blink):
    imagelist = []
    driver = webdriver.Firefox()
    driver.set_window_size(appWidth + marginLeft + marginRight, appHeight + marginTop + marginBottom)
    driver.get(blink)
    time.sleep(20)
    for this_p in range(int(driver.find_element(By.XPATH, '//*[@id="totalPages"]').text) + 25):
        time.sleep(random.uniform(0,5))
        if this_p%25 == 0:
           time.sleep(15)		
        canvas = driver.find_element(By.CSS_SELECTOR, "#canvas0")
        canvas_base64 = driver.execute_script(f"return arguments[0].toDataURL('image/png').substring(21);", canvas)
        canvas_png = base64.b64decode(canvas_base64)
        with open(rf"D:\Taghche\book/{this_p}.png", 'wb') as f:
            f.write(canvas_png)
        driver.find_element(By.ID, '___nextPageMobile').click()

        image = Image.open(rf'D:\Taghche\book/{this_p}.png')
        image.load()

        width, height = image.size
        left = marginLeft
        top = marginTop - 50
        # right = width - marginRight
        right = width
        # bottom = height - marginBottom
        bottom = height

        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])

        background = background.crop((left, top, right, bottom))
        background.save(rf'D:\Taghche\book/{this_p}.png')

        imagelist.append(background)  
    imagelist[0].save(rf'D:\Taghche\book/shit.pdf', save_all=True, append_images=imagelist)

blink = "https://taaghche.com/"
screenshot_all_page( blink)
