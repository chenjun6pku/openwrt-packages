'use strict';
'require view';
'require fs';
'require poll';
'require ui';

return view.extend({
    retrieveLog: async function () {
        return Promise.all([
            L.resolveDefault(fs.stat('/usr/libexec/syslog-wrapper'), null),
        ]).then((stat) => {
            const logger = stat[0]?.path;
            return fs.exec_direct(logger).then(logdata => {
                let loglines = logdata.trim().split(/\n/);
                // loglines = loglines
                //     .filter(line => line.includes('minieap'))
                //     .map(line =>
                //         line.replace(
                //             /^[A-Z][a-z]{2} [A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}:\d{2} \d{4} daemon\.info minieap\[\d+\]:\s*/,
                //             ''
                //         )
                //     );
                loglines = loglines.filter(line => line.includes('minieap'));
                return {
                    value: loglines.join('\n'),
                    rows: loglines.length + 1
                };
            }).catch(function (err) {
                ui.addNotification(null, E('p', {}, _('Unable to load log data: ' + err.message)));
                return {
                    value: '',
                    rows: 0
                };
            });
        });
    },

    pollLog: async function () {
        const element = document.getElementById('syslog');
        if (element) {
            const scrollTolerance = 5;
            const isScrolledToBottom = element.scrollHeight - element.scrollTop <= element.clientHeight + scrollTolerance;
            const log = await this.retrieveLog();
            element.value = log.value;
            element.rows = log.rows;
            if (isScrolledToBottom) {
                element.scrollTop = element.scrollHeight;
            }
        }
    },

    load: async function () {
        poll.add(this.pollLog.bind(this));
        return await this.retrieveLog();
    },

    render: function (loglines) {
        setTimeout(() => {
            const element = document.getElementById('syslog');
            if (element) {
                console.log("首次加载页面执行了setTimeout自动滚动到底部");
                element.scrollTop = element.scrollHeight;
            }
        }, 0);
        return E([], [
            E('div', {
                'id': 'content_syslog'
            }, [
                E('textarea', {
                    'id': 'syslog',
                    'style': 'font-family: Consolas; font-size: 15px; width: 100%; height: 69vh;',
                    'readonly': 'readonly',
                    'wrap': 'off',
                    'rows': loglines.rows,
                }, [loglines.value])
            ])
        ]);
    },

    handleSaveApply: null,
    handleSave: null,
    handleReset: null
});