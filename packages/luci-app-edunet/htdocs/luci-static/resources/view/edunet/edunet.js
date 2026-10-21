'use strict';
'require view';
'require form';
'require rpc';
'require ui';
'require poll';
'require tools.widgets as widgets';
'require fs';
'require dom';
const callSetLocaltime = rpc.declare({
	object: 'luci',
	method: 'setLocaltime',
	params: ['localtime']
});

const callServiceList = rpc.declare({
	object: 'service',
	method: 'list',
	params: ['name'],
	expect: { '': {} }
});

const getServiceStatus = async function (serviceName) {
	const res = await L.resolveDefault(callServiceList(serviceName), {});
	return res?.[serviceName]?.instances?.[serviceName]?.running === true;
}

function renderStatus(isRunning) {
	const serviceName = _('EDUNET');
	return E('em', {}, [
		E('span', { 'style': `color:${isRunning ? 'green' : 'red'}` }, [
			E('strong', {}, [
				isRunning
					? `${serviceName} ${_('RUNNING')}`
					: `${serviceName} ${_('NOT RUNNING')}`
			])
		])
	]);
}

return view.extend({
	render: function () {
		let m, s, o, ss, so;

		m = new form.Map('edunet',
			_('EDUNET Client'),
			_('Configure the EDUNET client for 802.1X authentication.')
		);

		s = m.section(form.TypedSection);
		s.anonymous = true;
		s.render = function () {
			const statusContainer = E('p', { 'id': 'service_status' }, E('em', {}, _('Collecting data…')));
			poll.add(async () => {
				const isRunning = await getServiceStatus('edunet');
				console.log('isRunning: ', isRunning);
				dom.content(statusContainer, renderStatus(isRunning));
			});
			return E('div', { 'class': 'cbi-section' }, [statusContainer]);
		};

		s = m.section(form.NamedSection, 'general', 'edunet', _('Client Configuration'));
		s.addremove = false;

		s.tab('auth', _('Auth Setting'));
		s.tab('general', _('General Setting'));
		s.tab('advanced', _('Advanced Setting'));
		s.tab('schedule', _('Schedule Setting'));

		o = s.taboption('auth', form.Flag, 'enabled', _('Enable'));

		// o = s.taboption('auth', form.Flag, 'toggle',
		// 	_('Toggle'),
		// 	_('Toggle this switch and click "Save & Apply" to restart the service if it is enabled but not running.'))
		// o.rmempty = false

		o = s.taboption('auth', form.Value, 'username', _('Username'));
		o.datatype = 'string';
		o.default = 'username';
		o.placeholder = 'username';

		o = s.taboption('auth', form.Value, 'password', _('Password'));
		o.password = true;
		o.default = 'password';
		o.placeholder = 'password';

		o = s.taboption('auth', widgets.NetworkSelect, 'nic', _('Network Interface'));

		o = s.taboption('general', form.Value, 'stage_timeout',
			_('Stage Timeout'),
			_('Timeout for a single authentication stage [Default: 5]'));
		o.datatype = 'uinteger';
		o.placeholder = '5';

		o = s.taboption('general', form.Value, 'wait_after_fail',
			_('Wait After Fail'),
			_('Waiting time before re-authentication after a failure [Default: 30]'));
		o.datatype = 'uinteger';
		o.placeholder = '30';

		o = s.taboption('general', form.Value, 'max_fail',
			_('Max Failures'),
			_('Maximum number of allowed authentication failures [Default: 3]'));
		o.datatype = 'uinteger';
		o.placeholder = '3';

		o = s.taboption('general', form.ListValue, 'no_auto_reauth',
			_('No Auto Reauth'),
			_('Do not allow automatic reconnection after disconnection [Default: True]'));
		o.value('0', _('False'));
		o.value('1', _('True'));
		o.default = '1';

		o = s.taboption('general', form.Value, 'auth_round',
			_('Auth Rounds'),
			_('Number of authentication rounds required [Default: 1]'));
		o.datatype = 'uinteger';
		o.placeholder = '1';	

		o = s.taboption('general', form.Value, 'max_retries',
			_('Max Retries'),
			_('Maximum number of timeout retries [Default: 3]'));
		o.datatype = 'uinteger';
		o.placeholder = '3';
		// o.default = '';

		o = s.taboption('general', form.ListValue, 'if_impl',
			_('Network Module'),
			_('Selects a network module for send and receive packages [Default: sockraw]'));
		o.value('sockraw', _('sockraw'));
		o.default = 'sockraw';

		o = s.taboption('advanced', form.Value, 'heartbeat',
			_('Heartbeat Interval'),
			_('Heartbeat interval in seconds [Default: 60]'));
		o.datatype = 'uinteger';
		o.placeholder = '60';
		// o.default = '';

		o = s.taboption('advanced', form.ListValue, 'eap_bcast_addr',
			_('EAP Broadcast Address'),
			_('Broadcast address for the Start packet [Default: Standard Address]'));
		o.value('0', _('Standard Address'));
		o.value('1', _('Ruijie Private Address'));
		o.default = '0';

		o = s.taboption('advanced', form.ListValue, 'dhcp_type',
			_('DHCP Type'),
			_('DHCP mode: [Default: DHCP After Auth]'));
		o.value('0', _('No DHCP'));
		o.value('1', _('Secondary Auth'));
		o.value('2', _('DHCP Before Auth'));
		o.value('3', _('DHCP After Auth'));
		o.default = '3';

		o = s.taboption('advanced', form.Value, 'dhcp_script',
			_('DHCP Script'),
			_('Script to run during re-authentication or after auth completion [Default: None]'));

		o = s.taboption('advanced', form.DynamicList, 'rj_option',
			_('Custom Ruijie Option'),
			_('Custom authentication field in hexadecimal format [Default: None]'));

		// o = s.taboption('advanced', form.Value, 'service',
		// 	_('Service Name'),
		// 	_('Custom service name for authentication [Default: internet]'));
		// o.optional = true;
		// o.value('internet');
		// o.rmempty = false;

		o = s.taboption('advanced', form.Value, 'version_str',
			_('Version String'),
			_('Custom ruijie client version string [Default: RG-SU For Linux V1.0]'));
		o.placeholder = 'RG-SU For Linux V1.0';

		o = s.taboption('advanced', form.Value, 'max_dhcp_count',
			_('Max DHCP Count'),
			_('Max timeout count for waiting for DHCP result during re-authentication [Default: 3]'));
		o.datatype = 'uinteger';
		o.placeholder = '3'

		o = s.taboption('advanced', form.Value, 'fake_dns1',
			_('Fake Primary DNS'),
			_('Custom primary DNS address (IPv4) [Default: auto-detect]'));
		o.datatype = 'ip4addr';
		// o.default = '';

		o = s.taboption('advanced', form.Value, 'fake_dns2',
			_('Fake Secondary DNS'),
			_('Custom secondary DNS address (IPv4 / IPv6) [Default: auto-detect]'));
		o.datatype = 'ip4addr';
		// o.default = '';

		o = s.taboption('advanced', form.Value, 'fake_serial',
			_('Fake Disk Serial'),
			_('Custom disk serial number [Default: auto-detect]'));
		// o.default = '';

		// TAB SCHEDULE

		o = s.taboption('schedule', form.SectionValue, '__schedule__',
			form.GridSection,
			'schedule',
			null,
			null
			// _('Create automated schedules to start or stop the client.')
		);
		ss = o.subsection;
		ss.addremove = true;
		ss.anonymous = true;
		ss.modaltitle = _('Schedule Configuration');
		ss.nodescriptions = true;

		so = ss.option(form.Flag, 'enabled', _('Enable'));
		so.default = '0'
		so.rmempty = false;
		so.editable = true;

		so = ss.option(form.Value, 'desc',
			_('Description'),
			_('Enter a short description for the schedule')
		);

		so = ss.option(form.Value, 'hour',
			_('Hour'),
			_('Enter the hour for the schedule (Range: 0-23)')
		);
		so.placeholder = '6';
		so.rmempty = false;
		so.datatype = 'range(0,23)';
		// so.validate = function (session_id, value) {
		// 	return (value >= 0 && value <= 23) ? true : _('Range: 0-23');
		// }

		so = ss.option(form.Value, 'minute',
			_('Minute'),
			_('Enter the minute for the schedule (Range: 0-59)')
		);
		so.placeholder = '0';
		so.rmempty = false;
		so.datatype = 'range(0,59)';
		// so.validate = function (session_id, value) {
		// 	return (value >= 0 && value <= 59) ? true : _('Range: 0-59');
		// }

		so = ss.option(form.Value, 'weekday',
			_('Weekday'),
			_("Define on which days the schedule runs, use '*' for everday, '1-5' for a range, '1,3,5' for a list")
		);
		so.rmempty = false;
		so.validate = function (session_id, value) {
			const pattern = /^(?:\*|([1-7](-[1-7])?)(,[1-7](-[1-7])?)*)$/;
			if (pattern.test(value.trim())) {
				return true;
			} else {
				return _('Please enter the correct format');
			}
		}

		so = ss.option(form.ListValue, 'action',
			_('Action'),
			_('Select an action for this scheduled task')
		);
		so.value('0', _('Stop'))
		so.value('1', _('Start'))
		so.textvalue = function (section_id) {
			let v = this.cfgvalue(section_id);
			switch (v) {
				case "0": return _('Stop');
				case "1": return _('Start');
				default: return v;
			}
		};
		return m.render();
	},
	handleSaveApply: async function (ev, mode) {
		try {
			const now = Math.floor(Date.now() / 1000);
			console.log('同步当前时间：', new Date(now * 1000).toLocaleString());
			await this.handleSave(ev);
			await callSetLocaltime(now);
			await ui.changes.apply(mode == '0');
		} catch (err) {
			console.error('Error in handleSaveApply:', err);
			ui.addNotification(null, E('p', _('Error: ') + err.message));
		}
	}
});