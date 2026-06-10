graph TD
    A[Benutzer: Eingabe von Name & Passwort] --> B{Frontend: Sende POST /login Request};
    B --> C[Backend: Query DB nach Benutzername];
    C --> D[DB: Sende Benutzerdatensatz mit Hash];
    D --> E[Backend: Berechne Hash des eingegebenen Passworts];
    E --> F[Backend: Vergleiche berechneten Hash mit gespeichertem Hash];
    F --> G{DB: Bestätigung: Hashs übereinstimmen?};

    % Erfolgs-Pfad
    G -- TRUE --> H[Backend: Sende 200 OK mit Auth Token];
    H --> I[Frontend: Speichern Token & Weiterleitung];
    I --> J[Benutzer: Zugriff auf Hauptseite];

    % Fehlers-Pfad
    G -- FALSE --> K[Backend: Sende 401 Unauthorized mit Fehlermeldung];
    K --> L[Frontend: Zeige Fehlermeldung "Ungültige Anmeldedaten"];
    L --> M[Benutzer: Bleibt auf Anmeldebildschirm];
