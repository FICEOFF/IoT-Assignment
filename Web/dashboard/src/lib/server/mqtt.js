import mqtt from 'mqtt';

const PREFIX = '67070164';
const HOST = process.env.MQTT_HOST ?? 'mqtt-dashboard.com';

const TOPIC = {
    rgbSet: `${PREFIX}/rgb/set`,
    rgb: `${PREFIX}/rgb/state`,
    distance: `${PREFIX}/distance`,
    light: `${PREFIX}/light`,
    temperature: `${PREFIX}/temp`,
    humidity: `${PREFIX}/humid`
};

const TEXT_KEYS = ['rgb', 'light'];

const HISTORY_WINDOW = {
    temperature: 24 * 60 * 60 * 1000,
    humidity: 24 * 60 * 60 * 1000
};

export const COLORS = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'white', 'off'];

const store = (globalThis.__iot ??= {
    values: { rgb: null, light: null, distance: null, temperature: null, humidity: null },
    history: { temperature: [], humidity: [] },
    client: null
});

function record(key, value, now, retained) {
    const points = store.history[key];
    if (retained && points.length > 0) {
        return;
    }
    points.push([now, value]);
    const oldest = now - HISTORY_WINDOW[key];
    while (points.length > 0 && points[0][0] < oldest) points.shift();
}

function handle(topic, payload, packet) {
    const key = Object.keys(TOPIC).find((k) => TOPIC[k] === topic);
    const text = payload.toString().trim();
    const value = TEXT_KEYS.includes(key) ? text : Number(text);
    if (Number.isNaN(value)) {
        return;
    }
    const now = Date.now();
    store.values[key] = { value, time: now };
    if (key in HISTORY_WINDOW) {
        record(key, value, now, packet.retain);
    }
}

if (!store.client) {
    store.client = mqtt.connect(`mqtt://${HOST}:1883`, {
        clientId: `${PREFIX}-web-${Math.random().toString(16).slice(2, 8)}`,
        reconnectPeriod: 3000
    });
    store.client.on('connect', () => {
        store.client.subscribe(
            [TOPIC.rgb, TOPIC.distance, TOPIC.light, TOPIC.temperature, TOPIC.humidity],
            { qos: 1 }
        );
    });
    store.client.on('message', handle);
    store.client.on('error', () => {});
}

export function setRgb(color) {
    store.client.publish(TOPIC.rgbSet, color, { qos: 1 });
}

export function getState() {
    const now = Date.now();
    const values = {};
    for (const [key, entry] of Object.entries(store.values)) {
        values[key] = entry && { value: entry.value, age: now - entry.time };
    }
    return { connected: store.client.connected, values };
}

export function getHistory() {
    return store.history;
}
