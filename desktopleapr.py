#! /usr/bin/env python
#
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
#
# Using commands module instead of subprocess to spawn OS commands because,
# even though the later is the preferred method, it appears to have better
# performance. Reference: http://stackoverflow.com/questions/10888846/python-subprocess-module-much-slower-than-commands-deprecated
#
#

import Leap, sys
from Xlib import X, display, ext, XK

class Listnr(Leap.Listener):
    debug=0
    screenx=0
    screeny=0
    scalex=1.0
    scaley=1.0
    offsety=20.
    claw=0
    switcher=0
    rotationlock=0L
    nframes=10 # frames to average

    frames=list()
    prevframes=list()
    rootw=0

    def on_init(self, controller):
        import subprocess, re
        from time import sleep
# Get screen resolution
        displ=display.Display()
        s=displ.screen()
        Listnr.screenx=s.width_in_pixels
        Listnr.screeny=s.height_in_pixels
        Listnr.screenxmm=s.width_in_mms
        Listnr.screenymm=s.height_in_mms
        Listnr.scalex=s.width_in_pixels/300
        Listnr.scaley=s.height_in_pixels/300
        Listnr.rootw=s.root
        Listnr.display=displ
        print "Screen size is:",Listnr.screenx,Listnr.screeny
# Open file with debug output
        if (Listnr.debug == 1):
            f=open('output.txt','w')
            for ind in range(5): f.write(str(ind)+'\n')
            f.close()
# Create frame buffer
        print 'Initializing Leap Motion...'
        itry=0
        while (not controller.frame(2*Listnr.nframes).is_valid):
            itry+=1
            if itry == 1e5:
                print "Something's not right. Make sure the Leap Motion is connected"
                print 'and the leapd daemon is running'
                sys.exit(1)
        for iframe in range(Listnr.nframes):
            Listnr.frames.append(controller.frame(iframe))
            Listnr.prevframes.append(controller.frame(iframe+Listnr.nframes))
        print "Frame buffer sizes:",len(Listnr.frames),len(Listnr.prevframes)
#
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):

        def flush_buffer():
            Listnr.prevframes[0:Listnr.nframes]=Listnr.frames[0:Listnr.nframes]

        import commands
        from subprocess import call
        from time import sleep

        debug = Listnr.debug
#        window=Listnr.rootw.query_pointer().child
        ctrlkey=Listnr.display.keysym_to_keycode(XK.XK_Control_L)
        altkey=Listnr.display.keysym_to_keycode(XK.XK_Alt_L)
        shiftkey=Listnr.display.keysym_to_keycode(XK.XK_Shift_L)
        tabkey=Listnr.display.keysym_to_keycode(XK.XK_Tab)
        leftkey=Listnr.display.keysym_to_keycode(XK.XK_Left)
        rightkey=Listnr.display.keysym_to_keycode(XK.XK_Right)
        currentframe=controller.frame()

        nframes2=Listnr.nframes-10 # Use few frames for pointing to avoid lag
        nframes=Listnr.nframes

        Listnr.prevframes.pop(0) # Remove first element and shift list
        Listnr.prevframes.append(Listnr.frames[0])
        Listnr.frames.pop(0) # Remove first element and shift list
        Listnr.frames.append(currentframe)

        numfingers=len(currentframe.hands[0].fingers)
