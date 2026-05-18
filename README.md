# ⛽ TCS Carburant for Home Assistant

Custom Home Assistant integration for Swiss fuel prices using the public **TCS Benzinpreis-Radar** database.

Supports:

- 🇨🇭 Swiss stations
- SP95 / SP98 / Diesel
- Cheapest nearby stations
- Distance from Home Assistant location
- Price freshness / reliability
- Top 3 or Top 10 display
- Station logos
- Google Maps links
- Lovelace dashboard ready

---

## Preview

![Dashboard](images/dashboard.png)

---

## Features

### Fuel types

- SP95
- SP98
- DIESEL

### Sensors

Creates:

```text
sensor.tcs_sp95_moins_cher
sensor.tcs_sp98_moins_cher
sensor.tcs_diesel_moins_cher
```

And ranked sensors:

```text
sensor.tcs_sp95_top_1
sensor.tcs_sp95_top_2
...
sensor.tcs_sp95_top_10
```

Same for:

- SP98
- DIESEL

### Attributes

Each station includes:

- station name
- city
- distance
- reliability
- last update
- Google Maps link
- station logo

---

## Installation (HACS)

### Custom repository

1. Open **HACS**
2. Click the **3 dots** (top right)
3. Select **Custom repositories**
4. Add:

```text
https://github.com/froguinou/hass-tcs-carburant
```

Type:

```text
Integration
```

5. Install
6. Restart Home Assistant

---

## Configuration

Add to `configuration.yaml`:

```yaml
sensor:
  - platform: tcs_carburant
    radius_km: 20
```

---

## Optional Helpers

For the dynamic Lovelace dashboard, add these helpers to your `configuration.yaml`:

```yaml
input_select:
  carburant_tcs:
    name: Carburant TCS
    options:
      - SP95
      - SP98
      - DIESEL
    initial: SP95
    icon: mdi:gas-station

input_boolean:
  carburant_tcs_top10:
    name: Afficher Top 10
    icon: mdi:format-list-numbered
```
Restart Home Assistant after adding them.

---

## Lovelace Example

Requires:

- `flex-table-card`
- `card-mod`

