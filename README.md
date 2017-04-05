# MTSGO Server
![Build Status](https://api.travis-ci.com/aneutron/mtsgo-server.svg?token=wgWk1dajYyv8wpbcqiyk&branch=dev-alpha)

## Présentation

Ceci est le repo du bloc serveur de l'application MTSGO. Il regroupe la documentation, les spécifications techniques et les diagrammes UML qui ont été utilisés pour ce bloc. Le code source est sous la licence X.

## Dépendences

Le projet dépend des librairies:
- Django (1.10): Framework de base pour le projet
- django-tokenapi (0.2.5): Librairie pour l'authentification
- matplotlib (1.5.3): Utilisé pour résoudre le problème _point in polygon_.
- pymysql (0.7.10): Le driver classique MySQLdb ne marche pas sur Python 3 pour le moment, c'est pourquoi cet alternative est utilisée. (Elle est installée comme si elle était MySQLdb)

## Installation

D'abord installez les dépendances (Préférablement dans un __environnement virtuel__ pour éviter les conflits de dépendances):

`pip install django==1.10 django-tokenapi==0.2.5 matplotlib==1.5.3 pymysql==0.7.10`

Puis positionnez vous dans le dossier que vous souhaitez, et cloner le projet:

`git clone https://github.com/aneutron/mtsgo-server`

Modifiez les paramètres de votre application à présent dans `mtsgo-server/mtsgo/settings.py`, ensuite appliquez les migrations à votre BDD avec `python mtsgo-server/manage.py makemigrations` puis `python mtsgo-server/manage.py migrate`, et lancez le serveur test de django en utilisant `python mtsgo-server/manage.py runserver`.

## Auteurs

François Beugin, Ronan Garet, Ayoub Boudhar.
