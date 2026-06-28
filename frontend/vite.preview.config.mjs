// Preview-only Vite config (NOT committed; used by the lms-preview container).
// Runs the dev server with hot-reload and proxies all backend paths to the
// live Frappe backend on the compose network, forcing the Host header to the
// real site name so Frappe resolves the correct site.
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Route backend paths through the FRONTEND nginx container (not gunicorn
// directly): nginx serves /assets + /files static, proxies /api to gunicorn,
// and proxies /socket.io to the websocket service — gunicorn alone 404s on
// static /assets. Reachable by service name on `frappe-net`.
const BACKEND = process.env.PREVIEW_BACKEND || 'http://frontend:8080'
const SOCKETIO = process.env.PREVIEW_SOCKETIO || 'http://frontend:8080'
// Static paths (/assets, /files, /private) MUST go through the frontend nginx,
// which serves them off disk. gunicorn (backend:8000) does NOT serve static
// /assets and returns 404 — so when PREVIEW_BACKEND is set to http://backend:8000
// (as it is in compose.preview.yml), routing /assets to BACKEND 404s every asset.
// Pin static to nginx independently of PREVIEW_BACKEND.
const STATIC = process.env.PREVIEW_STATIC || 'http://frontend:8080'
// Real Frappe site name — sent as Host header so site resolution succeeds.
const SITE = process.env.PREVIEW_SITE || 'frappe.craftspace.space'

const setSiteHost = (proxyReq) => {
	proxyReq.setHeader('Host', SITE)
	proxyReq.setHeader('X-Frappe-Site-Name', SITE)
}

const forceSiteHost = {
	configure: (proxy) => {
		// HTTP requests: /api, /assets, and the socket.io *polling* transport.
		proxy.on('proxyReq', setSiteHost)
		// WebSocket upgrade: the socket.io *websocket* transport. Without this
		// the upgrade reaches the backend with the public Host (lms-preview...),
		// the socketio service can't resolve the site, and closes the connection
		// — "WebSocket is closed before the connection is established" — which
		// then falls back to polling with a dead sid (400 Bad Request).
		proxy.on('proxyReqWs', setSiteHost)
	},
}

// Full proxy map: every backend path -> frontend nginx, with the site Host
// forced. nginx serves /assets+/files static, proxies /api to gunicorn, and
// proxies /socket.io to the websocket service.
const PROXY = {
	// API / app routes -> gunicorn (or whatever PREVIEW_BACKEND points at).
	...Object.fromEntries(
		['/api', '/method', '/app', '/login', '/recorder', '/scorm'].map((p) => [
			p,
			{ target: BACKEND, changeOrigin: false, ...forceSiteHost },
		]),
	),
	// Static routes -> nginx, which serves these off disk (gunicorn 404s them).
	...Object.fromEntries(
		['/assets', '/files', '/private'].map((p) => [
			p,
			{ target: STATIC, changeOrigin: false, ...forceSiteHost },
		]),
	),
	'/socket.io': {
		target: SOCKETIO,
		ws: true,
		changeOrigin: false,
		...forceSiteHost,
	},
}

// The frappe-ui plugin UNCONDITIONALLY injects its own proxy (regex
// ^/(desk|app|login|api|assets|files|private) routed to http://<req-host>:8000)
// even with frappeProxy:false. That collides with /assets and routes it to an
// unreachable host. This post-enforced plugin hard-replaces server.proxy with
// ours after frappe-ui's config() has run.
const overrideProxy = {
	name: 'preview-proxy-override',
	enforce: 'post',
	config(cfg) {
		cfg.server = cfg.server || {}
		cfg.server.proxy = PROXY
	},
}

export default defineConfig(async () => {
	const frappeui = (await import('frappe-ui/vite')).default
	return {
		define: { __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false' },
		plugins: [
			// frappeProxy:false — we define our own proxy below (container needs
			// to target the backend service, not the request host).
			frappeui({
				frappeProxy: false,
				lucideIcons: true,
				jinjaBootData: true,
				buildConfig: { indexHtmlPath: '../lms/www/_lms.html' },
			}),
			vue(),
			overrideProxy,
		],
		resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
		optimizeDeps: {
			// Pre-bundle the heavy chart deps (echarts/zrender) so their hundreds of
			// submodules collapse into a couple of files — otherwise dev serves them
			// raw and the request flood trips ngrok's connection limit (503s).
			// frappe-ui MUST stay excluded: it uses `~icons/*` virtual imports that
			// only resolve via the vite plugin, not the esbuild pre-bundler, so
			// including it crashes dep optimization entirely.
			include: [
				'feather-icons',
				'tailwind.config.js',
				'interactjs',
				'highlight.js',
				'plyr',
				'echarts',
				'zrender',
			],
			exclude: ['frappe-ui'],
		},
		server: {
			host: '0.0.0.0',
			port: 5173,
			allowedHosts: true,
			// Served behind Cloudflare, which STORES `no-cache` responses (then
			// revalidates) and overrides them with a 4h browser TTL — so dev edits
			// never reach the browser. `no-store` tells Cloudflare not to cache at
			// all, keeping the preview live. Applies to every dev response.
			headers: { 'Cache-Control': 'no-store' },
			// Served behind Cloudflare (TLS) + Traefik, so the HMR websocket the
			// browser opens must target the public https port, not :5173.
			hmr: { clientPort: 443, protocol: 'wss' },
			proxy: PROXY,
		},
	}
})
