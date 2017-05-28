# MTSGO Server

## Présentation

MTSGO est un projet visant à créer une application similaire dans le concept à Pokémon® Go®, où l'objectif est de répondre à des questions dispersées dans le monde.

Le projet se fait dans le cadre d'un projet à Télécom Bretagne comme projet de développement S2.

Le système devra notamment fonctionner avec une API REST-ish fournie par le serveur, que les autres parties devront utiliser pour ajouter et exploiter les données.

Ceci est le repo du bloc __backend__ de l'application serveur MTSGO. Il regroupe la documentation, les spécifications techniques avec le code du projet. Le code source est sous la licence libre.

La spécification de l'API est faite avec le langage RAML 1.0 ([API Supervision](./api_super), Lien vers l'API client, [API Utilisateurs](./api))

La réalisation du projet se fait en Python avec le framework Django, les données seront stockées sur un backend du choix de l'utilisateur parmis SQLite, MySQL ou PostgreSQL.

Une suite de tests a été écrite pour tester la conformité de la solution à la spécification de l'API, tests qui sont éxecutés automatiquement à chaque modification, et pour les trois logiciels de SGBD mentionnés précédemment.

## Fonctionnalités

### Première version: v0.1a

L'objectif est d'assurer un fonctionnement minimal du jeu. 
- Modèles de questions, instances de questions, zones d'exclusion, et gestion des joueurs.
- Réponse aux questions, geolocking.


## Auteurs

François Beugin, Ronan Garet, Ayoub Boudhar.
