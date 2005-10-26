%.py: %.ui
	pyuic $< > $@
	
targets= \
 uicmainwindow.py \
 uicaboutdlg.py \
 uicumlconnectorattributedlg.py \
 uictextaligndlg.py \
 uicpageformatdlg.py \
 uicgridlinesdlg.py \
 uictextmarginsdlg.py \
 uiccollaborationwidget.py \
 uicservercontrol.py
 
all: $(targets) icons

icons:
	cd images; make	

clean:
	cd images; make	clean
	rm -rf *.ps
	rm -rf *.pdf
	rm -rf *.svg
	rm -rf *.pyc
	rm -rf uic*.py
	rm -rf *~
	rm -rf noname_*.kg

