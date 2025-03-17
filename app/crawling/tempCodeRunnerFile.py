def get_link(driver):
    anchors = driver.find_elements('tag name', 'a')    
    anchors = [a.get_attribute('href') for a in anchors]
    anchors = [a for a in anchors if str(a).startswith("https://www.instagram.com/p/")][:5]
    return anchors[:5]