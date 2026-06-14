from DrissionPage import ChromiumOptions
options = ChromiumOptions()
path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
options.set_browser_path(path)
options.save()