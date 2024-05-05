Napinklikkaus web-videopeli

Ominaisuudet
Rekisteröityminen kirjautuminen yms
Paina nappia ja saa pisteitä; parhaat klikkaajat pääsevät tulostaulukolle
Voit tehdä koplia / liittyä niihin ja kerätä pisteitä yhteistyön voimalla
Admin/moderointi systeemi (ensimmäinen luotu tili saa adminin)

Kuinka testata:

kloonaa tämä repostorio ja luo .env tiedosto johon määrität sisällön seuraavasti

`DATABASE_URL= <tietokannan-paikallinen-osoite>`

`SECRET_KEY= <salainen-avain>`

Aktivoi virtuaaliympäristö ja asenna riippuvuudet seuraavilla komennoilla

`$ python3 -m venv venv`

`$ source venv/bin/activate`

`$ pip install -r ./requirements.txt`

määritä tietokannan skeema komennolla

`$ psql < schema.sql`

käynnistä komennolla

`$ flask run`



