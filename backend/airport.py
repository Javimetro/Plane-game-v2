import random
import os

from geopy.distance import geodesic

import config


class Airport:

    def __init__(self, cur_icao):
        self.cur_icao = cur_icao



    def haeLatLong(self):
        sql = f'''select latitude_deg, longitude_deg from airport where ident="{self.cur_icao}"'''
        kursori = config.conn.cursor()
        kursori.execute(sql)
        tulos = kursori.fetchall()
        #self.lat = float(tulos[0][0])               #miksi?
        #print(f'lat on: {self.lat}')
        #self.long = float(tulos[0][1])
        #print(f'long on: {self.long}')
        return tulos

    def valikoima(self, kilometrit):
        # self.kilometrit = kilometrit              # ei tarvii luoda muuttujan
        lat = self.haeLatLong()[0][0]               #kutsutaan funktion vain kerran
        long = self.haeLatLong()[0][1]
        northlimit = float(lat) + float(kilometrit) * float(0.01)
        southlimit = float(lat) - float(kilometrit) * float(0.01)
        westlimit = float(long)
        eastlimit = float(long) + float(kilometrit) * float(0.01)
        if -180 < eastlimit < 180:
            sql = f'''SELECT ident, name, latitude_deg, longitude_deg
                FROM airport WHERE (type LIKE 'medium%' OR type LIKE'large%') AND latitude_deg BETWEEN {southlimit} AND {northlimit}
                AND longitude_deg BETWEEN {westlimit} AND {eastlimit}'''
        elif eastlimit > 180:
            eastlimit = eastlimit - 360

            sql = f'''SELECT ident, name, latitude_deg, longitude_deg
                FROM airport WHERE (type LIKE 'medium%' OR type LIKE'large%') AND latitude_deg BETWEEN {southlimit} AND {northlimit}
                AND longitude_deg BETWEEN {-180} AND {eastlimit} AND {westlimit} AND {180}'''

        kursori = config.conn.cursor(dictionary=True)
        kursori.execute(sql)
        tulos = kursori.fetchall()
        print(tulos)
        return tulos


    def vaihtoehdot(self, kilometrit):
        #self.kilometrit = kilometrit
        self.vaihtoehdot1 = []
        tulos = self.valikoima(kilometrit)
        for i in range(10):
            self.vaihtoehdot1.append(random.choice(tulos))
        #print(vaihtoehdot1)
        for vaihtoehto in self.vaihtoehdot1:
            dest_icao = vaihtoehto['ident']
            hinta = self.get_price(dest_icao)
            etaisyys = self.distance(dest_icao)
            vaihtoehto['price'] = round(hinta, 1)
            vaihtoehto['distance'] = int(etaisyys)
        return self.vaihtoehdot1

    def londoncityairport(self):
        sql = '''select ident, name, latitude_deg, longitude_deg
            from airport
            where ident = "EGLC"'''
        kursori = config.conn.cursor()
        kursori.execute(sql)
        tulos = kursori.fetchone()
        print(tulos)
        return tulos

    def city_country(self):
        sql = f'''select airport.municipality, country.name from airport, country 
        where airport.ident="{self.cur_icao}" and airport.iso_country=country.iso_country;'''
        kursori = config.conn.cursor()
        kursori.execute(sql)
        tulos = kursori.fetchall()
        for i in tulos:
            print(f'{i[0]} ,{i[1]}')

    def get_price(self, dest_icao):
        distanse = self.distance(dest_icao)
        hinta = distanse / 10 * self.alennus_alue(dest_icao)
        return round(hinta)

    def alennus_alue(self, dest_icao):
        tuple = (dest_icao,)
        sql = '''SELECT latitude_deg FROM airport 
            WHERE ident = %s'''
        kursori = config.conn.cursor()
        kursori.execute(sql, tuple)
        tulos = kursori.fetchone()
        if 20 < tulos[0] < 40:
            return 0.5
        elif 40 <= tulos[0] <= 60:
            return 1
        elif 0 < tulos[0] < 20:
            return 0.3
        elif 60 < tulos[0] < 80:
            return 1.3
        else:
            return 1

    def distance(self, dest_icao):
        dist = round(geodesic(self.coord(self.cur_icao), self.coord(dest_icao)).km, 3)
        return dist

    def coord(self, icao):
        sql = f'''SELECT latitude_deg, longitude_deg 
        FROM airport 
        WHERE ident = "{icao}"'''
        kursori = config.conn.cursor()
        kursori.execute(sql)
        tulos = kursori.fetchone()
        return tulos

    def yht_etaisyys(self, dest_icao):
        sql1 = f'''UPDATE game SET kilometrit_yht = kilometrit_yht + {self.distance(dest_icao)}'''
        sql2 = f'''SELECT kilometrit_yht FROM game WHERE location = {self.cur_icao}'''
        kursori = config.conn.cursor()
        kursori.execute(sql1)
        kursori.execute(sql2)
        tulos = kursori.fetchone()
        return tulos



    def londoncityairport(self, dest_icao):
        sql = '''select ident, name, latitude_deg, longitude_deg
                from airport
                where ident = "EGLC"'''
        kursori = config.conn.cursor()
        kursori.execute(sql)
        lontoo = kursori.fetchone()

        if self.yht_etaisyys(dest_icao) > 5000:
            etaisyysLCA = round(geodesic(self.coord(self.cur_icao), self.coord(lontoo[0])).km, 6)
            print(f'etäisyys Lontoosta: {etaisyysLCA}\n')
            if -50 < self.haeLatLong()[0][1] < 5 and self.distance(dest_icao) >= etaisyysLCA:
                self.vaihtoehdot1.append(lontoo)

