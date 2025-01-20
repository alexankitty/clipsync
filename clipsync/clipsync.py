#!/usr/bin/env python
import subprocess
import traceback
import time
import argparse

verbose = False

def getWaylandClipboard():
    try:
        mime = getWaylandMimeType()
        return tryDecode(subprocess.run(['wl-paste', '-t', mime], capture_output=True, timeout=0.5).stdout)
    
    except Exception as e:
        if type(e) is subprocess.TimeoutExpired:
            #assume we got garbage
            return ''
        print(traceback.format_exc())

def getX11Clipboard():
    try:
        mime = getX11MimeType()
        return tryDecode(subprocess.run(['xclip', '-o', '-t', mime], capture_output=True, timeout=0.5).stdout)
    
    except Exception as e:
        if type(e) is subprocess.TimeoutExpired:
            #assume we got garbage
            return b''
        print(traceback.format_exc())

def getWaylandMimeType():
    try:
        targets = tryDecode(subprocess.run(['wl-paste', '-l'], capture_output=True).stdout)

        if 'text/uri-list' in targets:
            return 'text/uri-list'

        for target in targets.split('\n'):
            if 'image/' in target:
                return target
        
        #assume it's text because nothing bad could ever happen, right?
        #addendum: if this isn't set to utf-8, furryfox dies in a fire
        return 'text/plain;charset=utf-8'
    
    except Exception as e:
        print(traceback.format_exc())

def getX11MimeType():
    try:
        targets = tryDecode(subprocess.run(['xclip', '-o', '-selection', 'clipboard', '-t', 'TARGETS'], capture_output=True).stdout)
        if 'text/uri-list' in targets:
            return 'text/uri-list'

        for target in targets.split('\n'):
            if 'image/' in target:
                #is finding the first match really acceptable??
                return target
        
        #assume it's text because nothing bad could ever happen, right?
        return 'text/plain'

    except Exception as e:
        print(traceback.format_exc())

def setWaylandClipboard(input, mime):
    try:
        subprocess.run(['wl-copy', '-t', mime], input=input)

    except Exception as e:
        print(traceback.format_exc())

def setX11Clipboard(input, mime):
    try:
        log(mime)
        if 'text' in mime:
            # it doesn't like if you set the mime type on piped text
            subprocess.run(['xclip', '-i', '-t', mime], input=input)
        else:    
            subprocess.run(['xclip', '-i', '-t', mime], input=input)
            setWaylandClipboard(input, mime)
        
    except Exception as e:
        print(traceback.format_exc())

def storeClipHist(input, enabled):
    if not enabled:
        return
    try:
        subprocess.run(['cliphist', 'store'], input=input)
    except Exception as e:
        print(traceback.format_exc())

def tryDecode(data):
    try:
        if type(data) is bytes:
            return data.decode('utf-8').strip().strip('\x00')
    except:
        pass
    return data
    
def tryEncode(text):
    try:
        if type(text) is str:
            return text.encode('utf-8')
    except:
        pass
    return text

def commandExists(command):
    return not subprocess.run(['which', command], capture_output=True).returncode

def checkRequirements():
    reqs = ['wl-copy', 'wl-paste', 'xclip', 'clipnotify']
    missing = ''

    for req in reqs:
        if not commandExists(req):
            missing = f"{missing} {req}"

    missing = missing.strip()

    if missing:
        print(f"Missing the following requirements: {missing}")
        quit()

def log(info):
    global verbose
    if(verbose):
        print(info)

def main():
    parser = argparse.ArgumentParser(
        description='The daemon that lives in your computer that shuttles wayland and xorg clipboards.',
        epilog='Written by Alexankitty 2025'
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    global verbose
    verbose = args.verbose
    startupTime = 5
    if verbose:
        startupTime = 0
    #give enough time for the clipboard to ready up
    time.sleep(startupTime)
    #make sure we can run
    checkRequirements()
    #assume we have nothing
    lastclip = ''
    cliphistenabled = commandExists('cliphist')
    
    while True:
        try:
            subprocess.run('clipnotify')
        except:
            #if it dies it probably got killed
            exit()
        wValue = getWaylandClipboard()
        wMime = getWaylandMimeType()
        xValue = getX11Clipboard()
        xMime = getX11MimeType()

        log(f"Wayland: {wValue}, Mime: {wMime}")
        log(f"X11: {xValue}, Mime: {xMime}")
        log(f"Last: {lastclip}")

        if wValue == xValue:
            # stops everything from firing on x selection
            continue

        if wValue and wValue != lastclip:
            log("Updating X11 Clipboard")
            setX11Clipboard(tryEncode(wValue), wMime)
            lastclip = wValue
            storeClipHist(tryEncode(lastclip), cliphistenabled)
            # makes wayland the more important clipboard - this helps everything run smoothly
            continue

        if xValue and xValue != lastclip:
            log("Updating Wayland Clipboard")
            setWaylandClipboard(tryEncode(xValue), xMime)
            lastclip = xValue
            storeClipHist(tryEncode(lastclip), cliphistenabled)

if __name__ == '__main__':
    main()