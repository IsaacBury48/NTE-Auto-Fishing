#**NTE Auto Fishing**

##**Description**

This program is designed to allow AFK fishing when used in conjuction with an autoclicker (mostly cause I haven't added that funcitonality yet)

##**Usage**

1. Download and install Python 3.14.0+ ; Be sure to add python to the environmental variables
    Double check the python installation with the following command:
        >python --version
2. Install the following python packages\
    - NumPy\
    - opencv-python\
    - pyautogui\
    - pynput\
    - mss\
    - pillow\
    This can be done with the following command in an elevated command prompt:\
        >pip install numpy opencv-python pyautogui pynput mss pillow
3. Open NTE and Naviagate to the Desired Fishing spot
4. Select "Start Fishing"; Ensure there is a Fish Hook in the bottom left corner
5. Open the Program and press "Start"

*Note: The program waits 5 seconds to allow NTE to be focused. Start the Auto-Clicker after the program, otherwise the Auto Fishing isn't truly afk.*

##**Technical Details**

This program is designed to check in specific spots of the screen for specific pixel hex colors.
Based on these colors, it will provide various keyboard input to allow autofishing. There is 
currently no way to Hotkey to Start/Stop of the program yet. 

*This was made in all of 5 hours, 50% vibe-coded, 50% me-coded.*