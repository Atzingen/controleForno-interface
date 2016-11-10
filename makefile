clean-pyc:
	del /q /s *.pyc

clean-qtui:
	del source\\forno_gui.py

qt-ui:
	pyuic GUI/forno_design.ui -o source/forno_gui.py

run:
	python source/app.py
