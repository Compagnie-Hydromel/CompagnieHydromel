# Bus de communication WebSocket

Le serveur web héberge **un seul bus partagé** sur `/api/internal/bus`. Barman,
Ménestrel, Archiveuse et le serveur web possèdent chacun un client. Aucun broker
MQTT, Redis ou serveur HTTP par fonctionnalité n'est nécessaire.

## Configuration et migration

Dans `.env`, remplacer les anciennes variables `MUSIC_CONTROL_*` par :

```dotenv
BUS_URL=ws://127.0.0.1:8000/api/internal/bus
BUS_WEBSERVER_TOKEN=un-secret-aleatoire-pour-le-web
BUS_BARMAN_TOKEN=un-autre-secret-pour-barman
BUS_MENESTREL_TOKEN=un-autre-secret-pour-menestrel
BUS_ARCHIVEUSE_TOKEN=un-autre-secret-pour-archiveuse
```

Générer **chaque** jeton séparément avec `openssl rand -hex 32` (les valeurs
ci-dessus sont des exemples). Ce sont des secrets internes, pas les tokens Discord.
Le hub doit connaître les jetons de tous les composants. Chaque composant a besoin
uniquement de son propre jeton ; si tous utilisent le même `.env`, ce fichier
doit donc être réservé à des processus de confiance. Ne jamais transmettre ces
jetons au navigateur. Les sessions web ne donnent aucun accès direct au bus.

Sans son `BUS_<COMPOSANT>_TOKEN`, un composant continue à fonctionner sans bus ;
le contrôle musical web renvoie alors `503`. Les commandes Discord restent disponibles.
Le serveur web doit être démarré pour toute communication inter-composants.
`python3 bot.py start` lance déjà les quatre services ; l'ordre n'est pas important
car les clients se reconnectent automatiquement.

Docker Compose fournit `BUS_URL=ws://webserver:8000/api/internal/bus`. Aucun port
supplémentaire n'est publié. Bloquer ce chemin dans le reverse proxy public.
Sur plusieurs machines, utiliser un réseau privé ou **WSS** : les connexions WS
simples ne chiffrent pas les jetons ni les messages. Ne pas désactiver la validation
TLS. Les secrets ne doivent pas être placés dans l'URL.

Pour ajouter un composant, étendre `BUS_COMPONENTS` (par défaut
`webserver,barman,menestrel,archiveuse`), définir son `BUS_<NOM>_TOKEN` côté hub,
puis utiliser `ComponentBus.from_env("nom")`. Les noms sont en minuscules ; points
et tirets deviennent des underscores dans le nom de variable du jeton.

## Exposer et appeler une action

Dans un cog Barman, par exemple :

```python
from libs.communication import BusError

async def guild_summary(payload, context):
    # L'identité vient de la connexion authentifiée, pas du payload.
    guild = bot.get_guild(int(payload["guild_id"]))
    if guild is None:
        raise BusError("Serveur introuvable", code="not_found", status=404)
    return {"name": guild.name, "member_count": guild.member_count}

bus = bot.component_bus
if bus:
    bus.register("guild.summary", guild_summary, callers={"webserver", "archiveuse"})
```

Dans un autre composant :

```python
from libs.communication import BusError

summary = await bot.component_bus.call(
    "barman", "guild.summary", {"guild_id": "123456789"}, timeout=10
)
```

Le client est accessible via `bot.component_bus` dans les bots et
`request.app.state.component_bus` dans les contrôleurs web. Côté web, la même
méthode `register` permet aussi d'exposer des actions (dans le lifespan de l'app).
`bus.unregister("guild.summary")` retire une action, notamment lors du déchargement
d'un cog. L'enregistrement et ses permissions sont actualisés sans reconnexion.

Seules les fonctions **explicitement enregistrées** sont accessibles. Le hub
vérifie les appelants autorisés, puis le composant destinataire vérifie à nouveau
ces permissions. Le code de la fonction reste responsable des permissions métier
(utilisateur, serveur Discord, salon vocal…). L'action musicale `music.control`
est réservée à `webserver` et conserve les contrôles de session et de présence
vocale existants. Aucun nom de fonction Python arbitraire ne peut être invoqué.

Les fonctions reçoivent `(payload, context)` et retournent des données JSON.
Elles peuvent être synchrones ou asynchrones. Elles s'exécutent sur la boucle
du composant, ce qui préserve les connexions SQLite de MIWOS. Ne déporter que les
opérations réseau/CPU bloquantes avec `asyncio.to_thread`, **pas les accès SQLite**.

Chaque composant expose aussi `system.ping` aux autres composants configurés,
pour tester la communication sans dépendre de la disponibilité de Discord.

## Événements

```python
async def on_music_changed(payload, context):
    print(context.caller, payload["guild_id"])

web_bus.on("menestrel.music.changed", on_music_changed)
await menestrel_bus.publish("music.changed", {"guild_id": "123456789"})
web_bus.off("menestrel.music.changed", on_music_changed)
```

Le client ajoute automatiquement son nom comme préfixe de publication. Un
composant ne peut pas publier au nom d'un autre. Les abonnements correspondent
à des noms exacts, sans wildcard, et sont rétablis à la reconnexion. Les événements
sont internes, visibles aux composants authentifiés abonnés : ne pas y inclure
de secrets ou de données personnelles inutiles. L'exemple ci-dessus montre comment
ajouter une notification ; le dashboard musical conserve actuellement son polling HTTP.

## Garanties et limites

- Identité liée à un jeton distinct, une connexion active par composant.
- Corrélation des réponses, appels simultanés et erreurs structurées `BusError`.
- Délai par appel de 30 secondes par défaut, 120 maximum (musique : 90 secondes).
- Déconnexion : les appels en cours échouent immédiatement, sans être rejoués.
  Cela évite de relancer automatiquement une action comme « ajouter un titre ».
- Annulation et timeout : le handler distant est annulé, mais les effets déjà
  effectués ne sont pas annulés. Ce n'est **pas** une garantie « exactement une fois ».
- Reconnexion avec heartbeat et backoff, réenregistrement des actions/abonnements.
- Événements best-effort : pas de stockage, de rejeu ni d'accusé de traitement ;
  `publish` renvoie `False` lorsque le client est déconnecté.
- Messages JSON de 256 Kio maximum, 64 appels en cours par client, travail des
  handlers borné. Aucune sérialisation pickle ni exécution de code à distance.
- Arrêt : fermeture des sockets, annulation des handlers et nettoyage des appels
  en attente. Le client doit être fermé avec `await bus.close()`.

Le bus est un point central : si le serveur web est arrêté, les bots restent
utilisables via Discord, mais leurs échanges attendront une nouvelle connexion.
