run:
	python source/app.py

clean:
	del /q /s *.pyc
	del source\\forno_gui.py

clean-pyc:
	del /q /s *.pyc

clean-qtui:
	del source\\forno_gui.py

clean-ft:
	del /q /s *.so

ui:
	pyuic4 GUI/tela.ui -o source/forno_gui.py

ui-display:
	pyuic4 GUI/tela-display.ui -o source/forno_gui.py

ui-win:
	python C:\Users\Gustavo-PC\Anaconda2\Lib\site-packages\PyQt4\uic\pyuic.py GUI/tela.ui -o source/forno_gui.py

ui-display-win:
	python C:\Users\Gustavo-PC\Anaconda2\Lib\site-packages\PyQt4\uic\pyuic.py

f2py:
	f2py -c -m forno1d_fortran source/simulacao/forno1d.f90
	f2py -c -m alimento_fortran source/simulacao/alimento.f90
	mv alimento_fortran.so source/simulacao/alimento_fortran.so
	mv forno1d_fortran.so source/simulacao/forno1d_fortran.so

all-w:
	python C:\Users\Gustavo-PC\Anaconda2\Lib\site-packages\PyQt4\uic\pyuic.py GUI/tela.ui -o source/forno_gui.py
	python source/app.py

all-display-w:
	python C:\Users\Gustavo-PC\Anaconda2\Lib\site-packages\PyQt4\uic\pyuic.py
	python source/app.py

all:
	pyuic4 GUI/tela.ui -o source/forno_gui.py
	python source/app.py

all-display:
	pyuic4 GUI/tela-display.ui -o source/forno_gui.py
	python source/app.py

help:
	@echo "Makefile para execução de comandos para o software"
	@echo "Uso:"
	@echo ""
	@echo ""
	@echo " run: executa o programa principal e inicia a UI"
	@echo " clean-ui: Limpa os arquivos gerados da interface pelo pyuic"
	@echo " clean-pyc: Limpa os arquivos .pyc criados pelo interpretador"
	@echo " clean: Limpa os arquivos .pyc criados pelo interpretador e os gerados pelo pyuic"
	@echo " ui: executa o comando pyuic e cria os bindings do pyqt para a interface pelos arquivos .ui"
	@echo " ui: mesmo comando do .ui porém usando a interface do display"
	@echo " -w: comandos usandos no SO windows para teste"
