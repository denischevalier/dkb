dkb
===
[Version 0.0.1]

(For english README.md, scroll down the page)

Simple moteur de keybindings pour linux en python.

Attention
---
Ce logiciel est en cours de développement intensif. Les fonctionnalités viendront au fur et à mesure.

Description technique
---
Ce logiciel est codé en python3 orienté objet parallèle. Il utilise peu de dépendances: principalement Xlib, et pillow. dkb est un fork, une simplification (il n'en utilise qu'une infime partie) et une mise à jour de pykeylogger @ http://sourceforge.com/projects/pykeylogger.

Instructions
---
Pour utiliser ce logiciel, entrez simplement `./dkb` dans un terminal, et observez le en action. La touche Scroll_Lock permet de l'arrêter proprement. 

Etat du projet
---
dkb est à présent capable de monitorer tous les évènements clavier du display Xorg sur lequel il est lancé.
Afin de rester dans une philosophie unix, le reste du programme sera dévelopé de manière à piper la sortie de dkb :
Un programme, une fonctionnalité.

Le tout sera encapsulé dans un script shell qui fera le liant entre les différents composants.

A terme, je prévoies (éventuellement) de réécrire les outils en `c` / `c++` :( / `golang`.

______
English
===
Simple keybindings motor for linux, written in python.

Warning
---
This software is under heavy development. Fonctionnalities will comme as soon as they will be developed *(ie. When I'll have some time do do so)*.

Technical description
---
This software is coded in python3 using OOP and Parallelizm. It needs just a few dependancies: mostly xlib, and pillow. dkb is forked, simplified (it uses just a very little subset of the original software) and updated from pykeylogger @ http://sourceforge.com/projects/pykeylogger.

Instructions
---
In order to use this software, you simply have to type `./dkb` on a terminal, and observe it in action. The Scroll_Lock keyboard key permits to stop it properly.

Activity of the project
---
dkb is now able to monitor every keyboard event on its Xorg display. 
In order to stay in the UNIX philosophy, the other parts of the software will be developed so that they would pipe dkb's out: One command, one fonctionnality.

All of that will be encapsulated into a bash script which will link all of its parts.

In the long term, I would rewrite the tools in `c` / `c++` :( / `golang`.
