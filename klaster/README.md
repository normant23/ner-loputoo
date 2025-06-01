# Teadusarvutuste keskuse arvutusklastril Rocket kasutatud koodifailid

Arvutusklaster Rocket: https://hpc.ut.ee/services/HPC-services/Rocket

Failis `requirements.txt` on toodud arvutusklastril tööks kasutatud Pyhton virtuaalkeskkonna kõikide teekide versioonid. See sisaldab ka üleliigseid teeke, mis tulid kaasa arvutusklastril virtuaalkeskkonda luues. Pythoni versiooniks oli 3.12.3. Töös kasutatud virtuaalkeskkonna saab luua järgmiste käskudega:

Linux/macOS
```
virtualenv myenv
source myenv/bin/activate
pip install -r requirements.txt
```
Windows
```
virtualenv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

Kaustas `python` on toodud erinevad Pythoni koodifailid, mida töö jooksul kasutati. Kaustas `python/abi` on toodud koodifailid, mida kasutati linnavolikogu protokollide sõnestamiseks ja lausestamiseks. Need pole loodud antud töö autori poolt. Kaustas `python/taggers` on toodud erinevad märgendajad, mis aitavad mudelit rakendada. Märgendajat `estbertner_tagger` kasutati `EstBERT_NER` ja õppijamudelite rakendamiseks. See märgendaja on tavaliselt kaasas `estnltk_neural` teegiga, kuid autor kopeeris selle, et testida sellel erinevaid muudatusi. Teisi märgendajaid katsetati  õpetajamudeli rakendamiseks linnavolikogu andmetel.

Kaustas `slurm` on toodud ressusihaldus programmi Slurm tööskriptid, mida kasutati klastril vajalike tööde käivitamiseks.