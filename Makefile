TARGETS=pulsar_filterbank.py
PY=fb_helper.py
SOURCES=pulsar_filterbank.grc

%.py: %.grc
	-grcc -d . $<

all: $(TARGETS)

install: $(TARGETS) $(PY)
	cp $(TARGETS) $(PY) /usr/local/bin
