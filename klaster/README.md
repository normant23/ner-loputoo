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

## Koodifailide kirjeldused

### Ettevalmistus

`filter_koik` - Valmistab ette kõikidest protokollidest koosneva andmestiku.

`filter_tudeng` - Valmistab ette katsemärgendusandmestiku.

`process_gold` - Valmistab ette kuldstandardandmestiku. Lisaks parandatakse mõned andmetes esinevad vead, mis avastati käesoleva töö käigus.


### Andmetöötlus

`tagged_to_csv` - Õpetajamudeli rakendamisel saadud andmetest tehaks erinevate lävendite alusel csv failid, kus igale real on info sobiva lause kohta. Iga lause kohta on toodud csv-failis protokolli faili nimi, lause indeks, lause algusindeks sõnade tasemel, lause lõpuindeks sõnade tasemel, LOC kategooria märgendite arv, PER kategooria märgendite arv, ORG kategooria märgendite arv.

`sen_csv_to_silver` - `tagged_to_csv` tulemusena saadud csv-failidest valitakse suvaliselt laused, kuni märgendite arv ületab kindlat piiri. Selliseid piire on mitu ja selle faili tulemusena luuakse valitud lausete andmetest csv-failid. Iga lause kohta on toodud csv-failis protokolli faili nimi, lause indeks, lause algusindeks sõnade tasemel, lause lõpuindeks sõnade tasemel, LOC kategooria märgendite arv, PER kategooria märgendite arv, ORG kategooria märgendite arv.

`silver_to_bio` - `sen_csv_to_silver` tulemusena saadud csv failidest võetakse valitud lausete informatsioon ja need viiakse BIO-kujule, et neid saaks kasutada mudelite loomiseks. BIO-kujul olevad andmed salvestatakse csv-kujule.

`tudeng_to_bio` - Teisendab katsemärgendusandmestiku sobivad laused bio-kujule, et neid andmeid saaks kasutatada katsemärgendusmudeli loomiseks.


### Mudelite loomine 

`teacher_model` - Loob ristvalideerimise gruppide põhjal õpetajamudelid.

`single_model` - Loob korraga ühe mudeli õppijamudeli/katsemärgendusmudeli.

`multiple_models` - Loob korraga palju erinevaid õppijamudeleid.


### Mudeli rakendamine

`apply_teacher_model` - Rakendab märgendamata protokollidele õpetajamudeleid.


### Tulemused

`cpu_final_results` - Mudelite tulemused andmetel (cpu)

`gpu_final_results` - Mudelite tulemsued andmetel (gpu),  `gpu_final_results.py` Pythoni fail väljastab tulemused kasutades `print` ja `gpu_final_results_csv.py` salvestab tulemused csv-kujule 
