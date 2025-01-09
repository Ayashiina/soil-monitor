async function loadAlerts() {
    try {
        const [alertsResponse, devicesResponse] = await Promise.all([
            fetch(CONFIG.ALERTS_URL),
            fetch(CONFIG.DEVICES_URL)
        ]);

        if (!alertsResponse.ok) throw new Error('Failed to load alerts');
        if (!devicesResponse.ok) throw new Error('Failed to load devices');

        const alerts = await alertsResponse.json();
        const devices = await devicesResponse.json();

        const deviceMap = devices.reduce((map, device) => {
            map[device.id] = device;
            return map;
        }, {});

        alerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        const alertsTable = document.getElementById('alertsTable');
        alertsTable.innerHTML = '';

        alerts.forEach(alert => {
            const formattedDate = new Date(alert.timestamp).toLocaleDateString('en-GB', {
                weekday: 'short',
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });

            let row = alertsTable.insertRow();
            row.insertCell(0).innerText = deviceMap[alert.device_id]?.name || 'Unknown';
            row.insertCell(1).innerText = deviceMap[alert.device_id]?.location || 'Unknown';
            row.insertCell(2).innerText = formattedDate;
            row.insertCell(3).innerText = alert.status;
        });
    } catch (error) {
        console.error('Error loading alerts:', error);
        alert('Failed to load alerts. Please try again later.');
    }
}

//Reload every 10s
setInterval(loadAlerts, 10000);
window.onload = loadAlerts;
