import pyautogui
import webbrowser
import time
pyautogui.FAILSAFE = True
def automate_page_entry():
    url = "https://practicetestautomation.com/practice-test-login/"  
    webbrowser.open(url)
    time.sleep(5)
    pyautogui.press('tab', presses=9, interval= 0.1)
    pyautogui.write("student", interval=0.05)
    pyautogui.press('tab')
    pyautogui.write("Password123", interval=0.05)
    pyautogui.press('tab')
    pyautogui.press('enter')                        
if __name__ == "__main__":
    automate_page_entry()                   