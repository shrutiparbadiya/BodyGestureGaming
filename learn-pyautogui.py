import pyautogui

# Move the mouse to (100, 200)
pyautogui.moveTo(100, 200, duration=1)

# Click at current location
pyautogui.click()

# Right-click
pyautogui.rightClick()

# Double-click
pyautogui.doubleClick()

# Move and click at (500, 300)
pyautogui.click(x=500, y=300)
