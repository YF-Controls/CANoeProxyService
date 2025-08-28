

pip install py_canoe --upgrade



en la DB9

resistencia 120 ohms entr 1 y 8


https://support.vector.com/kb?sys_kb_id=9ef442e41b2614148e9a535c2e4bcb69&id=kb_article_view&sysparm_rank=5&sysparm_tsqueryId=b046dd80fbe22a542430f55dbeefdcf7

Channel (a)1 (can/lin) (este es el canal que va a la puerta)
DB9 --------------------------------> DCU
can L 2 (marron)             pin 1 (gris)
gnd   3 blanco               
can H 7 (verde)              pin 2 (verde)

Channel (b)3 (can)
DB9 --------------------------------> DCU
can L 1 (marron)             pin 1 (gris)
gnd   6 blanco               
can H 8 (verde)              pin 2 (verde)


## Zenzefi

https://127.0.0.1:61000/#/zenzefi/ui/error/401
Usuario: S1AZENZE
Contraseña: GA0525,Prod

HMI
user: admin
pass: ide


Hacer login offline de vez en cuando.

Hacer pantalla de advertencia para que el operario
haga login offline.


Log format:

%(asctime)s [%(levelname)-8s] %(message)-80s [%(name)s , %(funcName)s , %(lineno)d]
%(asctime)s [%(levelname)-8s] [%(name)s , %(funcName)s , %(lineno)d] %(message)
