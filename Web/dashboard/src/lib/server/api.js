import { Hono } from 'hono';
import { COLORS, setRgb, getState, getHistory } from '#lib/server/mqtt.js';

export const app = new Hono().basePath('/api');

app.get('/state', (c) => {
    return c.json(getState());
});

app.get('/history', (c) => {
    return c.json(getHistory());
});

app.post('/rgb', async (c) => {
    const { color } = await c.req.json().catch(() => ({}));
    if (!COLORS.includes(color)) {
        return c.json({ error: 'Invalid color' }, 400);
    }
    setRgb(color);
    return c.json({ ok: true });
});
