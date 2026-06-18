# PlantLover — Home Assistant Integration

Integracja do [PlantLover](https://github.com/lukaszgdk/plantlover-ha) — aplikacji do zarządzania roślinami domowymi.

## Funkcje

- Sensory dla każdej rośliny: ostatnie podlanie, następne podlanie, dni do podlania
- Przycisk **Podlej** dla każdej rośliny
- Automatyczne odświeżanie co 5 minut

## Instalacja przez HACS

1. W HACS → **Custom repositories** → dodaj `https://github.com/lukaszgdk/plantlover-ha` jako **Integration**
2. Znajdź **PlantLover** w HACS i zainstaluj
3. Uruchom ponownie Home Assistant
4. Ustawienia → Urządzenia i usługi → **Dodaj integrację** → PlantLover
5. Podaj adres URL swojej aplikacji PlantLover (np. `http://10.10.30.270`)

## Dashboard Lovelace

W repozytorium znajduje się gotowy plik `dashboard.yaml`.

**Opcja A — auto-entities (automatyczny, zawsze aktualny):**

1. Zainstaluj w HACS frontend: [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
2. W HA: Ustawienia → Dashboardy → Dodaj dashboard → z pliku YAML → wklej treść `dashboard.yaml`

**Opcja B — spersonalizowany YAML z dokładnymi encjami:**

```bash
GET http://<adres-plantlover>/api/plants/ha-dashboard
```

Endpoint generuje YAML z encjami dla każdej Twojej rośliny. Skopiuj odpowiedź do HA.

## Wymagania

- Działająca instancja [PlantLover](https://github.com/lukaszgdk/plantlover)
- Home Assistant 2023.1+
