<script>
    let { points = [], color = '#0e9f6e', unit = '', digits = 1 } = $props();

    const H = 220;
    const L = 48;
    const R = 14;
    const T = 14;
    const B = 28;

    let W = $state(600);
    let hover = $state(null);

    const view = $derived.by(() => {
        if (points.length === 0) {
            return null;
        }
        const values = points.map((p) => p[1]);
        let lo = Math.min(...values);
        let hi = Math.max(...values);
        if (hi - lo < 1) {
            lo -= 0.5;
            hi += 0.5;
        }
        const pad = (hi - lo) * 0.1;
        return {
            lo: lo - pad,
            hi: hi + pad,
            t0: points[0][0],
            t1: points[points.length - 1][0]
        };
    });

    const x = (t) => L + ((t - view.t0) / (view.t1 - view.t0 || 1)) * (W - L - R);
    const y = (v) => T + ((view.hi - v) / (view.hi - view.lo)) * (H - T - B);

    const path = $derived(
        view
            ? points.map((p, i) => `${i ? 'L' : 'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join('')
            : ''
    );
    const ticks = $derived(
        view ? [0, 1, 2, 3].map((i) => view.lo + ((view.hi - view.lo) * i) / 3) : []
    );
    const showSeconds = $derived(view ? view.t1 - view.t0 < 3600000 : false);
    const picked = $derived(hover !== null && points[hover] ? points[hover] : null);

    function clock(t, seconds) {
        return new Date(t).toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            second: seconds ? '2-digit' : undefined
        });
    }

    function move(e) {
        const rect = e.currentTarget.getBoundingClientRect();
        const px = e.clientX - rect.left;
        let best = 0;
        let gap = Infinity;
        for (let i = 0; i < points.length; i++) {
            const d = Math.abs(x(points[i][0]) - px);
            if (d > gap) {
                break;
            }
            gap = d;
            best = i;
        }
        hover = best;
    }
</script>

<div bind:clientWidth={W} class="overflow-hidden">
{#if view}
    <svg
        width={W}
        height={H}
        class="block touch-pan-y select-none"
        role="img"
        aria-label="History chart"
        onpointermove={move}
        onpointerleave={() => (hover = null)}
    >
        {#each ticks as tick}
            <line x1={L} x2={W - R} y1={y(tick)} y2={y(tick)} stroke="#e5e7eb" />
            <text x={L - 8} y={y(tick) + 4} text-anchor="end" font-size="11" fill="#6b7280">
                {tick.toFixed(digits)}
            </text>
        {/each}
        <text x={L} y={H - 6} font-size="11" fill="#6b7280">{clock(view.t0, showSeconds)}</text>
        <text x={W - R} y={H - 6} text-anchor="end" font-size="11" fill="#6b7280">
            {clock(view.t1, showSeconds)}
        </text>
        <path d={path} fill="none" stroke={color} stroke-width="2" stroke-linejoin="round" />
        {#if points.length === 1}
            <circle cx={x(points[0][0])} cy={y(points[0][1])} r="4" fill={color} />
        {/if}
        {#if picked}
            <line
                x1={x(picked[0])}
                x2={x(picked[0])}
                y1={T}
                y2={H - B}
                stroke="#9ca3af"
                stroke-dasharray="3 3"
            />
            <circle cx={x(picked[0])} cy={y(picked[1])} r="4" fill={color} />
            <text
                x={x(picked[0]) > W / 2 ? x(picked[0]) - 8 : x(picked[0]) + 8}
                y={T + 10}
                text-anchor={x(picked[0]) > W / 2 ? 'end' : 'start'}
                font-size="12"
                fill="#111827"
            >
                {picked[1].toFixed(digits)} {unit} · {clock(picked[0], true)}
            </text>
        {/if}
    </svg>
{:else}
    <div class="flex h-40 items-center justify-center text-gray-400">No data yet</div>
{/if}
</div>
