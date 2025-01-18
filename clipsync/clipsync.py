#!/usr/bin/env python
import subprocess
import traceback
import time

def getWaylandClipboard():
    try:
        print("getting wayland clipboard")
        mime = getWaylandMimeType()
        return tryDecode(subprocess.run(['wl-paste', '-t', mime], capture_output=True, timeout=0.5).stdout)
    
    except Exception as e:
        if type(e) is subprocess.TimeoutExpired:
            #assume we got garbage
            return ''
        print(traceback.format_exc())

def getX11Clipboard():
    try:
        print("getting xorg clipboard")
        mime = getX11MimeType()
        return tryDecode(subprocess.run(['xclip', '-o', '-selection', 'clipboard', '-t', mime], capture_output=True, timeout=0.5).stdout)
    
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
        subprocess.run(['xclip', '-selection', 'clipboard', '-t', mime], input=input)
        if not "text" in mime:
            #hack to undo whatever xclip messes up when it gets sync'd to the wl clipboard
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

def main():
    #give enough time for the clipboard to ready up
    time.sleep(5)
    #make sure we can run
    checkRequirements()
    #assume we have nothing
    lastclip = ''
    print(f"last {lastclip}")
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

        if wValue == xValue:
            # stops everything from firing on x selection
            continue

        if wValue and wValue != lastclip:
            setX11Clipboard(tryEncode(wValue), wMime)
            lastclip = wValue
            storeClipHist(tryEncode(lastclip), cliphistenabled)
            # makes wayland the more important clipboard - this helps everything run smoothly
            continue

        if xValue and xValue != lastclip:
            setWaylandClipboard(tryEncode(xValue), xMime)
            lastclip = xValue
            storeClipHist(tryEncode(lastclip), cliphistenabled)

if __name__ == '__main__':
    main()