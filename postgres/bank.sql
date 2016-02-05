DROP TABLE Operacja_wykonana;
DROP TABLE Operacja;
DROP TABLE Rachunek_otwarty;
DROP TABLE Rachunek_zamkniety;
DROP TABLE Rachunek;
DROP TABLE Klient;
DROP TABLE Rodzaj;


CREATE TABLE Klient (
    id SERIAL PRIMARY KEY,
    Imie VARCHAR(255) NOT NULL,
    Nazwisko VARCHAR(255) NOT NULL,
    Login VARCHAR(255) UNIQUE NOT NULL,
    Haslo VARCHAR(255) NOT NULL
);
-- niezbedny klient
INSERT INTO Klient (Imie, Nazwisko, Login, Haslo) VALUES ('Atrapa', 'Atrapa', 'Atrapa', 'atrapa');


CREATE TABLE Rodzaj (
    id SERIAL PRIMARY KEY,
    Nazwa VARCHAR(255) UNIQUE NOT NULL,
    Odsetki DECIMAL(10,4) NOT NULL,
    Co_ile_naliczane INTEGER UNIQUE NOT NULL,
    Opis VARCHAR(255)
);


CREATE TABLE Rachunek (
    id SERIAL PRIMARY KEY,
    id_Klient INTEGER REFERENCES Klient(id) NOT NULL,
    id_Rodzaj INTEGER REFERENCES Rodzaj(id) NOT NULL,
    Numer INTEGER UNIQUE NOT NULL,
    Saldo DECIMAL(10, 4) DEFAULT 0.0000 NOT NULL,
    Dni_od_odsetek INTEGER DEFAULT 0 NOT NULL
);


CREATE TABLE Operacja (
    id SERIAL PRIMARY KEY,
    Nazwa VARCHAR(255) UNIQUE NOT NULL,
    Opis VARCHAR(255)
);
-- niezbedne operacje
INSERT INTO Operacja (Nazwa) VALUES 
    ('wplata'),
    ('wyplata'),
    ('aktualizacja')
;


CREATE TABLE Operacja_wykonana (
    id SERIAL PRIMARY KEY,
    id_Rachunek INTEGER REFERENCES Rachunek(id) NOT NULL,
    id_Operacja INTEGER REFERENCES Operacja(id) NOT NULL,
    Data DATE DEFAULT 'now()' NOT NULL,
    Zmiana DECIMAL(10,4) DEFAULT 0.0000 NOT NULL,
    Uwagi VARCHAR(255)
);


CREATE TABLE Rachunek_otwarty (
    id SERIAL PRIMARY KEY,
    id_Rachunek INTEGER REFERENCES Rachunek(id) NOT NULL,
    Data_otwarcia DATE DEFAULT 'now()' NOT NULL
);


CREATE TABLE Rachunek_zamkniety (
    id SERIAL PRIMARY KEY,
    id_Rachunek INTEGER REFERENCES Rachunek(id) NOT NULL,
    Data_zamkniecia DATE DEFAULT 'now()' NOT NULL
);


CREATE OR REPLACE FUNCTION otworz_rachunek(id_klient INTEGER, id_rodzaj INTEGER, numer INTEGER) 
    RETURNS void AS $$
DECLARE
    row Rachunek%rowtype;
BEGIN
    INSERT INTO Rachunek (id_Klient, id_Rodzaj, Numer) VALUES (id_klient, id_rodzaj, numer);
    SELECT * INTO row FROM Rachunek R WHERE R.Numer = otworz_rachunek.numer; 
    INSERT INTO Rachunek_otwarty (id_Rachunek) VALUES (row.id);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION next_day()
    RETURNS void AS $$
DECLARE
    row Rachunek%rowtype;
BEGIN
    FOR row IN SELECT * FROM Rachunek
    LOOP
        UPDATE Rachunek SET Dni_od_odsetek = row.Dni_od_odsetek + 1 WHERE id = row.id;
    END LOOP;
END
$$ language plpgsql;


CREATE OR REPLACE FUNCTION zamknij_rachunek(id_rachunek INTEGER) 
    RETURNS void AS $$
DECLARE
    row Rachunek%rowtype;
BEGIN
    UPDATE Rachunek SET id_Klient = 1, Saldo = 0, Dni_od_odsetek = 0 WHERE id = id_rachunek;
    INSERT INTO Rachunek_zamkniety (id_Rachunek) VALUES (id_rachunek);
END;
$$ LANGUAGE plpgsql;


INSERT INTO Rodzaj (Nazwa, Odsetki, Co_ile_naliczane) VALUES 
    ('DobreKonto', 0.10, 10),
    ('Ekstra', 0.50, 1),
    ('Slabe', -0.50, 2)
;