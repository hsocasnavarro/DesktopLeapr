# DESKTOP LEAPER, Hector Socas-Navarro 2013 (hsocas.iac@gmail.com)
#  Experimental Python app using the LeapMotion API
#  Released under GPL v2 license. Please, give some credit if
#  you use this
#
# Requirements
# * Linux
# * Python
# * python-Xlib
#   * LeapMotion SDK
#   * if not in your path, LeapSDK/lib/Leap.py and LeapSDK/lib/x??/LeapPython.so
#        must be present in the running directory
# * OPTIONAL: xdotool (if not present, windows cannot be minimized) 
#
# Instructions:
#
#   This program sends simulated key presses to the X server in order to
#   interact with the window manager. The following key bindings need
#   to be associated with certain window manager actions to function
#   properly:
#     Ctrl+Alt+Left, Ctrl+Alt+Right: Switch to desktop on the left or 
#         right
#     Ctrl+Shift+Tab: Invoke the Window Switcher application. Assumed
#         behavior is that while Ctrl+Shift are held down the mouse
#         pointer can be used to select a window
#     Alt+Mouse left click: Grab a window until Alt key is released

#   *Use one finger to move the mouse pointer. Pointer is given by the 
#      position of the palm, not the finger but this is unnoticeable in
#      practice
#   *While moving the pointer, push the finger towards the screen above
#      the Leap Motion to generate a mouse click. Note: It is very 
#      difficult to make precise mouse clicks in this manner
#   *Activate window switcher by holding your hand open with all fingers
#      pointing down. Once activated the hand may be returned to
#      horizontal position but should still be open to move the pointer
#      to the desired window. Once the pointer is over the desired window
#      close hand and leave only one finger or move the hand towards the
#      screen to select that window. It takes practice to do this without
#      altering the pointer poisition.
#   *The window switcher is closed when either the hand is pushed towards
#      the screen above the leap motion or when it is in horizontal
#      position and closed or showing only one finger
#   *To grab a window, hold hour hand horizontally, open your hand
#      completely for a second and then close it quickly. Once a window
#      has been grabbed you can just move it to any other location and
#      release it by simply opening your hand again. It can also be
#      minimized by moving it rapidly to the left edge of the screen
#      (minimization is done invoking the xdotool command so you'd need
#      to have it installed and in the path).
#   *To scroll up or down, hold your hand horizontally with the palm
#      facing down and move all your fingers up or down while the mouse
#      pointer is over a window that can be scrolled.
#   *To switch to the desktop to the left or right, simply open your
#      hand with your palm facing up and slowly rotate it clockwise 
#      or counterclockwise. A slow rotation will be easier to pick up
#      by the Leap Motion.
#