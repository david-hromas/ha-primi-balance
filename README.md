# Primi Balance

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for monitoring your account balance(s) on [primiapp.cz](https://primiapp.cz) (Primirest).

## Features

- Logs in to your `primiapp.cz` account and discovers all available scopes/roles (e.g. organizations, family members) linked to your login.
- Creates one sensor entity per scope, exposing the current account balance and currency.
- Fires a `primi_balance_low` event on the Home Assistant event bus whenever a balance drops below a configurable threshold, so you can trigger automations (notifications, etc.).
- Configurable polling interval and low-balance threshold, adjustable at any time via the integration's **Options**.

## Installation

### HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. In Home Assistant, go to **HACS → Integrations → ⋮ → Custom repositories**.
3. Add this repository URL with category **Integration**.
4. Find **Primi Balance** in HACS and click **Download**.
5. Restart Home Assistant.

### Manual

1. Copy the `primi_balance` folder into your Home Assistant `config/custom_components/` directory, so that it ends up at `config/custom_components/primi_balance/`.
2. Restart Home Assistant.

## Configuration

Configuration is done entirely through the UI:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Primi Balance**.
3. Enter your `primiapp.cz` username and password.
4. Optionally set:
   - **Low balance threshold** — the balance value below which the `primi_balance_low` event is fired (default: `100`).
   - **Update interval** — how often (in minutes) the integration polls for new balance data (default: `60`).

You can change the threshold and update interval at any time via the integration's **Configure** (Options) button.

## Entities

For each scope/role associated with your account, a sensor is created:

- **State**: current account balance (numeric).
- **Attributes**:
  - `currency` — the currency of the balance (e.g. `CZK`).
  - `low_balance` — `true`/`false` depending on whether the balance is under the configured threshold.

## Events

| Event | Description |
|---|---|
| `primi_balance_low` | Fired when a scope's balance drops below the configured threshold. Event data includes `name`, `balance`, `currency`, and `threshold`. |

Example automation trigger:

```yaml
trigger:
  - platform: event
    event_type: primi_balance_low
condition: []
action:
  - service: notify.notify
    data:
      title: "Low Primi Balance"
      message: >
        {{ trigger.event.data.name }} balance is
        {{ trigger.event.data.balance }} {{ trigger.event.data.currency }}
        (threshold: {{ trigger.event.data.threshold }})
```

## Supported Languages

- English
- Čeština (Czech)
- Slovenčina (Slovak)

## Disclaimer

This is an unofficial, community-maintained integration and is not affiliated with or endorsed by Primirest or primiapp.cz.

## Contributing

Issues and pull requests are welcome. Please open an issue describing the bug or feature request before submitting a PR.

## License

See [LICENSE](LICENSE) for details.
