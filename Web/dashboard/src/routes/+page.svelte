<script>
    import Chart from '#lib/Chart.svelte';

    const COLORS = [
        { id: 'red', label: 'Red', hex: '#ef4444' },
        { id: 'yellow', label: 'Yellow', hex: '#facc15' },
        { id: 'green', label: 'Green', hex: '#22c55e' },
        { id: 'cyan', label: 'Cyan', hex: '#06b6d4' },
        { id: 'blue', label: 'Blue', hex: '#2563eb' },
        { id: 'magenta', label: 'Magenta', hex: '#d946ef' },
        { id: 'white', label: 'White', hex: '#ffffff' },
        { id: 'off', label: 'Off', hex: '#1f2937' }
    ];

    let live = $state(null);
    let history = $state({ temperature: [], humidity: [] });
    let offline = $state(false);

    const values = $derived(live?.values ?? {});
    const rgb = $derived(values.rgb?.value ?? null);
    const rgbColor = $derived(COLORS.find((c) => c.id === rgb));
    const distance = $derived(values.distance && values.distance.age < 5000 ? values.distance.value : null);
    const light = $derived(values.light?.value ?? null);
    const temperature = $derived(values.temperature?.value ?? null);
    const humidity = $derived(values.humidity?.value ?? null);

    const STATUS_STYLE = {
        Connected: 'border-green-200 bg-green-50 text-green-700',
        Disconnected: 'border-red-200 bg-red-50 text-red-700',
        Connecting: 'border-gray-200 bg-gray-50 text-gray-600'
    };

    const DOT_STYLE = {
        Connected: 'bg-green-500',
        Disconnected: 'bg-red-500',
        Connecting: 'bg-gray-400'
    };

    const status = $derived(
        offline || (live && !live.connected) ? 'Disconnected' : live ? 'Connected' : 'Connecting'
    );

    async function load() {
        try {
            live = await (await fetch('/api/state')).json();
            offline = false;
        }
        catch {
            offline = true;
        }
    }

    async function loadHistory() {
        try {
            history = await (await fetch('/api/history')).json();
        } 
        catch {}
    }

    async function setRgb(color) {
        try {
            await fetch('/api/rgb', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ color })
            });
            setTimeout(load, 500);
        }
        catch {
            offline = true;
        }
    }

    $effect(() => {
        load();
        loadHistory();
        const fast = setInterval(load, 1000);
        const slow = setInterval(loadHistory, 5000);
        return () => {
            clearInterval(fast);
            clearInterval(slow);
        };
    });
</script>

<main class="mx-auto max-w-5xl px-6 py-10 text-gray-900">
    <header class="flex flex-col items-start gap-3 sm:flex-row sm:justify-between sm:gap-4">
        <div>
            <h1 class="text-4xl font-bold">IoT Dashboard</h1>
            <p class="text-xl mt-1 text-gray-600">Control and monitor the Raspberry Pi and LoRa node</p>
        </div>
        <span
            class="flex shrink-0 items-center gap-2 rounded-full border px-3 py-1 text-sm font-bold whitespace-nowrap {STATUS_STYLE[
                status
            ]}"
        >
            <span class="size-2 rounded-full {DOT_STYLE[status]}"></span>
            MQTT {status}
        </span>
    </header>

    <section class="mt-10">
        <h2 class="text-2xl font-bold">RGB Light</h2>
        <p class="mt-1 text-gray-600">Pick one of 7 colors, or turn the light off</p>

        <div class="mt-4 rounded-xl border border-gray-200 bg-white p-5">
            <div class="flex items-center gap-4">
                <span
                    class="size-12 rounded-full border border-gray-300"
                    style:background={rgbColor?.hex}
                ></span>
                <div>
                    <div class="text-sm text-gray-500">Current status</div>
                    <div class="text-xl font-bold">
                        {#if rgb === null}
                            No data yet
                        {:else if rgb === 'off'}
                            Off
                        {:else}
                            {rgbColor?.label ?? rgb}
                        {/if}
                    </div>
                </div>
            </div>

            <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                {#each COLORS as color (color.id)}
                    <button
                        onclick={() => setRgb(color.id)}
                        class="flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 text-left transition {rgb ===
                        color.id
                            ? 'border-brand bg-brand/10'
                            : 'border-gray-200 hover:bg-gray-50'}"
                    >
                        <span
                            class="size-5 rounded-full border border-gray-300"
                            style:background={color.hex}
                        ></span>
                        {color.label}
                    </button>
                {/each}
            </div>
        </div>
    </section>

    <section class="mt-10">
        <h2 class="text-2xl font-bold">Sensors</h2>
        <p class="mt-1 text-gray-600">Latest values from the Raspberry Pi and LoRa node</p>

        <div class="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div class="rounded-xl border border-gray-200 bg-white p-5">
                <div class="text-sm text-gray-500">Distance</div>
                <div class="mt-2 text-3xl font-bold">
                    {distance ?? '—'}<span class="ml-1 text-base text-gray-500">cm</span>
                </div>
            </div>

            <div class="rounded-xl border border-gray-200 bg-white p-5">
                <div class="text-sm text-gray-500">Light</div>
                <div class="mt-3">
                    {#if light === 'bright'}
                        <span class="rounded-full bg-amber-100 px-4 py-1 text-lg font-bold text-amber-700">
                            ☀️ Day
                        </span>
                    {:else if light === 'dark'}
                        <span class="rounded-full bg-slate-800 px-4 py-1 text-lg font-bold text-white">
                            🌙 Night
                        </span>
                    {:else}
                        <span class="text-3xl font-bold">—</span>
                    {/if}
                </div>
            </div>

            <div class="rounded-xl border border-gray-200 bg-white p-5">
                <div class="text-sm text-gray-500">Temperature</div>
                <div class="mt-2 text-3xl font-bold">
                    {temperature ?? '—'}<span class="ml-1 text-base text-gray-500">°C</span>
                </div>
            </div>

            <div class="rounded-xl border border-gray-200 bg-white p-5">
                <div class="text-sm text-gray-500">Humidity</div>
                <div class="mt-2 text-3xl font-bold">
                    {humidity ?? '—'}<span class="ml-1 text-base text-gray-500">%RH</span>
                </div>
            </div>
        </div>
    </section>

    <section class="mt-10">
        <h2 class="text-2xl font-bold">History</h2>
        <p class="mt-1 text-gray-600">Hover or tap a chart to see the value at that time</p>

        <div class="mt-4 grid gap-4 lg:grid-cols-2">
            <div class="min-w-0 rounded-xl border border-gray-200 bg-white p-5">
                <h3 class="mb-3 font-bold">Temperature (°C)</h3>
                <Chart points={history.temperature} color="#f97316" unit="°C" />
            </div>
            <div class="min-w-0 rounded-xl border border-gray-200 bg-white p-5">
                <h3 class="mb-3 font-bold">Humidity (%RH)</h3>
                <Chart points={history.humidity} color="#06b6d4" unit="%RH" />
            </div>
        </div>
    </section>
</main>
