#!env python
import subprocess
import traceback
import time

def getWaylandClipboard():
    try:
        mime = getWaylandMimeType()
        return tryDecode(subprocess.run(['wl-paste', '-t', mime], capture_output=True).stdout)
    
    except Exception as e:
        print(traceback.format_exc())

def getX11Clipboard():
    try:
        mime = getX11MimeType()
        return tryDecode(subprocess.run(['xclip', '-o', '-selection', 'clipboard', '-t', mime], capture_output=True).stdout)
    
    except Exception as e:
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
        return 'text/plain'
    
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

def storeClipHist(input):

    try:
        subprocess.run(['cliphist', 'store'], input=input)
    except Exception as e:
        print(traceback.format_exc())

def tryDecode(data):
    try:
        if type(data) is bytes:
            return data.decode('utf-8')
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
    #use the wayland clipboard as the intial source of truth
    lastclip = getWaylandClipboard()
    cliphist = commandExists('cliphist')
    
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

        if wValue != lastclip:
            setX11Clipboard(tryEncode(wValue), wMime)
            lastclip = wValue
            continue

        if xValue != lastclip:
            setWaylandClipboard(tryEncode(xValue), xMime)
            lastclip = xValue

        if cliphist:
            # todo: add an argument for turning off cliphist
            storeClipHist(tryEncode(lastclip))    

if __name__ == '__main__':
    main()