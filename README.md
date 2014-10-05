dkb
===
(For english, please scroll down the page)

Simple moteur de keybindings pour linux en python.

Attention
---
La version 0.2.2 a été publiée. A voir sur la page release.

Description technique
---
Ce logiciel est codé en python3 orienté objet parallèle. Sa seule dépendance est xlib. dkb utilise pyxhook (présent dans le repos), ainsi qu'une infime partie de pykeylogger @ http://sourceforge.com/projects/pykeylogger.

Instructions
---
Pour utiliser ce logiciel, modifiez le fichier config_example.json, puis entrez `./dkb` dans un terminal. Vos raccourcis claviers sont maintenant accessible dans toute votre session xorg. La touche Scroll_Lock permet de l'arrêter proprement. 

Etat du projet
---
dkb est à présent capable de monitorer tous les évènements clavier du display Xorg sur lequel il est lancé. Il lit le fichier de configuration, et exécute les commandes shell qu'il contient dès qu'une combinaison de touches est pressée. Le délais maximum entre de frappes de touches est de 500 milisecondes.

En réalité, dkb est construit autour de deux scripts distincts : keyboard_logger.py, qui écoute tous les évènements clavier de la session xorg, et les affiche à l'écran, et keylog_parser.py qui reçoit la sortie de keyboard_logger.py et lance l'exécution des commandes définies dans le fichier de configuration: Un programme, une fonctionnalité.

Le script 'dkb', quant à lui, permet de faire le lien entre les différents composants.

A terme, je prévoies (éventuellement) de réécrire les outils en `c` / `c++` :( / `golang`.

______
English
===
Simple keybindings motor for linux, written in python.

Warning
---
The 0.1.0 version has been released. You can see it on the release page.

Technical description
---
This software is coded in python3 using OOP and Parallelizm. The only dependency it needs is python3-xlib . dkb uses pyxhook (that you can find in the repo), and a very little subset of pykeylogger @ http://sourceforge.com/projects/pykeylogger.

Instructions
---
In order to use this software, edit the config_example.json file, then type `./dkb` on a terminal. Your keybindings are now accessible from your xorg session. The Scroll_Lock keyboard key permits to stop it properly.

Activity of the project
---
dkb is now able to monitor every keyboard event on its Xorg display. He reads the config file, and executes the shell commands that this file contains as the corresponding keystrokes are made. The maximum delay between two keystrokes is 500 miliseconds.

Actually, dkb is constructed aroud two different python scripts : keyboard_logger.py, which listens to all keyboard events from the xorg session, and print them to stdout ; and keylog_parser.py, which reads keyboard_logger.py's out and launch execution of commands defined in the config file: One program, one functionnality.

The 'dkb' script is here to link the different parts of the software one whith each other.

In the long term, I would rewrite the tools in `c` / `c++` :( / `golang`.
