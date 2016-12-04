run:
	python source/app.py

clean-pyc:
	del /q /s *.pyc

clean-qtui:
	del source\\forno_gui.py

ui:
	pyuic4 GUI/tela.ui -o source/forno_gui.py

ui-display:
	pyuic4 GUI/tela-display.ui -o source/forno_gui.py

all:
	pyuic4 GUI/tela.ui -o source/forno_gui.py
	python source/app.py

all-display:
	pyuic4 GUI/tela-display.ui -o source/forno_gui.py
	python source/app.py
