# clipsync: the daemon that lives in your computer that shuttles wayland and xorg clipboards
Synchronizes the contents of your wayland and x11 clipboards in a MIME type aware fashion, designed in such a way to continue running should the nukes in your computer go off.  

If wayland copies don't trigger `clipnotify` this will not work.  

This will probably only function well in a wlroots based compositor (and hyprland)

## Dependencies
```
wl-copy
wl-paste
xclip
clipnotify
```

## Optional Dependencies
```
cliphist
```

## Installation
### Arch (via sparse checkout)
```sh
git init clipsync
cd clipsync
git remote add -f origin https://github.com/alexankitty/clipsync
git config core.sparseCheckout true
echo "packaging" >> .git/info/sparse-checkout
git pull origin main
cd packaging
makepkg -si
```
I'm too lazy to put the PKGBUILD up on the AUR. You do it.

### Most Distros
Run `./install.sh` with the terminal of your choosing, and then add the `clipsync` to the autostart of your window manager.  
Alternatively you may use the python build system with `./buildandinstall.sh` but please be aware this script is configured with `--break-system-packages`. It is recommended setting it up with your distro's build system, instead.

## Important
If you are using wl-paste to watch your clipboard, please consider disabling it as it will interfere with this application doing the same thing.

## Why did this happen?
I was getting frustrated with not being able to copy and paste correctly between xwayland and wayland applications. So I did a little bit of research, and on a github issue I found a bash script at the bottom of [this issue](https://github.com/hyprwm/Hyprland/issues/6132) which claimed to resolve the issue. However it had a lot of problems that stemmed from the lack of code blocking, and no MIME type awareness. So I created this to fix all of the shortcomings.

## Features
Image Sync
File URI Sync
Text Sync
Basically runs as a daemon
Clipboard history (via cliphist)
... and maybe more
