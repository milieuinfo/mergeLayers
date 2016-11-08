# translation
TRANSLATIONS = i18n/mergeLayers_nl.ts

SOURCES = \
	__init__.py \
	mergeLayers.py mergeLayers_dialog.py

FORMS = ui_mergeLayers_dialog.ui
#----
PLUGINNAME = merge_Layers

PY_FILES = \
	__init__.py \
	mergeLayers.py mergeLayers_dialog.py utils.py

UI_FILES = ui_mergeLayers_dialog.py

EXTRAS = metadata.txt images i18n

RESOURCE_FILES = resources_rc.py

PLUGIN_UPLOAD = $(c)/scripts/plugin_upload.py

QGISDIR = .qgis2

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES) 

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	#pyuic4 -o $@ $<
	python C:\OSGeo4W64\apps\Python27\lib\site-packages\PyQt4\uic\pyuic.py -o $@ $<

deploy: compile transup
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	if [ -d "$(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)" ]; then rm -r $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME); fi
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	#cp -vfr i18n $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The dclean target removes compiled python files from plugin directory
# also deletes any .git entry
dclean:
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;


derase:
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

zip: deploy
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f build/$(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/build/$(PLUGINNAME).zip $(PLUGINNAME)

package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

#transup:
#	@chmod +x scripts/update-strings.sh
#	@scripts/update-strings.sh $(LOCALES)

transup: 
	pylupdate4 Makefile
	lrelease ${TRANSLATIONS}

transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)