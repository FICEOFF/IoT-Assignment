<script>
    import './layout.css';

    let { children } = $props();
</script>

<svelte:head>
    <title>IoT Dashboard</title>
    <link rel="icon" href="/assets/favicon.svg" />
</svelte:head>

{@render children()}
