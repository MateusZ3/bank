from django.db import connection
from decimal import Decimal

class Klient:

    def __init__ (self, data_tuple):
        (id, imie, nazwisko, login, haslo) = data_tuple
        self.id = id
        self.imie = imie
        self.nazwisko = nazwisko
        self.login = login
        self.haslo = haslo

    @staticmethod
    def get_klient_by_login(login):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, Imie, Nazwisko, Login, Haslo FROM Klient WHERE Login = %s;", [login])
            data = cursor.fetchone()
        return data

    @staticmethod
    def get_klient_by_id(id):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, Imie, Nazwisko, Login, Haslo FROM Klient WHERE id = %s;", [id])
            data = cursor.fetchone()
        return data

    def registration(self):
        return self.__save()

    def __save(self):
        result = False
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Klient (Imie, Nazwisko, Login, Haslo) VALUES (%s, %s, %s, %s);", [self.imie, self.nazwisko, self.login, self.haslo])
            result = True
        return result

    def get_rachunki(self):
        data = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, id_Klient, id_Rodzaj, Numer, Saldo, Dni_od_odsetek FROM Rachunek WHERE id_Klient = %s;", [self.id])
            for rachunek_tuple in cursor.fetchall():
                data.append(Rachunek(rachunek_tuple))
        return tuple(data)



class Rodzaj:
    def __init__(self, data_tuple):
        (id, nazwa, odsetki, co_ile_naliczane) = data_tuple
        self.id = id
        self.nazwa = nazwa
        self.odsetki = odsetki
        self.co_ile_naliczane = co_ile_naliczane

    @staticmethod
    def get_rodzaj_by_id(id):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, Nazwa, Odsetki, Co_ile_naliczane FROM Rodzaj WHERE id = %s;", [id])
            data = cursor.fetchone()
        return data

    @staticmethod
    def get_rodzaj_by_nazwa(nazwa):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, Nazwa, Odsetki, Co_ile_naliczane FROM Rodzaj WHERE Nazwa = %s;", [nazwa])
            data = cursor.fetchone()
        return data

    @staticmethod
    def get_all_rodzaj():
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, Nazwa, Odsetki, Co_ile_naliczane FROM Rodzaj;")
            data = cursor.fetchall()
        return data


class Rachunek:
    def __init__(self, data_tuple):
        (id, id_klient, id_rodzaj, numer, saldo, dni_od_odsetek) = data_tuple
        self.id = id
        self.klient = Klient(Klient.get_klient_by_id(id_klient))
        self.rodzaj = Rodzaj(Rodzaj.get_rodzaj_by_id(id_rodzaj))
        self.numer = numer
        self.saldo = saldo
        self.dni_od_odsetek = dni_od_odsetek

    def wplata(self, kwota, operacja):
        zmiana = self.saldo
        self.saldo = self.saldo + kwota
        zmiana = self.saldo - zmiana
        return self.__save_saldo(operacja, zmiana)

    def wyplata(self, kwota, operacja):
        zmiana = self.saldo
        self.saldo = max((self.saldo - kwota), 0)
        zmiana = self.saldo - zmiana
        return self.__save_saldo(operacja, zmiana)

    def aktualizacja(self, kwota, operacja):
        zmiana = self.saldo
        self.saldo = max((self.saldo + kwota), 0)
        zmiana = self.saldo - zmiana
        return self.__save_saldo(operacja, zmiana) and self.__save_dni_od_odsetek()

    def __save_saldo(self, operacja, zmiana):
        result = False
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Rachunek SET Saldo = %s WHERE id = %s;", [self.saldo, self.id])
            result = Operacja_wykonana((None , self.id, operacja.id, None, zmiana)).save()
        return result

    def __save_dni_od_odsetek(self,):
        result = False
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Rachunek SET Dni_od_odsetek = 0 WHERE id = %s;", [self.id])
            result = True
        return result

    def get_history(self):
        data = []
        for operacja_wykonana_tuple in Operacja_wykonana.get_operacje_wykonane_by_id_rachunek(self.id):
            data.append(Operacja_wykonana(operacja_wykonana_tuple))
        return tuple(data)

    def close(self):
        result = False
        with connection.cursor() as cursor:
            cursor.execute("SELECT zamknij_rachunek(%s);", [self.id])
            result = True
        return result

    def amount(self):
        return self.saldo * self.rodzaj.odsetki

    @staticmethod
    def get_rachunek_by_numer(numer):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, id_Klient, id_Rodzaj, Numer, Saldo, Dni_od_odsetek FROM Rachunek WHERE Numer = %s;", [numer])
            data = cursor.fetchone()
        return data

    @staticmethod
    def get_rachunek_by_id(id):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, id_Klient, id_Rodzaj, Numer, Saldo, Dni_od_odsetek FROM Rachunek WHERE id = %s;", [id])
            data = cursor.fetchone()
        return data

    @staticmethod
    def check_free(numer):
        return not Rachunek.get_rachunek_by_numer(numer)

    @staticmethod
    def otworz_rachunek(id_klient, rodzaj_nazwa, numer):
        rodzaj = Rodzaj(Rodzaj.get_rodzaj_by_nazwa(rodzaj_nazwa))
        result = False
        with connection.cursor() as cursor:
            cursor.execute("SELECT otworz_rachunek(%s, %s, %s);", [id_klient, rodzaj.id, numer])
            result = True
        return result

    @staticmethod
    def next_day():
        result = False
        with connection.cursor() as cursor:
            cursor.execute("SELECT next_day()")
            result = True
        return result

    @staticmethod
    def interest():
        result = False
        with connection.cursor() as cursor:
            cursor.execute("SELECT Rachunek.id, id_Klient, id_Rodzaj, Numer, Saldo, Dni_od_odsetek FROM Rachunek LEFT OUTER JOIN Rodzaj ON Rachunek.id_Rodzaj = Rodzaj.id WHERE Dni_od_odsetek >= Co_ile_naliczane;")
            operacja = Operacja(Operacja.get_operacja_by_nazwa('aktualizacja'))
            result = True
            for rachunek_tuple in cursor.fetchall():
                rachunek = Rachunek(rachunek_tuple)
                result = result and operacja.realize(rachunek, rachunek.amount())
        return result;


