# Visualisation et navigation dans une image très haute définition

Projet qui vise à permettre une navigation agréable et ergonomique dans des images très haute définition via le lancement d'un script python.

## Pour commencer

Ces instructions permettent d'effectuer une copie du projet et de faire tourner le script sur votre machine locale, à des fins de test.

### Prérequis

Installer Python si ce n'est pas déjà fait (Ici nous utilisons la version 3).

Créer un chemin vers Python dans les variables d'environnement afin de pouvoir appeler le langage depuis le terminal.

Créer un dossier dans lequel le script ainsi que toutes les photos, préalablement regroupées dans un autre dossier, seront déposées. 


## Lancer l'algorithme

Commandes à taper dans le terminal afin de lancer le script:

2 cas ont été pris en compte: le cas où l'on commence l'étude de l'image et le cas où l'on souhaite reprendre l'étude d'une zone précise entamée précédemment.

**1er cas**: Partir de l'image la plus générique qui possède la plus faible résolution

```
python show.py 8192 nomdudossiercontenantlesimages/
```

**2ème cas**: Partir d'une position préalablement enregistrée et continuer une étude

```
python show.py peuimporte nomdudossiercontenantlesimages/ "SauvegardePosition.txt"
```


## Authors
Antoine HURARD & Andrianirina RAKOTOHARISOA
