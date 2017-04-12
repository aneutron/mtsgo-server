# MTSGO Server
![Build Status](https://travis-ci.org/aneutron/mtsgo-server.svg?branch=master)
![Code Coverage](https://codecov.io/github/aneutron/mtsgo-server/coverage.svg?branch=master)

## Présentation

Ceci est le repo du bloc serveur de l'application MTSGO. Il regroupe le code, la documentation, et les spécifications techniques.

## Dépendences

Pour le moment, le développement se fait avec Python 3, et est testé avec les versions 3.5 et 3.6. _(Des efforts sont en cours pour étudier la portabilité de la solution à Python 2.7)_

Le projet dépend des librairies:
- Django (1.10): Framework de base pour le projet
- django-tokenapi (0.2.5): Librairie pour l'authentification
- matplotlib (1.5.3): Utilisé pour résoudre le problème _point in polygon_.
- pymysql (0.7.10): Si vous voulez utiliser MySQL, Le driver classique MySQLdb ne marche pas sur Python 3 pour le moment, c'est pourquoi cet alternative est utilisée. (Elle peut être installée comme si elle était MySQLdb) 

_(En théorie, la solution ne dépends pas d'une fonctionnalité particulière d'un SGBD, donc tant que Django supporte cette back-end, il y a à priori moyen de l'utiliser)_

## Installation
D'abord positionnez vous dans le dossier que vous souhaitez, et cloner le projet:

`git clone https://github.com/aneutron/mtsgo-server`

Ensuite installez les dépendances _(Préférablement dans un __environnement virtuel__ pour éviter les conflits de dépendances)_:

`pip install -r requirements.txt`

Eventuellement modifiez les paramètres dans `mtsgo/settings.py`, ensuite appliquez les schémas à votre BDD avec `python mtsgo-server/manage.py makemigrations` puis `python mtsgo-server/manage.py migrate`.

Pour lancer votre serveur de test, éxecutez:

`python manage.py runserver`

Vous pouvez bien évidemment l'installer comme application uWSGI derrière Apache ou Nginx. Un autre guide viendra après.


## Code coverage & Tests

Pour tester la conformité à la spécification de l'API, et assurer une qualité du code assez correcte, des tests ont été écrit pour chaque API
_(mtsgo/test.py, api/test.py, superapi/test.py)_ , et sont lancés automatiquement à chaque _commit_, et des statistiques de code coverage sont générés.

Vous pouvez visiter [la page du projet](https://travis-ci.org/aneutron/mtsgo-server/) sur la plateforme d'intégration continue TravisCI, et aussi [la page du projet](https://codecov.io/gh/aneutron/mtsgo-server/) sur la plateforme de statistiques de code coverage CodeCov.io .

Voici un des graphes montrant la couverture avec l'arborescence du projet:
![Code Coverage Tree](https://codecov.io/gh/aneutron/mtsgo-server/branch/master/graphs/icicle.svg)

## Auteurs

François Beugin, Ronan Garet, Ayoub Boudhar.
