# MTSGO Server

## Présentation

MTSGO est un projet visant à créer une application similaire dans le concept à Pokémon® Go®, où l'objectif est de répondre à des questions dispersées dans le monde.

Le projet se fait dans le cadre d'un projet à Télécom Bretagne comme projet de développement S2.

Le système devra notamment fonctionner avec une API REST-ish fournie par le serveur, que les autres parties devront utiliser pour ajouter et exploiter les données.

Ceci est le repo du bloc __backend__ de l'application serveur MTSGO. Il regroupe la documentation, les spécifications techniques avec le code du projet. Le code source est sous la licence libre.

## Réalisation technique

La spécification se fait avec le langage RAML 1.0 ([Lien](./api) vers l'API Supervision, Lien vers l'API client.)

La réalisation du projet se fait en Python avec le framework Django, les données seront stockées sur MySQL.

## Fonctionnalités

### Première version: v0.1a

L'objectif est d'assurer un fonctionnement minimal du jeu. l'API couvrira:

_Les fonctionnalités précédées par un __[S]__ concernent la supervision du serveur_
- __[S]__ L'ajout et la modification de questions dans le monde.
- Retourner les questions environnantes pour les joueurs.
- Confirmer ou pas la réponse d'un joueur à une question et créditer son score.
- Fournir la carte du monde.
- __[S]__ Fournir des statistiques sur le serveur et le monde.

## Installation

_À terme, le projet devra fournir un script pour l'installation d'une instance du projet_

(à venir)

## Auteurs

François Beugin, Ronan Garet, Ayoub Boudhar.
