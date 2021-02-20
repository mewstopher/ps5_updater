import time

def wait_to_click(type, value, driver):
    """
    check in element is clickable yet on page.
    """
    if type == 'id':
        action = driver.find_element_by_id
    elif type == 'xpath':
        action = driver.find_element_by_xpath
    counter = 0
    while counter < 11:
        try:
            action(value).click()
            break
        except Exception:
            counter += 1
            time.sleep(5)
            print('sleeping')




