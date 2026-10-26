# Compagnie de l’Hydromel

Trois bots Discord et un tableau de bord web pour animer et administrer un serveur :

- **Barman** : administration, rôles, règlement, messages automatiques et bannière vocale.
- **Archiveuse** : profils, niveaux, smartpoints et classements.
- **Ménestrel** : musique YouTube, SoundCloud et radios, avec commandes Discord et lecteur web.
- **Tableau de bord** : connexion depuis Discord, personnalisation des profils et administration.

## Documentation

La documentation est centralisée dans le **[wiki du projet](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki)**.
Les guides détaillés et leurs mises à jour sont à rédiger dans le wiki.

| Besoin | Guide |
| --- | --- |
| Installer et lancer en local | [Installation](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Installation) |
| Configurer Discord, les secrets et la base | [Configuration](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Configuration) |
| Déployer avec SQLite ou MariaDB | [Déploiement Docker](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Deploiement-Docker) |
| Utiliser le dashboard et les profils | [Guide utilisateur](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Guide-utilisateur) |
| Administrer un serveur | [Administration](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Administration) |
| Gérer les utilisateurs, badges et radios | [Super administration](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Super-administration) |
| Utiliser ou dépanner le lecteur | [Musique](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Musique) |
| Comprendre le code et le bus | [Architecture](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Architecture) · [Communication](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Communication) |
| Retrouver les commandes disponibles | [Commandes](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Commandes) |
| Migrer, sauvegarder et mettre à jour | [Base de données](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Base-de-donnees) · [Exploitation et sauvegardes](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Exploitation-et-sauvegardes) |
| Contribuer et exécuter les vérifications | [Développement](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Developpement) |
| Résoudre un problème | [Dépannage](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Depannage) |

## Fichiers de configuration

- [.env.example](.env.example) : configuration pour l’exécution locale.
- [Dockerfile](Dockerfile) : image commune aux bots et au serveur web.
- [deploy/docker/compose.yml](deploy/docker/compose.yml) : déploiement SQLite.
- [deploy/docker/compose.mariadb.yml](deploy/docker/compose.mariadb.yml) : surcharge MariaDB.
- [deploy/docker/.env.example](deploy/docker/.env.example) : configuration Docker à copier dans `deploy/docker/.env`.

## Licence

[MIT](LICENSE)
