# Browser runtime

`PlaywrightBrowserBackend` requires the Playwright Python package, a matching
Chromium download, Chromium system libraries, and a usable network egress path.
None of these details are exposed to the Researcher model.

## Prerequisites

Install Playwright and Chromium in the application environment, then provision
the official host dependencies:

```bash
python -m playwright install chromium
playwright install-deps chromium
```

The second command may require administrator privileges. Deployment images
should install dependencies during image construction instead of at request
time.

When system packages cannot be installed, the runtime can automatically supply
the current Python environment's `lib/` directory to the Chromium child process
if all required NSPR, NSS, and ALSA libraries are present there. This fallback is
child-process scoped: it does not globally export `LD_LIBRARY_PATH`, is not a
Browser business setting, and should not replace proper deployment provisioning.

Dependency resolution therefore has three explicit outcomes:

1. System libraries resolve: launch Chromium normally.
2. System libraries are missing but the active Python environment contains the
   complete library set: add that environment's `lib/` only to the Chromium
   child process.
3. Neither location is complete: fail before launch with a dependency error and
   an instruction to run `playwright install-deps chromium` during deployment.

## Network modes

The typed Browser configuration supports:

- `inherit` (default): resolve the first configured host proxy in
  `HTTPS_PROXY`, `https_proxy`, `HTTP_PROXY`, `http_proxy` order and explicitly
  adapt it to Playwright. `NO_PROXY` or `no_proxy` becomes Playwright bypass.
  With no proxy, this behaves like direct network access.
- `direct`: ignore all host proxy variables and do not pass a proxy to Chromium.

Proxy credentials stay in the host environment and must never be committed.
Runtime summaries expose only whether a proxy, credentials, and bypass are
configured; they do not expose the proxy URI or credentials.

The Browser public-URL validation runs before navigation and continues to reject
userinfo, localhost, private addresses, local addresses, and non-HTTP(S)
schemes. A proxy does not relax this SSRF boundary.

## Zero-model preflight

Run before any model-backed experiment:

```bash
PYTHONPATH=backend/src python -m \
  novelty_agent_framework.diagnostics.browser_preflight \
  --network-mode inherit \
  --output outputs/experiments/Browser_Runtime_Repair/preflight.json
```

The preflight checks Playwright import, Chromium availability and launch,
context/page creation, local HTML rendering, sanitized network resolution, and
a public static-page fetch. It makes zero model API calls and classifies failures
as dependency, launch, network configuration, navigation, or content errors.
