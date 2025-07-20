// ----- TOGGLE -----
const btn = document.getElementById('toggle-btn');
let isOn = deviceState['pico/relay'] === 'on';

btn.textContent = isOn ? 'Turn OFF' : 'Turn ON';
btn.dataset.state = isOn ? 'on' : 'off';

btn.addEventListener('click', async () => {
    const newState = isOn ? 'off' : 'on';
    const resp = await fetch('/control-device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            topic: 'pico/relay', value: newState
        })
    });

    if (resp.ok) {
        isOn = !isOn;
        btn.textContent = isOn ? 'Turn OFF' : 'Turn ON';
        btn.dataset.state = isOn ? 'on' : 'off';
    } else {
        alert('Error toggling LED');
    }
});

// ----- SLIDER -----
const slider = document.getElementById('brightness-slider');
const valueLabel = document.getElementById('brightness-value');
let debounceTimer;

const brightness = parseInt(deviceState['pico/led/brightness']) || 50;
console.log(deviceState, deviceState['pico/led/brightness'], { brightness });

slider.value = brightness;
valueLabel.textContent = brightness;

slider.addEventListener('input', () => {
    const value = slider.value;
    valueLabel.textContent = value;

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetch('/control-device', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: 'pico/led/brightness', value: parseInt(value) })
        }).catch(() => console.error('Failed to send brightness'));
    }, 100);
});
