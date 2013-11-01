
ifndef $(CONFIG_DIR)
	CONFIG_DIR=/etc/home/
endif

ifndef $(BIN_DIR)
	BIN_DIR=/usr/local/bin/
endif

ifndef $(SYSTEMD_DIR)
	SYSTEMD_DIR=/etc/systemd/system/
endif

install:
	mkdir -p $(CONFIG_DIR)
	cp rulesRest.cfg $(CONFIG_DIR)
	cp servers.json $(CONFIG_DIR)/monitor-servers.json
	cp rulesRestServer.py $(BIN_DIR)/home-rulesRestServer.py
	cp home-rulesRest.service $(SYSTEMD_DIR)
	cp monitor.py $(BIN_DIR)/home-monitor.py
	cp home-monitor.service $(SYSTEMD_DIR)
