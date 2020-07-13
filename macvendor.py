import requests
import os
# import time

class macvendor:
    __DBFILE = os.path.join(os.path.dirname(__file__), 'macvendorsdb.txt')
    __INSTANCE = None
    
    @staticmethod
    def get_instance():
        if not macvendor.__INSTANCE:
            macvendor.__INSTANCE = macvendor()
        return macvendor.__INSTANCE

    def __init__(self):
        self.__data = {}
        self.__load_database()

    def get_vendor(self, mac):
        lookup = self.__get_mac_lookup(mac)
        vendor = self.__cached_fetch(lookup)
        if vendor == 'unknown':
            vendor = self.__remote_fetch(lookup)
            if vendor != 'unknown':
                self.__data[lookup] = vendor
                self.__insert_intodb(lookup, vendor)
        return vendor
    
    def __load_database(self):
        with open(macvendor.__DBFILE) as fp:
            for line in fp:
                tokens = line[:-1].split()
                lookup = tokens[0].upper()
                vendor = ' '.join(tokens[1:])
                self.__data[lookup] = vendor
    
    def __insert_intodb(self, lookup, vendor):
        with open(macvendor.__DBFILE, 'a') as fp:
            fp.write('{}\t{}\n'.format(lookup, vendor))
    
    def __get_mac_lookup(self, mac):
        return mac.replace(':', '')[:6].upper()
    
    def __cached_fetch(self, lookup):
        try:
            return self.__data[lookup]
        except KeyError:
            return 'unknown'
    
    def __remote_fetch(self, lookup):
        resend_limit = 3
        for _ in range(resend_limit):
            response = requests.get('http://api.macvendors.com/{}'.format(lookup))
            if response.ok:
                return response.content.decode().upper()
            #else:
            #    time.sleep(1)
        return 'unknown'