# Get average quantities from frame collections
        norm=1./Listnr.nframes
        norm2=1./(nframes-nframes2+1)
        avtime=sum(Fr.timestamp for Fr in Listnr.frames)*norm
        prevavtime=sum(Fr.timestamp for Fr in Listnr.prevframes)*norm
        avnhands=sum(len(Fr.hands) for Fr in Listnr.frames)*norm
        prevavnhands=sum(len(Fr.hands) for Fr in Listnr.prevframes)*norm
        avpitch=sum(Fr.hands[0].direction.pitch for Fr in Listnr.frames)*Leap.RAD_TO_DEG*norm
        avsphere=sum(Fr.hands[0].sphere_radius for Fr in Listnr.frames)*norm
        prevavpitch=sum(Fr.hands[0].direction.pitch for Fr in Listnr.prevframes)*Leap.RAD_TO_DEG*norm
        avnumfingers=sum(len(Fr.hands[0].fingers) for Fr in Listnr.frames)*norm
        prevavnumfingers=sum(len(Fr.hands[0].fingers) for Fr in Listnr.prevframes)*norm

        pointervalid=0
        prevavpos=[0.,0.,0.]
        nadded=0
        for Fr in Listnr.prevframes[nframes2:nframes]:
            if Fr.hands[0].is_valid:
                prevavpos[0]+=Fr.hands[0].palm_position[0]
                prevavpos[1]+=Fr.hands[0].palm_position[1]
                prevavpos[2]+=Fr.hands[0].palm_position[2]
                nadded+=1
        if nadded >= 1:
            prevavpos[0]=prevavpos[0]*1./nadded
            prevavpos[1]=prevavpos[1]*1./nadded
            prevavpos[2]=prevavpos[2]*1./nadded
        avpos=[0.,0.,0.]
        avvel=[0.,0.,0.]
        nadded=0
        for Fr in Listnr.frames[nframes2:nframes]:
            if Fr.hands[0].is_valid:
                avpos[0]+=Fr.hands[0].palm_position[0]
                avpos[1]+=Fr.hands[0].palm_position[1]
                avpos[2]+=Fr.hands[0].palm_position[2]
                avvel[0]+=Fr.hands[0].palm_velocity[0]
                avvel[1]+=Fr.hands[0].palm_velocity[1]
                avvel[2]+=Fr.hands[0].palm_velocity[2]
                pointervalid=1
                nadded+=1
        if pointervalid == 1:
            avpos[0]=avpos[0]*1./nadded
            avpos[1]=avpos[1]*1./nadded
            avpos[2]=avpos[2]*1./nadded
            avvel[0]=avvel[0]*1./nadded
            avvel[1]=avvel[1]*1./nadded
            avvel[2]=avvel[2]*1./nadded

        if avnhands > 0.5:
            handhorizontal=0
            prevhandhorizontal=0
            handvertical=0
            prevhandvertical=0
            if avpitch > -10 and avpitch < 20: handhorizontal=1
            if prevavpitch > -10 and prevavpitch < 20: prevhandhorizontal=1
            if avpitch > 55 and avpitch < 70: handvertical=1
            if avpitch < -60 and avpitch > -90: handvertical=-1
            if prevavpitch > 35 and prevavpitch < 70: prevhandvertical=1

            if pointervalid == 1:
                if (avnumfingers > 0.7 and avnumfingers < 1.5) or Listnr.claw == 1 or Listnr.switcher == 1 : # Pointer
                    coordx=(avpos[0]+150.)*Listnr.scalex
                    coordx=min(coordx,Listnr.screenx)
                    coordx=max(coordx,0)
                    coordy=Listnr.screeny-(avpos[1]-150)*Listnr.scaley
                    coordy=min(coordy,Listnr.screeny)
                    coordy=max(coordy,0)
                    Listnr.rootw.warp_pointer(coordx,coordy)
                    Listnr.display.flush()

# Switcher
            if avnumfingers >= 1.5 and handvertical==-1 and Listnr.switcher==0:
                Listnr.switcher=1
                print 'Invoking Switcher'
                ext.xtest.fake_input(Listnr.display, X.KeyPress, ctrlkey)
                ext.xtest.fake_input(Listnr.display, X.KeyPress, shiftkey)
                ext.xtest.fake_input(Listnr.display, X.KeyPress, tabkey)
                ext.xtest.fake_input(Listnr.display, X.KeyRelease, tabkey)
                Listnr.display.flush()
                flush_buffer()
                Listnr.rotationlock = currentframe.timestamp

            if Listnr.switcher==1 and ( ( handhorizontal == 1 and avnumfingers <= 1.5 ) or avpos[2] < 0 ):
                print 'Release Switcher'
                Listnr.switcher=0
                ext.xtest.fake_input(Listnr.display, X.KeyRelease, ctrlkey)
                ext.xtest.fake_input(Listnr.display, X.KeyRelease, shiftkey)
                ext.xtest.fake_input(Listnr.display, X.ButtonPress, 1)
                ext.xtest.fake_input(Listnr.display, X.ButtonRelease, 1)
                Listnr.display.flush()
                flush_buffer()
                Listnr.rotationlock = currentframe.timestamp

            if debug >= 2:
                f=open('output.txt','r')
                lines=f.readlines()
                f.close()
                f=open('output.txt','w')
                for ind in range(4):
                    f.write(lines[len(lines)-(4-ind)])
                f.write('fingers:'+str(prevavnumfingers)+' '+str(avnumfingers)+' '+str(numfingers)+', hor:'+str(handhorizontal)+' x='+str(avpos[0])+' velx='+str(avvel[0])+'\n')
                f.close()

# debug printout
            if prevavnumfingers <= 1.5 and avnumfingers >= 3.8:
                print 'Open hand'
