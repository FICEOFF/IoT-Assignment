# sv

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli) and [Bun](https://bun.com/).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project
bunx sv create my-app
```

To recreate this project with the same configuration:

```sh
# recreate this project
bun x sv@1.3.0 create --template minimal --no-types --add tailwindcss="plugins:none" sveltekit-adapter="adapter:bun" --install bun Web
```

## Adding features

Add features to your project with `sv add`:

```sh
bunx sv add
```

For example, to add Tailwind CSS:

```sh
bunx sv add tailwindcss
```

## Developing

Once you've created a project and installed dependencies with Bun, start a development server:

```sh
bun install
bun --bun run dev
```

Or start the server and open the app in a new browser tab:

```sh
bun --bun run dev --open
```

## Building

To create a production version of your app:

```sh
bun --bun run build
```

You can preview the production build with:

```sh
bun --bun run preview
```

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment. See the [Bun SvelteKit guide](https://bun.com/guides/ecosystem/sveltekit) for deployment instructions.
