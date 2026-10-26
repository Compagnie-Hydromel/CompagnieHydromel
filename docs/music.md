# Musique du Ménestrel

Le son est **streamé directement** vers Discord par FFmpeg. Aucun morceau n'est
téléchargé ni conservé sur disque : yt-dlp est appelé avec `download=False` pour
résoudre les métadonnées et l'URL du flux. Les URL temporaires sont résolues à
nouveau au moment de lire chaque titre.

## Installation

- Installer les dépendances Python (`pip install -r requirements.txt`), FFmpeg,
  libopus et Node.js 22+ (résolution YouTube). L'image Docker les inclut.
- Pycord 2.8.1 avec ses dépendances vocales assure aussi la prise en charge du
  chiffrement vocal Discord DAVE ; ne pas conserver l'ancienne version 2.6.1.
- Configurer `MENESTREL_TOKEN`, puis démarrer `python3 bot.py menestrel`.
- Avant de redémarrer les services après cette mise à jour, exécuter
  `python3 bot.py migrate` pour créer le catalogue de radios en base de données.
  Docker Compose lance déjà les migrations avec son service `migrate`.
- Pour le web, configurer le [bus WebSocket partagé](communication.md) et démarrer
  également `python3 bot.py webserver`. L'action `menestrel / music.control`
  remplace l'ancien serveur HTTP musical : aucun port 8001 n'est nécessaire.
- Définir des jetons distincts `BUS_WEBSERVER_TOKEN` et `BUS_MENESTREL_TOKEN`.
  Les anciennes variables `MUSIC_CONTROL_*` ne sont plus utilisées.
- En local, `BUS_URL=ws://127.0.0.1:8000/api/internal/bus` ; Docker Compose utilise
  automatiquement `ws://webserver:8000/api/internal/bus`.
- Le bot web doit utiliser un autre token que Ménestrel (Barman par défaut).

## Sources

- **YouTube** : recherche par titre/artiste ou lien YouTube public.
- **SoundCloud** : recherche ou lien public `soundcloud.com`.
- **Radio** : choisir une station dans le catalogue global en base de données.
  Seul le **superadmin** peut ajouter, modifier ou supprimer une station dans
  `/dashboard/superadmin/radios` (nom + URL publique du flux audio direct).
  Les utilisateurs ne peuvent pas saisir d'URL libre depuis le lecteur ou les
  commandes. Le catalogue est actualisé sans redémarrer les bots, y compris
  l'autocomplétion `/radio` sur Discord. La migration initialise FIP, France Inter,
  franceinfo, France Culture, France Musique et Mouv’ une seule fois.
  N'ajouter que des flux et redirections de confiance : FFmpeg s'y connecte
  depuis le réseau du bot. Les URL locales/privées et les identifiants intégrés
  sont refusés. Aucune variable `MUSIC_RADIO_URLS` n'est nécessaire.

Les contenus privés, payants ou protégés par DRM (notamment Spotify/Apple Music)
ne sont pas pris en charge. YouTube et SoundCloud peuvent imposer des limitations
géographiques, anti-bot ou de disponibilité. Mettre yt-dlp à jour si nécessaire.
Seuls les titres individuels sont ajoutés, pas les playlists complètes.

## Contrôles web ET Discord

Le dashboard contient un lecteur compact et `/dashboard/music` affiche le lecteur
complet avec sa file d'attente. Actualisation toutes les 5 secondes.

Sur Discord : `/play search:<titre ou lien> source:<youtube|soundcloud|radio>`,
`/pause`, `/resume`, `/skip`, `/back`, `/stop`, `/queue`, `/now` et les boutons du
lecteur. La source par défaut de `/play` reste YouTube.
Pour les radios, utiliser `/radio station:<choix de la liste>` ou
`/play source:radio search:fip` (identifiant de station, jamais une URL).

Tous pilotent **le même lecteur par serveur**. Pour modifier la lecture, il faut
être dans le même salon vocal classique que le bot (ou dans un salon pour lancer
la première musique). Le bot doit pouvoir voir le salon, s'y connecter et parler.
Le web vérifie l'identité de la session puis le bot vérifie l'appartenance au
serveur, la visibilité et la présence vocale ; aucun ID utilisateur envoyé par
le navigateur n'est accepté.

La file contient au maximum 100 titres. Pause conserve le titre en cours ;
ajouter un titre pendant la pause ne relance pas le lecteur. La fin de file
déconnecte automatiquement le bot. `/stop` vide la file et l'historique.

## Erreurs de lecture

Le lecteur transmet les en-têtes HTTP de yt-dlp à FFmpeg et attend une première
trame audio avant d'annoncer que le titre a démarré. En cas de refus du flux,
il tente une fois le flux **HLS** pour YouTube, plutôt que de reprendre le même
format direct refusé. SoundCloud bénéficie d'une résolution fraîche ; les radios
ne sont pas réessayées automatiquement. Un titre illisible est
ignoré pour essayer le suivant ; si aucun titre ne fonctionne, le bot reste
connecté et le dashboard affiche une erreur. Une fin de file normale continue
de déconnecter le bot. Les URL signées ne sont plus imprimées par FFmpeg.

Un refus YouTube HTTP 403 peut néanmoins persister (restrictions de la source,
de l'adresse IP ou anti-bot). La retransmission des en-têtes et le repli HLS ne garantissent pas
d'accès : essayer alors un autre titre ou une autre source.

Si l'API renvoie `503`, consulter les lignes `Music failure [étape]` du Ménestrel :
elles indiquent le type d'exception et sa pile d'appels, sans les URL signées ni
les secrets. Le message utile est également transmis au lecteur web.
Un client vocal Discord interrompu est nettoyé avant une nouvelle connexion.
Pendant le démarrage du bot web, les lectures de session/serveurs répondent
temporairement `503` avec `Retry-After` ; l'interface réessaie automatiquement.