# Claw
            if prevavnumfingers >= 3.8 and avnumfingers <= 1.2 and handhorizontal == 1 and Listnr.switcher == 0 and Listnr.claw == 0:
                Listnr.claw=1
                print 'Claw!'
                ext.xtest.fake_input(Listnr.display, X.KeyPress, altkey)
                ext.xtest.fake_input(Listnr.display, X.ButtonPress, 1)
                Listnr.display.flush()
                flush_buffer()
                Listnr.rotationlock = currentframe.timestamp

            if ( ( avnumfingers >= 1.5 ) or avpos[2] < 0) and Listnr.claw == 1 :
                Listnr.claw=0
                print 'Claw release'
                print 'pos, vel=',avpos[0],avvel[0]
                ext.xtest.fake_input(Listnr.display, X.KeyRelease, altkey)
                ext.xtest.fake_input(Listnr.display, X.ButtonRelease, 1)
                Listnr.display.flush()
                flush_buffer()
                Listnr.rotationlock = currentframe.timestamp

            if ( (avvel[0] < -100 and numfingers >= 2) or avpos[0] < -230 ) and Listnr.claw == 1:
                print 'Minimizing!!'
                command='xdotool keyup Alt mouseup 1 getactivewindow windowminimize'
                if debug >=1:
                    comman=command+' windowactivate' # Bounce back to the screen
                [errors,output]=commands.getstatusoutput(command)
                if errors != 0:
                    print "xdotool is not installed! Minimizing doesn't work"
                Listnr.claw=0
                print 'velocity=',avvel[0],avpos[0]
                ext.xtest.fake_input(Listnr.display, X.KeyRelease, altkey)
                ext.xtest.fake_input(Listnr.display, X.ButtonRelease, 1)
                Listnr.display.flush()
                flush_buffer()
                Listnr.rotationlock = currentframe.timestamp
 
# Click
            if avnumfingers > 0.7 and avnumfingers < 1.5 and avpos[2] < 0 and prevavpos[2] > 0:
                print 'Click'
                ext.xtest.fake_input(Listnr.display, X.ButtonPress, 1)
                ext.xtest.fake_input(Listnr.display, X.ButtonRelease, 1)
                Listnr.display.flush()
                flush_buffer()
                Listnr.rotationlock = currentframe.timestamp

# Mouse scroll
            if currentframe.hands[0].is_valid and numfingers >= 4 and Listnr.claw == 0 and Listnr.switcher == 0 and Listnr.rotationlock*0 == 0:
                fingspeed=sum(finger.tip_velocity[1] for finger in currentframe.hands[0].fingers)
                fingspeed=fingspeed*1./numfingers
                if fingspeed-currentframe.hands[0].palm_velocity[1] < -150:
                    repeats=abs(int(fingspeed/50.))
                    repeats=max(repeats,0)
                    repeats=min(repeats,5)
                    print 'scrolling up ',repeats
                    for irep in range(repeats):
                        ext.xtest.fake_input(Listnr.display, X.ButtonPress, 4)
                        ext.xtest.fake_input(Listnr.display, X.ButtonRelease, 4)
                        Listnr.display.flush()
                        sleep(.1)
                    Listnr.rotationlock = currentframe.timestamp
                    flush_buffer()

                if fingspeed-currentframe.hands[0].palm_velocity[1] > 150:
                    repeats=abs(int(fingspeed/50.))
                    repeats=max(repeats,0)
                    repeats=min(repeats,5)
                    print 'scrolling down ',repeats
                    for irep in range(repeats):
                        ext.xtest.fake_input(Listnr.display, X.ButtonPress, 5)
                        ext.xtest.fake_input(Listnr.display, X.ButtonRelease, 5)
                        Listnr.display.flush()
                        sleep(.1)
                    Listnr.rotationlock = currentframe.timestamp
                    flush_buffer()
                    
# Rotate (switch desktop)
    # Clear lock if more than 1 second has elapsed since last rotation
            if Listnr.rotationlock != 0:
                if currentframe.timestamp-Listnr.rotationlock > 1e6:
                    Listnr.rotationlock=0
            elif avsphere > 60 and avpitch > 0:
                rotangle=0.
                rotaxis=0.
                for ind in range(nframes):
                    rotangle+=Listnr.frames[ind].rotation_angle(Listnr.prevframes[ind])*Leap.RAD_TO_DEG*norm
                    rotaxis+=Listnr.frames[ind].rotation_axis(Listnr.prevframes[ind])[1]*norm

                if rotangle > 10:
                    if rotaxis > 0.8:
                        print 'Rotating Right',rotangle
                        ext.xtest.fake_input(Listnr.display, X.KeyPress, ctrlkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyPress, altkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyPress, rightkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyRelease, ctrlkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyRelease, altkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyRelease, rightkey)
                        Listnr.display.flush()
                        flush_buffer()
                        Listnr.rotationlock = currentframe.timestamp
                    if rotaxis < -0.8:
                        print 'Rotating Left',rotangle
                        ext.xtest.fake_input(Listnr.display, X.KeyPress, ctrlkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyPress, altkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyPress, leftkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyRelease, ctrlkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyRelease, altkey)
                        ext.xtest.fake_input(Listnr.display, X.KeyRelease, leftkey)
                        Listnr.display.flush()
                        flush_buffer()
                        Listnr.rotationlock = currentframe.timestamp

# Ok, done
            Listnr.display.sync()
            return

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"


def main():
    # Create a sample listener and controller
    listener = Listnr()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()
