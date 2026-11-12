'use strict';
'require view';
'require dom';
'require poll';
'require ui';
'require rpc';
'require uci';
'require form';
'require network';
'require firewall';

const isReadonlyView = !L.hasViewPermission();

function count_changes(section_id) {
	const changes = ui.changes.changes?.wireless;
	if (!Array.isArray(changes)) return 0;

	return changes.reduce((count, [, id]) => count + (id === section_id), 0);
}

function render_signal_badge(signalPercent, signalValue, noiseValue, wrap, mode) {
	let icon = L.resource('icons/signal-075-100.svg'), title, value;

	switch(true) {
	case(signalPercent  < 0): icon = L.resource('icons/signal-none.svg'); 	break;
	case(signalPercent == 0): icon = L.resource('icons/signal-000-000.svg');		break;
	case(signalPercent < 25): icon = L.resource('icons/signal-000-025.svg'); 	break;
	case(signalPercent < 50): icon = L.resource('icons/signal-025-050.svg');	break;
	case(signalPercent < 75): icon = L.resource('icons/signal-050-075.svg');	break;
	}

	if (signalValue) {
		if (noiseValue) {
			value = `${signalValue}/${noiseValue}\xa0${_('dBm')}`;
			title = [
				`${_('Signal')}: ${signalValue} ${_('dBm')}`,
				`${_('Noise')}: ${noiseValue} ${_('dBm')}`,
				`${_('SNR')}: ${signalValue - noiseValue} ${_('dBm')}`
			].filter(Boolean).join(' / ');
		}
		else {
			value = `${signalValue}\xa0${_('dBm')}`;
			title = `${_('Signal')} ${signalValue} ${_('dBm')}`;
		}
	}
	else if (signalPercent > -1) {
		switch (mode) {
			case 'ap':
				title = _('No client associated');
				break;

			case 'sta':
			case 'adhoc':
			case 'mesh':
				title = _('Not associated');
				break;

			default:
				title = _('No RX signal');
		}

		if (noiseValue) {
			value = `---/${noiseValue}\xa0${_('dBm')}`;
			title = `${title} / ${_('Noise')}: ${noiseValue} ${_('dBm')}`;
		}
		else {
			value = `---\xa0${_('dBm')}`;
		}
	}
	else {
		value = E('em', {}, E('small', {}, [ _('disabled') ]));
		title = _('Interface is disabled');
	}

	return E('div', {
		'class': wrap ? 'center' : 'ifacebadge',
		'title': title,
		'data-signal': signalValue,
		'data-noise': noiseValue
	}, [
		E('img', { 'src': icon }),
		E('span', {}, [
			wrap ? E('br') : ' ',
			value
		])
	]);
}

function render_network_badge(radioNet) {
	return render_signal_badge(
		radioNet.isUp() ? radioNet.getSignalPercent() : -1,
		radioNet.getSignal(), radioNet.getNoise(), false, radioNet.getMode());
}

function render_network_status(radioNet) {
	const mode = radioNet.getActiveMode();
	const bssid = radioNet.getActiveBSSID();
	const channel = radioNet.getChannel();
	const disabled = (radioNet.get('disabled') == '1' || uci.get('wireless', radioNet.getWifiDeviceName(), 'disabled') == '1');
	const is_assoc = (bssid && bssid != '00:00:00:00:00:00' && channel && mode != 'Unknown' && !disabled);
	const is_mesh = (radioNet.getMode() == 'mesh');
	const changecount = count_changes(radioNet.getName());
	let status_text = null;

	if (changecount)
		status_text = E('a', {
			href: '#',
			click: L.bind(ui.changes.displayChanges, ui.changes)
		}, _('Interface has %d pending changes').format(changecount));
	else if (!is_assoc)
		status_text = E('em', disabled ? _('Wireless is disabled') : _('Wireless is not associated'));

	return L.itemlist(E('div'), [
		is_mesh ? _('Mesh ID') : _('SSID'), (is_mesh ? radioNet.getMeshID() : radioNet.getSSID()) ?? '?',
		_('Mode'),       mode,
		_('BSSID'),      (!changecount && is_assoc) ? bssid : null,
		_('Encryption'), (!changecount && is_assoc) ? radioNet.getActiveEncryption() ?? _('None') : null,
		'',            status_text
	], [ ' | ', E('br') ]);
}

