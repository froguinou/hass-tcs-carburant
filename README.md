# TCS Carburant

Custom integration Home Assistant pour afficher les prix des carburants suisses depuis le service TCS https://benzin.tcs.ch.

## Fonctionnalités

- Prix SP95, SP98 et Diesel
- Top 3 ou Top 10 stations les moins chères
- Distance depuis la position Home Assistant
- Dernière mise à jour du prix
- Niveau de fiabilité
- Lien Google Maps
- Compatible Lovelace avec flex-table-card

## Installation via HACS

1. Ouvrir HACS
2. Aller dans les trois points en haut à droite
3. Choisir Custom repositories
4. Ajouter l’URL du repo GitHub
5. Type : Integration
6. Installer l’intégration
7. Redémarrer Home Assistant

## Configuration YAML

```yaml
sensor:
  - platform: tcs_carburant
    radius_km: 20