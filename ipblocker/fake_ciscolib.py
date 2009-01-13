def login(ip):
    return FakeCisco(ip)


class FakeCisco:
    def __init__(self, ip):
        self.ip = ip
        self.load()
    def load(self):
        ips = []
        try :
            ips = open("/tmp/nullroutes_" + self.ip).read().split()
        except:
            pass
        self._nullroutes = ips
    def save(self):
        f=open("/tmp/nullroutes_" + self.ip,'w')
        for ip in self._nullroutes:
            f.write("%s\n" % ip)
        f.close()

    def nullroute_list(self):
        return self._nullroutes

    def nullroute_remove_many(self, ips):
        for ip in ips:
            if ip in self._nullroutes:
                self._nullroutes.remove(ip)
        self.save()
        
    def nullroute_add_many(self, ips):
        for ip in ips:
            if ip in self._nullroutes:
                raise Exception("%s already blocked" % ip)
            self._nullroutes.append(ip)
        self.save()

    def nullroute_remove(self, ip):
        return self.nullroute_remove_many([ip])

    def nullroute_add(self, ip):
        return self.nullroute_add_([ip])

    def write_mem(self):
        return ["Write mem"]

    def logout(self):
        pass