function format_wifirate(rate) {
	let s = `${rate.rate / 1000}\xa0${_('Mbit/s')}, ${rate.mhz}\xa0${_('MHz')}`;

	if (rate?.ht || rate?.vht) s += [
		rate?.vht && `, VHT-MCS\xa0${rate?.mcs}`,
		rate?.nss && `, VHT-NSS\xa0${rate?.nss}`,
		rate?.ht  && `, MCS\xa0${rate?.mcs}`,
		rate?.short_gi && ', ' + _('Short GI').replace(/ /g, '\xa0')
	].filter(Boolean).join('');

	if (rate?.he) s += [
		`, HE-MCS\xa0${rate?.mcs}`,
		rate?.nss    && `, HE-NSS\xa0${rate?.nss}`,
		rate?.he_gi  && `, HE-GI\xa0${rate?.he_gi}`,
		rate?.he_dcm && `, HE-DCM\xa0${rate?.he_dcm}`
	].filter(Boolean).join('');

	if (rate?.eht) s += [
		`, EHT-MCS\xa0${rate?.mcs}`,
		rate?.nss    && `, EHT-NSS\xa0${rate?.nss}`,
		rate?.eht_gi  && `, EHT-GI\xa0${rate?.eht_gi}`,
		rate?.eht_dcm && `, EHT-DCM\xa0${rate?.eht_dcm}`
	].filter(Boolean).join('');

	return s;
}

function network_updown(id, map, ev) {
	const radio = uci.get('wireless', id, 'device');
	const disabled = (uci.get('wireless', id, 'disabled') == '1') ||
	               (uci.get('wireless', radio, 'disabled') == '1');

	if (disabled) {
		uci.unset('wireless', id, 'disabled');
		uci.unset('wireless', radio, 'disabled');
	}
	else {
		uci.set('wireless', id, 'disabled', '1');

		let all_networks_disabled = true;
		const wifi_ifaces = uci.sections('wireless', 'wifi-iface');

		wifi_ifaces.forEach(wifi_iface => {
			if (wifi_iface.device == radio && wifi_iface.disabled != '1')
				all_networks_disabled = false;
		});

		if (all_networks_disabled)
			uci.set('wireless', radio, 'disabled', '1');
	}

	return map.save().then(function() {
		ui.changes.apply();
	});
}

function next_free_sid(offset) {
	let sid = 'wifinet' + offset;

	while (uci.get('wireless', sid))
		sid = 'wifinet' + (++offset);

	return sid;
}

function add_dependency_permutations(o, deps) {
	let res = [{}];

	Object.entries(deps).forEach(([key, list]) => {
		if (!Array.isArray(list)) return;

		res = list.flatMap(value => res.map(item => ({ ...item, [key]: value })));
	});

	res.forEach(dep => o.depends(dep));
}

