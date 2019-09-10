TARGETS=pulsar_filterbank.py
PY=fb_helper.py
SOURCES=pulsar_filterbank.grc

%.py: %.grc
	-grcc -d . $<
	-./insert_sync_code pulsar_filterbank.py gps radio

all: $(TARGETS)

install: $(TARGETS) $(PY)
	cp $(TARGETS) $(PY) /usr/local/bin

clean:
	rm -f pulsar_filterbank.py
