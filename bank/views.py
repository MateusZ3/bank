from django.shortcuts import render
from .models import Klient, Rachunek, Rodzaj, Operacja, Operacja_wykonana, Test
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string

def login(request):
    if 'login' in request.session:
        return index(request, 'Podales popwarne dane, zostales zalogowany. Witamy!')
    if request.method == 'POST':
        login = request.POST['login']
        haslo = request.POST['haslo']
        data = Klient.get_klient_by_login(login)
        if data and Klient(data).haslo == haslo:
            request.session['login'] = login
            return index(request, 'Podales popwarne dane, zostales zalogowany. Witamy!')
        else:
            return render(request, 'bank/login.html', {'info': 'Bledne dane'})
    else:
        return render(request, 'bank/login.html', {})

def logout(request):
    if 'login' in request.session:
        del request.session['login']
    return HttpResponseRedirect('/login/')

def index(request, main=render_to_string('bank/reklama.html', {})):
    if 'login' in request.session:
        login = request.session['login']
        return render(request, 'bank/index.html', {'login': login, 'main': main})
    else:
        return HttpResponseRedirect('/login/')

def rachunki(request):
    if 'login' in request.session:
        rachunki = Klient(Klient.get_klient_by_login(request.session['login'])).get_rachunki()
        main = render_to_string('bank/rachunki.html', {'rachunki': rachunki})
        return index(request, main)
    else:
        return HttpResponseRedirect('/login/')

def rachunek(request, numer):
    if 'login' in request.session:
        klient = Klient(Klient.get_klient_by_login(request.session['login']))
        rachunek_tuple = Rachunek.get_rachunek_by_numer(numer)
        if rachunek_tuple:
            rachunek = Rachunek(rachunek_tuple)
            if klient.id == rachunek.klient.id:
                info = ''
                if request.method == 'POST':
                    kwota = request.POST['kwota']
                    operacja = request.POST['operacja']
                    if  Operacja.operacja(rachunek, operacja, kwota):
                        info = 'Operacja zakonczona sukcesem'
                    else:
                        return index(request, 'Nie mozna wykonac zadanej operacji')
                return render(request, 'bank/rachunek.html', {'rachunek': rachunek, 'login': klient.login, 'info': info})
            else:
                return index(request, 'Brak uprawnien')
        else:
            return index(request, 'Rachunek nie istnieje')
    else:
        return HttpResponseRedirect('/login/')

def historia(request, numer):
    if 'login' in request.session:
        klient = Klient(Klient.get_klient_by_login(request.session['login']))
        rachunek_tuple = Rachunek.get_rachunek_by_numer(numer)
        if rachunek_tuple:
            rachunek = Rachunek(rachunek_tuple)
            if klient.id == rachunek.klient.id:
                operacje_wykonane = rachunek.get_history()
                main = render_to_string('bank/historia.html', {'operacje_wykonane': operacje_wykonane})
                return index(request, main)
            else:
                return index(request, 'Brak uprawnien')
        else:
            return index(request, 'Rachunek nie istnieje')
    else:
        return HttpResponseRedirect('/login/')

def zamknij(request, numer):
    if 'login' in request.session:
        klient = Klient(Klient.get_klient_by_login(request.session['login']))
        rachunek_tuple = Rachunek.get_rachunek_by_numer(numer)
        if rachunek_tuple:
            rachunek = Rachunek(rachunek_tuple)
            if klient.id == rachunek.klient.id:
                if rachunek.close():
                    return index(request, 'Rachunek zostal zamkniety')
                else:
                    return index(request, 'Nie mozna wykonac zadanej operacji')
            else:
                return index(request, 'Brak uprawnien')
        else:
            return index(request, 'Rachunek nie istnieje')
    else:
        return HttpResponseRedirect('/login/')

def otworz(request):
    if 'login' in request.session:
        klient = Klient(Klient.get_klient_by_login(request.session['login']))
        all_rodzaj = []
        for rodzaj_tuple in Rodzaj.get_all_rodzaj():
            all_rodzaj.append(Rodzaj(rodzaj_tuple))
        info = ''
        if request.method == 'POST':
            numer = request.POST['numer']
            if Rachunek.check_free(numer):
                rodzaj = request.POST['rodzaj']
                if Rachunek.otworz_rachunek(klient.id, rodzaj, numer):
                    return index(request, 'Rachunek zostal otwarty')
                else:
                    return index(request, 'Nie mozna wykonac zadanej operacji')
            else:
                info = 'Podany numer rachunku jest zajety, wybierz inny'
        return render(request, 'bank/otworz.html', {'all_rodzaj': tuple(all_rodzaj), 'info': info})
    else:
        return HttpResponseRedirect('/login/')

def kolejny_dzien(request):
    if 'login' in request.session:
        Rachunek.next_day()
        if Rachunek.interest():
            return index(request, 'Mamy kolejny piekny dzien. Opcja prezentujaca naliczanie odsetek')
        else:
            return index(request, 'Nie mozna wykonac zadanej operacji')
    else:
        return HttpResponseRedirect('/login/')

def rodzaj(request, id):
    if 'login' in request.session:
        rodzaj_tuple = Rodzaj.get_rodzaj_by_id(id)
        if rodzaj_tuple:
            rodzaj = Rodzaj(rodzaj_tuple)
            return index(request, 'Konto: ' + rodzaj.nazwa + ', oprocentowanie wynosi ' + str(rodzaj.odsetki * 100) + '% naliczane co ' + str(rodzaj.co_ile_naliczane) + ' dni')
        else:
            return index(request, 'Rodzaj konta nie istnieje')
    else:
        return HttpResponseRedirect('/login/')

def oferta(request):
        all_rodzaj = []
        for rodzaj_tuple in Rodzaj.get_all_rodzaj():
            all_rodzaj.append(Rodzaj(rodzaj_tuple))
        if 'login' in request.session:
            login = request.session['login']
            return render(request, 'bank/oferta.html', {'all_rodzaj': tuple(all_rodzaj), 'login': login})
        else:
            return render(request, 'bank/oferta.html', {'all_rodzaj': tuple(all_rodzaj)})

def rejestracja(request):
    if 'login' in request.session:
        return index(request, 'Jestes zalogowany')
    else:
        if request.method == 'POST':
            imie = request.POST['imie']
            nazwisko = request.POST['nazwisko']
            login = request.POST['login']
            haslo = request.POST['haslo']
            if Klient.get_klient_by_login(login):
                return render(request, 'bank/rejestracja.html', {'info': 'Podany login jest zajety, wybierz inny'})
            else:
                if Klient((None, imie, nazwisko, login, haslo)).registration():
                    return HttpResponseRedirect('/login/')
                else:
                    return render(request, 'bank/rejestracja.html', {'info': 'Nie mozna wykonac zadanej operacji'})
        else:
            return render(request, 'bank/rejestracja.html', {})