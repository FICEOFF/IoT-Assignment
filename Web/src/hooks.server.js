import { app } from '#lib/server/api.js';

export function handle({ event, resolve }) {
    if (event.url.pathname.startsWith('/api/')) {
        return app.fetch(event.request);
    }
    return resolve(event);
}
