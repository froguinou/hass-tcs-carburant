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
      columns: &columns
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
              '<span style="opacity:0.6">' + x + '</span>'
            }
      css: &css
        tbody tr:nth-child(odd): "background-color: rgba(255,255,255,0.08)"
        tbody tr:nth-child(even): "background-color: rgba(255,255,255,0.04)"
        tbody tr:nth-child(1): "color: #00ff00; font-weight: bold"
        tbody tr:nth-child(2): "color: #8cff8c"
        tbody tr:nth-child(3): "color: #c8ffc8"
        th: "font-weight: bold; color: white; text-align: center"
        td: "padding: 7px 5px; vertical-align: middle"
        td:nth-child(1): "width: 58%; min-width: 210px"
        td:nth-child(2): "width: 17%; font-size: 15px; font-weight: bold"
        td:nth-child(3): "width: 10%; font-weight: bold"
        td:nth-child(4): "width: 15%; font-weight: bold"
      card_mod: &cardmod
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
      columns: *columns
      css: *css
      card_mod: *cardmod

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
      columns: *columns
      css: *css
      card_mod: *cardmod

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
      columns: *columns
      css: *css
      card_mod: *cardmod

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
      columns: *columns
      css: *css
      card_mod: *cardmod

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
      columns: *columns
      css: *css
      card_mod: *cardmod