return view.extend({
	poll_status: function(map, data) {
		const rows = map.querySelectorAll('.cbi-section-table-row[data-sid]');

		rows.forEach(row => {
			const section_id = row.getAttribute('data-sid');
			const radioNet = data[2].filter(function(n) { return n.getName() == section_id; })[0];
			const badge = row.querySelector('[data-name="_badge"] > div');
			const stat = row.querySelector('[data-name="_stat"]');
			const btns = row.querySelectorAll('.cbi-section-actions button');
			let busy = false;

			for (let i = 0; i < btns.length; i++)
				if (btns[i].classList.contains('spinning'))
					busy = true;

			if (!radioNet)
				return;

			dom.content(badge, render_network_badge(radioNet));
			dom.content(stat, render_network_status(radioNet));

			for (let i = 0; i < btns.length; i++)
				btns[i].disabled = isReadonlyView || busy;
		});

		const table = document.querySelector('#wifi_assoclist_table');
		const hosts = data[0];
		let trows = [];
		const radios = data[3];
		const zones = data[4];

		radios.forEach(zone => {
			const bss = zone;
			const name = hosts.getHostnameByMACAddr(bss.mac);
			const ipv4 = hosts.getIPAddrByMACAddr(bss.mac);
			const ipv6 = hosts.getIP6AddrByMACAddr(bss.mac);

			let hint;

			if (name && ipv4 && ipv6)
				hint = `${'%h'.format(name)} <span class="hide-xs">(${ipv4}, ${ipv6})</span>`;
			else if (name && (ipv4 ?? ipv6))
				hint = `${'%h'.format(name)} <span class="hide-xs">(${ipv4 || ipv6})</span>`;
			else
				hint = name || ipv4 || ipv6 || '?';

			let row = [
				E('span', {
					'class': 'ifacebadge',
					'data-ifname': bss.network.getIfname(),
					'data-ssid': bss.network.getSSID()
				}, [
					E('img', {
						'src': L.resource('icons/wifi%s.svg').format(bss.network.isUp() ? '' : '_disabled'),
						'title': bss.radio.getI18n()
					}),
					E('span', [
						` ${bss.network.getShortName()} `,
						E('small', `(${bss.network.getIfname()})`)
					])
				]),
				bss.mac,
				hint,
				render_signal_badge(Math.min((bss.signal + 110) / 70 * 100, 100), bss.signal, bss.noise),
				E('span', {}, [
					E('span', format_wifirate(bss.rx)),
					E('br'),
					E('span', format_wifirate(bss.tx))
				])
			];

			if (bss.vlan) {
				const desc = bss.vlan.getI18n();
				const vlan_network = bss.vlan.getNetwork();
				let vlan_zone;

				if (vlan_network && zones)
					for (let zone of zones)
						if (zone.getNetworks().includes(vlan_network))
							vlan_zone = zone;

				row[0].insertBefore(
					E('div', {
						'class' : 'zonebadge',
						'title' : desc,
						'style' : firewall.getZoneColorStyle(vlan_zone)
					}, [ desc ]), row[0].firstChild);
			}

			if (bss.network.isClientDisconnectSupported()) {
				if (table.firstElementChild.childNodes.length < 6)
					table.firstElementChild.appendChild(E('th', { 'class': 'th cbi-section-actions'}));

				row.push(E('button', {
					'class': 'cbi-button cbi-button-remove',
					'click': L.bind(function(net, mac, ev) {
						dom.parent(ev.currentTarget, '.tr').style.opacity = 0.5;
						ev.currentTarget.classList.add('spinning');
						ev.currentTarget.disabled = true;
						ev.currentTarget.blur();

						net.disconnectClient(mac, true, 5, 60000);
					}, this, bss.network, bss.mac),
					'disabled': isReadonlyView || null
				}, [ _('Disconnect') ]));
			}
			else {
				row.push('-');
			}

			trows.push(row);
		});

		cbi_update_table(table, trows, E('em', _('No information available')));

		return network.flushCache();
	},

	load: function() {
		return Promise.all([
			uci.changes(),
			uci.load('wireless'),
			firewall.getZones()
		]);
	},

	checkAnonymousSections: function() {
		return uci.sections('wireless', 'wifi-iface').some(iface => iface['.anonymous']);
	},

	callUciRename: rpc.declare({
		object: 'uci',
		method: 'rename',
		params: [ 'config', 'section', 'name' ]
	}),

	render: function(data) {
		if (this.checkAnonymousSections())
			return this.renderMigration();
		else
			return this.renderOverview(data[2]);
	},

	handleMigration: function(ev) {
		const wifiIfaces = uci.sections('wireless', 'wifi-iface');
		let id_offset = 0;
		const tasks = [];

		wifiIfaces.forEach((iface) => {
			if (iface['.anonymous']) {
				const new_name = next_free_sid(id_offset);
				tasks.push(this.callUciRename('wireless', iface['.name'], new_name));
				id_offset = parseInt(new_name.substring(7), 10) + 1;
		    }
		});

		return Promise.all(tasks)
			.then(L.bind(ui.changes.init, ui.changes))
			.then(L.bind(ui.changes.apply, ui.changes));
	},

	renderMigration: function() {
		ui.showModal(_('Wireless configuration migration'), [
			E('p', _('The existing wireless configuration needs to be changed for LuCI to function properly.')),
			E('p', _('Upon pressing "Continue", anonymous "wifi-iface" sections will be assigned with a name in the form <em>wifinet#</em> and the network will be restarted to apply the updated configuration.')),
			E('div', { 'class': 'right' },
				E('button', {
					'class': 'btn cbi-button-action important',
					'click': ui.createHandlerFn(this, 'handleMigration')
				}, _('Continue')))
		]);
	},

	renderOverview: function(zones) {
		let m, s, o;

		m = new form.Map('wireless');

		s = m.section(form.GridSection, 'wifi-iface', _('Wireless Overview'));
		s.anonymous = true;
		s.addremove = false;

		s.load = function() {
			return network.getWifiDevices().then(L.bind(function(radios) {
				this.radios = radios.sort(function(a, b) {
					return a.getName() > b.getName();
				});

				const tasks = [];

				radios.forEach(radio => {
					tasks.push(radio.getWifiNetworks());
				});

				return Promise.all(tasks);
			}, this)).then(L.bind(function(data) {
				this.wifis = [];

				data.forEach(d => {
					this.wifis.push.apply(this.wifis, d);
				});
			}, this));
		};

		s.cfgsections = function() {
			return this.wifis.map(wifi => wifi.getName());
		};

		s.modaltitle = function(section_id) {
			const radioNet = this.wifis.filter(function(w) { return w.getName() == section_id; })[0];
			return radioNet ? radioNet.getI18n() : _('Edit wireless network');
		};

		s.lookupNetwork = function(section_id) {
			return this.wifis.filter(function(w) { return w.getName() == section_id; })[0] || null;
		};

		s.renderRowActions = function(section_id) {
			const inst = this.lookupNetwork(section_id);
			if (!inst)
				return E('td', { 'class': 'td middle cbi-section-actions' });

			const isDisabled = (inst.get('disabled') == '1' ||
				uci.get('wireless', inst.getWifiDeviceName(), 'disabled') == '1');

			const btns = [
				E('button', {
					'class': 'cbi-button cbi-button-neutral enable-disable',
					'title': isDisabled ? _('Enable this network') : _('Disable this network'),
					'click': ui.createHandlerFn(this, network_updown, section_id, this.map)
				}, isDisabled ? _('Enable') : _('Disable')),
				E('button', {
					'class': 'cbi-button cbi-button-action important',
					'title': _('Edit this network'),
					'click': ui.createHandlerFn(this, 'renderMoreOptionsModal', section_id)
				}, _('Edit'))
			];

			return E('td', { 'class': 'td middle cbi-section-actions' }, E('div', btns));
		};

		s.addModalOptions = function(s) {
			return network.getWifiNetwork(s.section).then(function(radioNet) {
				const hwtype = uci.get('wireless', radioNet.getWifiDeviceName(), 'type');
				let o;

				o = s.option(form.Value, 'ssid', _('<abbr title="Extended Service Set Identifier">ESSID</abbr>'));
				o.datatype = 'maxlength(32)';

				const crypto_modes = [];
				const is_6ghz = uci.get('wireless', radioNet.getWifiDeviceName(), 'band') == '6g';

				let encr = o = s.option(form.ListValue, 'encryption', _('Encryption'));

				o.cfgvalue = function(section_id) {
					const v = String(uci.get('wireless', section_id, 'encryption'));
					if (v.match(/\+/))
						return v.replace(/\+.+$/, '');
					return v;
				};

				if (hwtype == 'mac80211') {
					const has_supplicant = L.hasSystemFeature('wpasupplicant');
					const has_hostapd = L.hasSystemFeature('hostapd');
					const has_ap_sae = L.hasSystemFeature('hostapd', 'sae');
					const has_sta_sae = L.hasSystemFeature('wpasupplicant', 'sae');

					if (has_hostapd || has_supplicant) {
						if (!is_6ghz)
							crypto_modes.push(['psk2', 'WPA2-PSK', 35]);
					}
					else {
						encr.description = _('WPA-Encryption requires wpa_supplicant (for client mode) or hostapd (for AP and ad-hoc mode) to be installed.');
					}

					if (has_ap_sae || has_sta_sae) {
						crypto_modes.push(['sae', 'WPA3-SAE', 31]);

						if (!is_6ghz)
							crypto_modes.push(['sae-mixed', 'WPA2-PSK/WPA3-SAE Mixed Mode', 30]);
					}
				}
				else if (hwtype == 'broadcom') {
					crypto_modes.push(['psk2', 'WPA2-PSK', 33]);
				}

				if (!is_6ghz)
					crypto_modes.push(['none', _('No Encryption'), 0]);

				crypto_modes.sort(function(a, b) { return b[2] - a[2]; });

				crypto_modes.forEach(crypto_mode => {
					const security_level = (crypto_mode[2] >= 30) ? _('strong security')
						: (crypto_mode[2] >= 20) ? _('medium security')
							: (crypto_mode[2] >= 10) ? _('weak security') : _('open network');

					encr.value(crypto_mode[0], '%s (%s)'.format(crypto_mode[1], security_level));
				});

				o = s.option(form.Value, '_wpa_key', _('Key'));
				add_dependency_permutations(o, { encryption: [ 'psk2', 'sae', 'sae-mixed' ] });
				o.datatype = 'wpakey';
				o.rmempty = true;
				o.password = true;

				o.cfgvalue = function(section_id) {
					const key = uci.get('wireless', section_id, 'key');
					return /^[1234]$/.test(key) ? null : key;
				};

				o.write = function(section_id, value) {
					uci.set('wireless', section_id, 'key', value);
					uci.unset('wireless', section_id, 'key1');
					uci.unset('wireless', section_id, 'key2');
					uci.unset('wireless', section_id, 'key3');
					uci.unset('wireless', section_id, 'key4');
				};
			});
		};

		o = s.option(form.DummyValue, '_badge');
		o.modalonly = false;
		o.textvalue = function(section_id) {
			const inst = this.section.lookupNetwork(section_id);
			const node = E('div', { 'class': 'center' });

			node.appendChild(render_network_badge(inst));

			return node;
		};

		o = s.option(form.DummyValue, '_stat');
		o.modalonly = false;
		o.textvalue = function(section_id) {
			const inst = this.section.lookupNetwork(section_id);

			return render_network_status(inst);
		};

		return m.render().then(L.bind(function(m, nodes) {
			poll.add(L.bind(function() {
				const tasks = [ network.getHostHints(), network.getWifiDevices() ];

				return Promise.all(tasks)
					.then(L.bind(function(hosts_radios) {
						const tasks = [];

						hosts_radios[1].forEach(r => tasks.push(r.getWifiNetworks()) );

						return Promise.all(tasks).then(function(data) {
							hosts_radios[2] = [];

							for (let d of data)
								hosts_radios[2].push.apply(hosts_radios[2], d);

							return hosts_radios;
						});
					}, network))
					.then(L.bind(function(hosts_radios_wifis) {
						const tasks = [];

						hosts_radios_wifis[2].forEach(hrw => tasks.push(hrw.getAssocList()) );

						return Promise.all(tasks).then(function(data) {
							hosts_radios_wifis[3] = [];

							for (let i = 0; i < data.length; i++) {
								const wifiNetwork = hosts_radios_wifis[2][i];
								const radioDev = hosts_radios_wifis[1].filter(function(d) { return d.getName() == wifiNetwork.getWifiDeviceName(); })[0];

								for (let dy of data[i])
									hosts_radios_wifis[3].push(Object.assign({ radio: radioDev, network: wifiNetwork }, dy));
							}

							return hosts_radios_wifis;
						});
					}, network))
					.then(L.bind(function(zones, data) {
						data.push(zones);
						return data;
					}, network, zones))
					.then(L.bind(this.poll_status, this, nodes));
			}, this), 5);

			const table = E('table', { 'class': 'table assoclist', 'id': 'wifi_assoclist_table' }, [
				E('tr', { 'class': 'tr table-titles' }, [
					E('th', { 'class': 'th nowrap' }, _('Network')),
					E('th', { 'class': 'th hide-xs' }, _('MAC address')),
					E('th', { 'class': 'th' }, _('Host')),
					E('th', { 'class': 'th' }, _('Signal / Noise')),
					E('th', { 'class': 'th' }, _('RX Rate / TX Rate'))
				])
			]);

			cbi_update_table(table, [], E('em', { 'class': 'spinning' }, _('Collecting data...')));

			return E([ nodes, E('div', { 'class': 'cbi-section' }, [
				E('h3', _('Associated Stations')),
				table
			]) ]);
		}, this, m));
	},

	handleReset: null
});
