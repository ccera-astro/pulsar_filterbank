TARGETS=pulsar_filterbank.py
PY=fb_helper.py
SOURCES=pulsar_filterbank.grc

#
# Generate the .py from the .grc
#
%.py: %.grc
	-grcc -d . $<
# Insert the synchronization code (if it's a UHD source)
	-./insert_sync_code $@ gps uhd_radio
# Inser the update-header code right after 'tb.wait' in the flow-graph
	-./insert_arbitrary_code $@ '    tb.wait'    '    fb_helper.update_header(None, None)'

all: $(TARGETS)

install: $(TARGETS) $(PY)
	cp $(TARGETS) $(PY) /usr/local/bin

clean:
	rm -f pulsar_filterbank.py
	rm -f *.header *.fil *.csv
