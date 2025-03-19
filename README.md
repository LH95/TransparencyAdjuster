請認真上班，斟酌使用

pip install pyinstaller
pip install PyQt5 pywin32
pyinstaller --onefile --windowed --add-data "paw.png;." --icon="paw_slider.ico" TransparencyAdjuster.py
