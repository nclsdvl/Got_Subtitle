# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 16:17:54 2020

@author: utilisateur
"""

import mysql.connector 
import json
import os


#################################################################################################
######################         RECUPERATION DES JSON        #####################################
#################################################################################################

def recup_des_json (dossier_json) :
    mes_jsons = {}
    for fichier in dossier_json :
       with open('./json/'+fichier) as json_data:
           mes_jsons[fichier] = json.load(json_data)
    return mes_jsons


dossier_json = os.listdir('./json')
mes_jsons = recup_des_json(dossier_json)

# exemple pour un seul fichier :
"""
with open ('./json/season1.json') as mon_json :
    saison1 = json.load(mon_json)
"""

#################################################################################################
######################          CREATION DE LA BASE         #####################################
#################################################################################################

conn = mysql.connector.connect(host="localhost",user="root",password="!Simplon54", database="dataia_nancy")
cursor = conn.cursor()

# ce try execept n'est utile qu'en phase de developpement
try :
    cursor.execute("drop table got;")
    print('dropped')
except :
    print("n'existe pas")
    
    
# representation de la bdd souhaitée :
    
# id | saison  | num_episode |    nom_episode    | ligne_id |    sub     |
#-----------------------------------------------------------------------
#  1 | season1 |   S01E01    | Winter is coming  |    1     | Easy, boy. |

cursor.execute("""
CREATE TABLE IF NOT EXISTS got (
    id int(5) NOT NULL AUTO_INCREMENT,
    saison varchar(10) NOT NULL,
    num_episode varchar(200) NOT NULL,
    nom_episode varchar(200) NOT NULL,
    ligne_id int(5) NOT NULL,
    subtitle varchar(200) NOT NULL,
    PRIMARY KEY(id)
);
""")

#################################################################################################
######################         INSERTION DES DONNEES        #####################################
#################################################################################################


# mes_json = {'seasonX.json' :
#                   "Game Of Throne + num_episode + nom_episode.srt" :
#                           "ligne_id" :
#                               "subtitle" }


for saison, dico_episodes in mes_jsons.items() :
    season = saison[:-5] #retire .json 
    for episode, dico_subs in dico_episodes.items():
        if episode != 'season4.json': # dans season4 se trouve un dictionaire (vide) en trop nommé season4.json
            num_episode = episode[16:22] # -> s01e07
            nom_episode = episode[23:-4] # retire .srt            
            for key, value in dico_subs.items() :
                ligne_id = int(key)
                subtitle = value
                valeurs_a_ajouter = (season, num_episode, nom_episode, ligne_id, subtitle)
                query = """INSERT INTO got 
                        (saison, num_episode, nom_episode, ligne_id, subtitle)
                        VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, valeurs_a_ajouter)
                conn.commit()
cursor.close()
conn.close()              


#################################################################################################
######################    RECUPERATION DES DONNEES EN BDD        ################################
#################################################################################################

conn = mysql.connector.connect(host="localhost",user="root",password="!Simplon54", database="dataia_nancy")
cursor = conn.cursor()

# création de 2 requetes :
query_s01e01 = "SELECT * from got WHERE num_episode = 'S01E01';"
query_nom_episodes = "SELECT DISTINCT nom_episode from got ;"

# execution de la premiere requete :
cursor.execute(query_s01e01)
mes_resultats = cursor.fetchall()

# recuperation des resultats pour la premiere requete
prem_phrase = mes_resultats[0]
derniere_phrase = mes_resultats[-1]

# execution de la seconde requete :
cursor.execute(query_nom_episodes)

# recuperation des resultats pour la seconde requete
noms_episodes = cursor.fetchall()
conn.commit()

print("\le premier épisode à pour nom : " + str(noms_episodes[0][0]))
print("la premiere phrase de l'episode 1 est : '"+ prem_phrase[5] + "'")
print("la dernière phrase de l'episode 1 est : '"+ derniere_phrase[5] + "'")



cursor.close()   
conn.close()