Example dashboard:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Filtres carburant
    entities:
      - entity: input_select.carburant_tcs
      - entity: input_boolean.carburant_tcs_top10
  - type: conditional
    conditions:
      - entity: input_select.carburant_tcs
        state: SP95
      - entity: input_boolean.carburant_tcs_top10
        state: "off"
    card:
      type: custom:flex-table-card
      title: Top 3 SP95
      sort_by: state
      max_rows: 3
      entities:
        include:
          - sensor.tcs_sp95_top_*
      columns:
        - name: Station
          data: station_display
          align: left
        - name: Prix
          data: state
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(3)
            } else {
              ''
            }
          suffix: " CHF/l"
        - name: Km
          data: distance_km
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(1)
            } else {
              ''
            }
        - name: Jours
          data: last_price_update
          align: center
          modify: |-
            if (x) {
              const days = Math.round((Date.now() - Date.parse(x)) / 86400000 * 10) / 10;

              if (days <= 1) {
                '<span style="color:#00ff00;font-weight:bold">' + days + '</span>'
              } else if (days <= 3) {
                '<span style="color:#ffd166;font-weight:bold">' + days + '</span>'
              } else if (days <= 7) {
                '<span style="color:#ff8c42;font-weight:bold">' + days + '</span>'
              } else {
                '<span style="color:#ff4d4d;font-weight:bold">' + days + '</span>'
              }
            } else {
              ''
            }
        - name: Qualité
          data: fiability_level
          align: center
          modify: |-
            if (x === 'CONFIDENT') {
              '<span style="color:#00ff00;font-weight:bold">OK</span>'
            } else if (x === 'FEW_RECENT_PRICES') {
              '<span style="color:#ffd166;font-weight:bold">Moyen</span>'
            } else if (x === 'OLD_LAST_UPDATE') {
              '<span style="color:#ff8c42;font-weight:bold">Vieux</span>'
            } else if (x === 'OUTDATED_LAST_PRICE_UPDATE') {
              '<span style="color:#ff4d4d;font-weight:bold">Très vieux</span>'
            } else {
              x
            }
        - name: Maps
          data: maps_url
          align: center
          modify: |-
            if (x) {
              '<a href="' + x + '" target="_blank">📍</a>'
            } else {
              ''
            }
      css:
        tbody tr:nth-child(odd): "background-color: rgba(255,255,255,0.08)"
        tbody tr:nth-child(even): "background-color: rgba(255,255,255,0.04)"
        tbody tr:nth-child(1): "color: #00ff00; font-weight: bold; font-size: 14px"
        tbody tr:nth-child(2): "color: #8cff8c"
        tbody tr:nth-child(3): "color: #c8ffc8"
        th: "font-weight: bold; color: white; text-align: center"
        td: |
          padding: 4px 6px;
          vertical-align: middle;
        td:nth-child(1): |
          min-width: 170px;
      card_mod:
        style: |
          ha-card {
            border-radius: 14px;
            overflow: hidden;
            font-size: 13px;
          }
  - type: conditional
    conditions:
      - entity: input_select.carburant_tcs
        state: SP95
      - entity: input_boolean.carburant_tcs_top10
        state: "on"
    card:
      type: custom:flex-table-card
      title: Top 10 SP95
      sort_by: state
      entities:
        include:
          - sensor.tcs_sp95_top_*
      columns:
        - name: Station
          data: station_display
          align: left
        - name: Prix
          data: state
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(3)
            } else {
              ''
            }
          suffix: " CHF/l"
        - name: Km
          data: distance_km
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(1)
            } else {
              ''
            }
        - name: Jours
          data: last_price_update
          align: center
          modify: |-
            if (x) {
              const days = Math.round((Date.now() - Date.parse(x)) / 86400000 * 10) / 10;

              if (days <= 1) {
                '<span style="color:#00ff00;font-weight:bold">' + days + '</span>'
              } else if (days <= 3) {
                '<span style="color:#ffd166;font-weight:bold">' + days + '</span>'
              } else if (days <= 7) {
                '<span style="color:#ff8c42;font-weight:bold">' + days + '</span>'
              } else {
                '<span style="color:#ff4d4d;font-weight:bold">' + days + '</span>'
              }
            } else {
              ''
            }
        - name: Qualité
          data: fiability_level
          align: center
          modify: |-
            if (x === 'CONFIDENT') {
              '<span style="color:#00ff00;font-weight:bold">OK</span>'
            } else if (x === 'FEW_RECENT_PRICES') {
              '<span style="color:#ffd166;font-weight:bold">Moyen</span>'
            } else if (x === 'OLD_LAST_UPDATE') {
              '<span style="color:#ff8c42;font-weight:bold">Vieux</span>'
            } else if (x === 'OUTDATED_LAST_PRICE_UPDATE') {
              '<span style="color:#ff4d4d;font-weight:bold">Très vieux</span>'
            } else {
              x
            }
        - name: Maps
          data: maps_url
          align: center
          modify: |-
            if (x) {
              '<a href="' + x + '" target="_blank">📍</a>'
            } else {
              ''
            }
      css:
        tbody tr:nth-child(odd): "background-color: rgba(255,255,255,0.08)"
        tbody tr:nth-child(even): "background-color: rgba(255,255,255,0.04)"
        tbody tr:nth-child(1): "color: #00ff00; font-weight: bold; font-size: 14px"
        tbody tr:nth-child(2): "color: #8cff8c"
        tbody tr:nth-child(3): "color: #c8ffc8"
        th: "font-weight: bold; color: white; text-align: center"
        td: |
          padding: 4px 6px;
          vertical-align: middle;
        td:nth-child(1): |
          min-width: 170px;
      card_mod:
        style: |
          ha-card {
            border-radius: 14px;
            overflow: hidden;
            font-size: 13px;
          }
  - type: conditional
    conditions:
      - entity: input_select.carburant_tcs
        state: SP98
      - entity: input_boolean.carburant_tcs_top10
        state: "off"
    card:
      type: custom:flex-table-card
      title: Top 3 SP98
      sort_by: state
      max_rows: 3
      entities:
        include:
          - sensor.tcs_sp98_top_*
      columns:
        - name: Station
          data: station_display
          align: left
        - name: Prix
          data: state
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(3)
            } else {
              ''
            }
          suffix: " CHF/l"
        - name: Km
          data: distance_km
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(1)
            } else {
              ''
            }
        - name: Jours
          data: last_price_update
          align: center
          modify: |-
            if (x) {
              const days = Math.round((Date.now() - Date.parse(x)) / 86400000 * 10) / 10;

              if (days <= 1) {
                '<span style="color:#00ff00;font-weight:bold">' + days + '</span>'
              } else if (days <= 3) {
                '<span style="color:#ffd166;font-weight:bold">' + days + '</span>'
              } else if (days <= 7) {
                '<span style="color:#ff8c42;font-weight:bold">' + days + '</span>'
              } else {
                '<span style="color:#ff4d4d;font-weight:bold">' + days + '</span>'
              }
            } else {
              ''
            }
        - name: Qualité
          data: fiability_level
          align: center
          modify: |-
            if (x === 'CONFIDENT') {
              '<span style="color:#00ff00;font-weight:bold">OK</span>'
            } else if (x === 'FEW_RECENT_PRICES') {
              '<span style="color:#ffd166;font-weight:bold">Moyen</span>'
            } else if (x === 'OLD_LAST_UPDATE') {
              '<span style="color:#ff8c42;font-weight:bold">Vieux</span>'
            } else if (x === 'OUTDATED_LAST_PRICE_UPDATE') {
              '<span style="color:#ff4d4d;font-weight:bold">Très vieux</span>'
            } else {
              x
            }
        - name: Maps
          data: maps_url
          align: center
          modify: |-
            if (x) {
              '<a href="' + x + '" target="_blank">📍</a>'
            } else {
              ''
            }
      css:
        tbody tr:nth-child(odd): "background-color: rgba(255,255,255,0.08)"
        tbody tr:nth-child(even): "background-color: rgba(255,255,255,0.04)"
        tbody tr:nth-child(1): "color: #00ff00; font-weight: bold; font-size: 14px"
        tbody tr:nth-child(2): "color: #8cff8c"
        tbody tr:nth-child(3): "color: #c8ffc8"
        th: "font-weight: bold; color: white; text-align: center"
        td: |
          padding: 4px 6px;
          vertical-align: middle;
        td:nth-child(1): |
          min-width: 170px;
      card_mod:
        style: |
          ha-card {
            border-radius: 14px;
            overflow: hidden;
            font-size: 13px;
          }
  - type: conditional
    conditions:
      - entity: input_select.carburant_tcs
        state: SP98
      - entity: input_boolean.carburant_tcs_top10
        state: "on"
    card:
      type: custom:flex-table-card
      title: Top 10 SP98
      sort_by: state
      entities:
        include:
          - sensor.tcs_sp98_top_*
      columns:
        - name: Station
          data: station_display
          align: left
        - name: Prix
          data: state
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(3)
            } else {
              ''
            }
          suffix: " CHF/l"
        - name: Km
          data: distance_km
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(1)
            } else {
              ''
            }
        - name: Jours
          data: last_price_update
          align: center
          modify: |-
            if (x) {
              const days = Math.round((Date.now() - Date.parse(x)) / 86400000 * 10) / 10;

              if (days <= 1) {
                '<span style="color:#00ff00;font-weight:bold">' + days + '</span>'
              } else if (days <= 3) {
                '<span style="color:#ffd166;font-weight:bold">' + days + '</span>'
              } else if (days <= 7) {
                '<span style="color:#ff8c42;font-weight:bold">' + days + '</span>'
              } else {
                '<span style="color:#ff4d4d;font-weight:bold">' + days + '</span>'
              }
            } else {
              ''
            }
        - name: Qualité
          data: fiability_level
          align: center
          modify: |-
            if (x === 'CONFIDENT') {
              '<span style="color:#00ff00;font-weight:bold">OK</span>'
            } else if (x === 'FEW_RECENT_PRICES') {
              '<span style="color:#ffd166;font-weight:bold">Moyen</span>'
            } else if (x === 'OLD_LAST_UPDATE') {
              '<span style="color:#ff8c42;font-weight:bold">Vieux</span>'
            } else if (x === 'OUTDATED_LAST_PRICE_UPDATE') {
              '<span style="color:#ff4d4d;font-weight:bold">Très vieux</span>'
            } else {
              x
            }
        - name: Maps
          data: maps_url
          align: center
          modify: |-
            if (x) {
              '<a href="' + x + '" target="_blank">📍</a>'
            } else {
              ''
            }
      css:
        tbody tr:nth-child(odd): "background-color: rgba(255,255,255,0.08)"
        tbody tr:nth-child(even): "background-color: rgba(255,255,255,0.04)"
        tbody tr:nth-child(1): "color: #00ff00; font-weight: bold; font-size: 14px"
        tbody tr:nth-child(2): "color: #8cff8c"
        tbody tr:nth-child(3): "color: #c8ffc8"
        th: "font-weight: bold; color: white; text-align: center"
        td: |
          padding: 4px 6px;
          vertical-align: middle;
        td:nth-child(1): |
          min-width: 170px;
      card_mod:
        style: |
          ha-card {
            border-radius: 14px;
            overflow: hidden;
            font-size: 13px;
          }
  - type: conditional
    conditions:
      - entity: input_select.carburant_tcs
        state: DIESEL
      - entity: input_boolean.carburant_tcs_top10
        state: "off"
    card:
      type: custom:flex-table-card
      title: Top 3 Diesel
      sort_by: state
      max_rows: 3
      entities:
        include:
          - sensor.tcs_diesel_top_*
      columns:
        - name: Station
          data: station_display
          align: left
        - name: Prix
          data: state
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(3)
            } else {
              ''
            }
          suffix: " CHF/l"
        - name: Km
          data: distance_km
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(1)
            } else {
              ''
            }
        - name: Jours
          data: last_price_update
          align: center
          modify: |-
            if (x) {
              const days = Math.round((Date.now() - Date.parse(x)) / 86400000 * 10) / 10;

              if (days <= 1) {
                '<span style="color:#00ff00;font-weight:bold">' + days + '</span>'
              } else if (days <= 3) {
                '<span style="color:#ffd166;font-weight:bold">' + days + '</span>'
              } else if (days <= 7) {
                '<span style="color:#ff8c42;font-weight:bold">' + days + '</span>'
              } else {
                '<span style="color:#ff4d4d;font-weight:bold">' + days + '</span>'
              }
            } else {
              ''
            }
        - name: Qualité
          data: fiability_level
          align: center
          modify: |-
            if (x === 'CONFIDENT') {
              '<span style="color:#00ff00;font-weight:bold">OK</span>'
            } else if (x === 'FEW_RECENT_PRICES') {
              '<span style="color:#ffd166;font-weight:bold">Moyen</span>'
            } else if (x === 'OLD_LAST_UPDATE') {
              '<span style="color:#ff8c42;font-weight:bold">Vieux</span>'
            } else if (x === 'OUTDATED_LAST_PRICE_UPDATE') {
              '<span style="color:#ff4d4d;font-weight:bold">Très vieux</span>'
            } else {
              x
            }
        - name: Maps
          data: maps_url
          align: center
          modify: |-
            if (x) {
              '<a href="' + x + '" target="_blank">📍</a>'
            } else {
              ''
            }
      css:
        tbody tr:nth-child(odd): "background-color: rgba(255,255,255,0.08)"
        tbody tr:nth-child(even): "background-color: rgba(255,255,255,0.04)"
        tbody tr:nth-child(1): "color: #00ff00; font-weight: bold; font-size: 14px"
        tbody tr:nth-child(2): "color: #8cff8c"
        tbody tr:nth-child(3): "color: #c8ffc8"
        th: "font-weight: bold; color: white; text-align: center"
        td: |
          padding: 4px 6px;
          vertical-align: middle;
        td:nth-child(1): |
          min-width: 170px;
      card_mod:
        style: |
          ha-card {
            border-radius: 14px;
            overflow: hidden;
            font-size: 13px;
          }
  - type: conditional
    conditions:
      - entity: input_select.carburant_tcs
        state: DIESEL
      - entity: input_boolean.carburant_tcs_top10
        state: "on"
    card:
      type: custom:flex-table-card
      title: Top 10 Diesel
      sort_by: state
      entities:
        include:
          - sensor.tcs_diesel_top_*
      columns:
        - name: Station
          data: station_display
          align: left
        - name: Prix
          data: state
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(3)
            } else {
              ''
            }
          suffix: " CHF/l"
        - name: Km
          data: distance_km
          align: center
          modify: |-
            if (x) {
              parseFloat(x).toFixed(1)
            } else {
              ''
            }
        - name: Jours
          data: last_price_update
          align: center
          modify: |-
            if (x) {
              const days = Math.round((Date.now() - Date.parse(x)) / 86400000 * 10) / 10;

              if (days <= 1) {
                '<span style="color:#00ff00;font-weight:bold">' + days + '</span>'
              } else if (days <= 3) {
                '<span style="color:#ffd166;font-weight:bold">' + days + '</span>'
              } else if (days <= 7) {
                '<span style="color:#ff8c42;font-weight:bold">' + days + '</span>'
              } else {
                '<span style="color:#ff4d4d;font-weight:bold">' + days + '</span>'
              }
            } else {
              ''
            }
        - name: Qualité
          data: fiability_level
          align: center
          modify: |-
            if (x === 'CONFIDENT') {
              '<span style="color:#00ff00;font-weight:bold">OK</span>'
            } else if (x === 'FEW_RECENT_PRICES') {
              '<span style="color:#ffd166;font-weight:bold">Moyen</span>'
            } else if (x === 'OLD_LAST_UPDATE') {
              '<span style="color:#ff8c42;font-weight:bold">Vieux</span>'
            } else if (x === 'OUTDATED_LAST_PRICE_UPDATE') {
              '<span style="color:#ff4d4d;font-weight:bold">Très vieux</span>'
            } else {
              x
            }
        - name: Maps
          data: maps_url
          align: center
          modify: |-
            if (x) {
              '<a href="' + x + '" target="_blank">📍</a>'
            } else {
              ''
            }
      css:
        tbody tr:nth-child(odd): "background-color: rgba(255,255,255,0.08)"
        tbody tr:nth-child(even): "background-color: rgba(255,255,255,0.04)"
        tbody tr:nth-child(1): "color: #00ff00; font-weight: bold; font-size: 14px"
        tbody tr:nth-child(2): "color: #8cff8c"
        tbody tr:nth-child(3): "color: #c8ffc8"
        th: "font-weight: bold; color: white; text-align: center"
        td: |
          padding: 4px 6px;
          vertical-align: middle;
        td:nth-child(1): |
          min-width: 170px;
      card_mod:
        style: |
          ha-card {
            border-radius: 14px;
            overflow: hidden;
            font-size: 13px;
          }

```

---

## Data source

This integration uses public station data from:

https://benzin.tcs.ch/

Data quality depends on TCS community updates.

---

## Disclaimer

This project is **not affiliated with TCS**.

Fuel prices may be outdated or inaccurate depending on community reporting.