async function addDevice() {
    const deviceName = document.getElementById("deviceName").value;
    const deviceLocation = document.getElementById("deviceLocation").value;

    if (!deviceName || !deviceLocation) {
        alert("Please fill in both the device name and location.");
        return;
    }

    try {
        const response = await fetch(CONFIG.ADD_DEVICES_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: deviceName,
                location: deviceLocation,
            }),
        });

        const result = await response.json();
        alert(result.message);

        if (response.ok) {
            fetchDevices();
        }
    } catch (error) {
        console.error("Error adding device:", error);
        alert("Failed to add the device. Please try again.");
    }
}

async function fetchDevices() {
    try {
        const response = await fetch(CONFIG.DEVICES_URL);
        if (!response.ok) throw new Error("Failed to fetch devices.");

        const devices = await response.json();
        const deviceList = document.getElementById("deviceList");
        deviceList.innerHTML = "";  

        devices.forEach(device => {
            const listItem = document.createElement("li");
            listItem.textContent = `${device.name} - ${device.location} `;

            const toggleButton = document.createElement("button");
            toggleButton.classList.add("toggle-button");
            toggleButton.classList.add(device.is_active ? "active" : "inactive");

            toggleButton.innerHTML = device.is_active ? '<i class="fas fa-power-off"></i>' : '<i class="fas fa-power-off"></i>';
            toggleButton.onclick = () => toggleDevice(device.id, toggleButton);

            listItem.appendChild(toggleButton);
            deviceList.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error fetching devices:", error);
        alert("Failed to load devices. Please try again.");
    }
}

async function toggleDevice(deviceId, button) {
    try {
        const newState = button.classList.contains("inactive"); 
        const action = newState ? "start" : "stop";  

        const response = await fetch(CONFIG.MONITORING_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ action: action, deviceId: deviceId })  
        });

        if (!response.ok) throw new Error("Failed to toggle device.");

        button.classList.toggle("active", newState);
        button.classList.toggle("inactive", !newState);
    } catch (error) {
        console.error("Error toggling device:", error);
        alert("Failed to update device state. Please try again.");
    }
}


document.addEventListener("DOMContentLoaded", fetchDevices);