class Operacja:

    def __init__(self, data_tuple):
        (id, nazwa) = data_tuple
        self.id = id
        self.nazwa = nazwa

    def realize(self, rachunek, kwota):
        if self.nazwa == 'wplata':
            return rachunek.wplata(Decimal(kwota), self)
        if self.nazwa == 'wyplata':
            return rachunek.wyplata(Decimal(kwota), self)
        if self.nazwa == 'aktualizacja':
            return rachunek.aktualizacja(Decimal(kwota), self)

    @staticmethod
    def get_operacja_by_nazwa(nazwa):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, Nazwa FROM Operacja WHERE Nazwa = %s;", [nazwa])
            data = cursor.fetchone()
        return data

    @staticmethod
    def get_operacja_by_id(id):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, Nazwa FROM Operacja WHERE id = %s;", [id])
            data = cursor.fetchone()
        return data

    @staticmethod
    def operacja(rachunek, operacja, kwota):
        operacja_tuple = Operacja.get_operacja_by_nazwa(operacja)
        if operacja_tuple:
            return Operacja(operacja_tuple).realize(rachunek, kwota)
        else:
            return False;


class Operacja_wykonana:

    def __init__(self, data_tuple):
        (id, id_rachunek, id_operacja, data, zmiana) = data_tuple
        self.id = id
        self.rachunek = Rachunek(Rachunek.get_rachunek_by_id(id_rachunek))
        self.operacja = Operacja(Operacja.get_operacja_by_id(id_operacja))
        self.data = data
        self.zmiana = zmiana

    @staticmethod
    def get_operacje_wykonane_by_id_rachunek(id_rachunek):
        data = ()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, id_Rachunek, id_Operacja, Data, Zmiana FROM Operacja_wykonana WHERE id_Rachunek = %s;", [id_rachunek])
            data = cursor.fetchall()
        return data

    def save(self):
        result = False
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Operacja_wykonana (id_Rachunek, id_Operacja, Zmiana) VALUES (%s, %s, %s);", [self.rachunek.id, self.operacja.id, self.zmiana])
            result = True
        return result

class Test:
    
    @staticmethod
    def testowa():
        data = ()
        with connection.cursor() as cursor:
            cursor.execute('''BEGIN; 
                SELECT dupa('cities_cur'); 
                FETCH ALL IN "cities_cur"; COMMIT;''')
            data = cursor.fetchone()
        return data