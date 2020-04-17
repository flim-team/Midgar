**The data with problems**
        Unnamed: 0 movie author  Class movietime
697540        2817     8      8    9.0         8
725981        9175     8      8    9.0         8

**Group by author:**
Scorsese     182392
Bergman      160118
Godard       143859
Fellini      127735
Antonioni     80688
Tarr          72041
8                 2
*Name: author, dtype: int64*

**Group by movie:**
movie                             author   
2 ou 3 choses que je sais d'elle  Godard        5971
8                                 8                2
A Londoni Férfi                   Tarr          8045
A bout de souffle                 Godard        5171
A torinói ló                      Tarr          9068
After Hours                       Scorsese      5943
Alice doesn_t live here anymore   Scorsese      6450
Allemagne 90 neuf zero            Godard        3729
Alphaville                        Godard        5933
Amarcord                          Fellini       7111
Ansikte mot ansikte               Bergman       6833
Ansiktet                          Bergman       5811
Aus dem Leben der Marionetten     Bergman       5972
Bande a part                      Godard        5763
Beröringen                        Bergman       5742
Blowup                            Antonioni     6401
Boxcar Bertha                     Scorsese      5288
Bringing Out the Dead             Scorsese      7262
Cape Fear                         Scorsese      7726
Casanova                          Fellini       8876
Casino                            Scorsese     10345
Cronaca di un amore               Antonioni     5882
Családi tűzfészek                 Tarr          5976
Das Schlangenei                   Bergman       7161
Det Sjunde inseglet               Bergman       5458
Detective                         Godard        5971
Djävulens öga                     Bergman       5033
E la nave va                      Fellini       7644
Eloge de l'amour                  Godard        5891
Fanny och Alexander               Bergman      10685
Film socialisme                   Godard        5838
For Ever Mozart                   Godard        4848
Fängelse                          Bergman       4513
Gangs of New York                 Scorsese      9996
Ginger e Fred                     Fellini       7632
Giulietta degli spiriti           Fellini       7897
Goodfellas                        Scorsese      8728
Gycklarnas afton                  Bergman       5305
Hugo                              Scorsese      7582
Höstsonaten                       Bergman       5320
I vinti                           Antonioni     6503
I vitelloni                       Fellini       6466
Il Bidone                         Fellini       6768
Il Mistero di Oberwald            Antonioni     7405
Il deserto rosso                  Antonioni     6718
Je vous salue Marie               Godard        4559
Jungfrukällan                     Bergman       5131
King Lear                         Godard        5097
Kundun                            Scorsese      8036
Kvinnordröm                       Bergman       5016
Kvinnors väntan                   Bergman       6197
L'avventura                       Antonioni     8583
L'eclisse                         Antonioni     7546
La Dolce Vita                     Fellini      10007
La Notte                          Antonioni     7014
La Strada                         Fellini       5797
La chinoise                       Godard        5532
La città delle donne              Fellini       8358
La signora senza camelie          Antonioni     6069
La voce della luna                Fellini       6836
Le Mepris                         Godard        6165
Le Petit Soldat                   Godard        5059
Le amiche                         Antonioni     5939
Le notti di Cabiria               Fellini       6647
Les Carabiniers                   Godard        4571
Lo sceicco bianco                 Fellini       5194
Luci del varietà                  Fellini       5841
Macbeth                           Tarr          3720
Made in USA                       Godard        5101
Masculin feminin                  Godard        5992
Mean Streets                      Scorsese      6444
Nattvardsgästerna                 Bergman       4840
New York, New York                Scorsese      9791
Notre musique                     Godard        4581
Nouvelle vague                    Godard        5131
Nära livet                        Bergman       4846
Otto e Mezzo                      Fellini       8285
Panelkapcsolat                    Tarr          4585
Persona                           Bergman       4744
Pierrot le Fou                    Godard        6621
Prenom Carmen                     Godard        5079
Professione reporter              Antonioni     5971
Prova d'orchestra                 Fellini       4161
Raging Bull                       Scorsese      7744
Riten                             Bergman       4313
Roma                              Fellini       6804
Saraband                          Bergman       6701
Sasom i en spegel                 Bergman       5364
Satyricon                         Fellini       7411
Sauve qui peut                    Godard        5080
Shutter Island                    Scorsese      8285
Skammen                           Bergman       6174
Smultronstället                   Bergman       5244
Soigne ta droite                  Godard        4906
Sommaren med Monika               Bergman       5513
Sommarlek                         Bergman       5509
Sommarnattens leende              Bergman       6261
Szabadgyalog                      Tarr          7315
Sátántangó                        Tarr         25233
Taxi Driver                       Scorsese      6827
The Age of Innocence              Scorsese      8306
The Aviator                       Scorsese     10206
The Departed                      Scorsese      8422
The King of Comedy                Scorsese      6540
The Last Temptation of Christ     Scorsese      9791
The Wolf of Wall Street           Scorsese     10794
The color of money                Scorsese      6720
Tout va bien                      Godard        5765
Tystnaden                         Bergman       5717
Une femme est une femme           Godard        4818
Une femme mariee                  Godard        5701
Vargtimmen                        Bergman       5248
Viskningar och rop                Bergman       5467
Vivre sa vie                      Godard        4986
Werckmeister harmóniák            Tarr          8099
Who's that knocking at my door    Scorsese      5166
Zabriskie Point                   Antonioni     6657

**Group by movie:**
0.0    368039
1.0    180504
9.0    156859
2.0     61433
Name: Class, dtype: int64

**Strategy:**

![img](https://ask.qcloudimg.com/http-save/yehe-1654149/rryvkclyu9.png?imageView2/2/w/1620)

oversampling:   1. Copy the original image groups which are less than the average number.

​							2. Use data augmentation to boost the number of images with less numebrs.



undersampling: Skip some of the images with larger number than others. 

