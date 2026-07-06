wsl -u root
apt update && apt install python3-pip python3-venv -y
pip3 install uv --break-system-packages
uv sync