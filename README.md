Napinklikkaus web-videopeli

Tilanne tällä hetkellä:
pystyy luomaan käyttäjän 
pystyy painamaan nappia ja saamaan pisteitä
pystyy tallentamaan pisteet
parhaat pisteet näytetään
pystyy liittymään koplaan (clique)
koplat voivat saavat pisteitä
parhaat koplat näytetään
virheet ilmoitetaan

Puutteet:
koplasta ei voi poistua
minimaalinen ja puutteellinen kommentointi
sivu näyttää huonolta (css tulossa)
käyttää neljää taulua (viides tulossa salee)
ei koodin hajautusta (tulee olemaan ongelma)


  Kuinka testata:

kloonaa tämä repostorio ja luo .env tiedosto johon määrität sisällön seuraavasti

DATABASE_URL= >tietokannan-paikallinen-osoite<

SECRET_KEY= >salainen-avain<

Aktivoi virtuaaliympäristö ja asenna riippuvuudet seuraavilla komennoilla

$ python3 -m venv venv

$ source venv/bin/activate

$ pip install -r ./requirements.txt

määritä tietokannan skeema komennolla

$ psql < schema.sql

käynnistä komennolla

$ flask run

  Visio: Napinklikkaus web-videopeli;

käyttäjät luovat tunnuksen jolla kirjautua. Painavat nappia kerätäkseen pisteitä.

Eniten pisteitä saaneet käyttäjät (ehkä joku top 10 tai jotain) saavat nimensä tulostaulukolle.

Käyttäjät voivat valita tai luoda joukkueen ja kerätä yhdessä tälle pisteitä; eri tulostaulukko mutta muuten sama.

Päivän kestävä 24h parhaat pisteet; kuin perusmuoto, mutta tulostaulukko ja pisteet nollautuisivat keskiyöllä.

Ehkä moderaattoreitä tjsp jolla oikeus poistaa tuloksia.
Jotain muuta mitä keksin?


