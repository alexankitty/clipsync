#!env sh

python -m build .
#please consider making this a system package
sudo pip install ./dist/clipsync-*.tar.gz --break-system-packages
echo "Installed! Go add it to your window manager's exec-once, or create a systemd service for it."

