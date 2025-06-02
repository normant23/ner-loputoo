# Tavaarvutil kasutatud koodifailid

Antud kaustas on toodud failid, mida kasutas antud töö autor tavaarvutil katsetuste tegemiseks.

Virtuaalkeskkond loodi tavaarvutil Conda abil. Virtuaalkeskkonna teekide versioonid on toodud failis `environment.yml`. Tavaarvutil kasutatud virtuaalkeskkonda saab taasluua järgmise käsuga:
```
conda env create -f environment.yml
```

Kaustas `abi` on toodud koodifailid, mida kasutati linnavolikogu protokollide sõnestamiseks ja lausestamiseks. Need pole loodud antud töö autori poolt.

Kaustas `taggers` on toodud erinevad märgendajad, mis aitavad mudelit rakendada. `bert_ner_tagger` märgendajat kasutati `est-roberta-hist-ner` mudeli rakendamiseks. Teisi märgendajaid katsetati õpetajamudeli rakendamiseks linnavolikogu andmetel.

Erinevaid `notebook` faile on kasutatud väiksemate koodiosade testimiseks ja väiksemate ülesannete lahendamiseks.
