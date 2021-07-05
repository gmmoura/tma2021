import dns
import sys
import json
from dnszone import dnszone


class TLD (object):
    def __init__(self, tld):
        self.tld = tld.lower()
        self.NSSet=set()
        self.NSes_A=dict()
        self.NSes_AAAA=dict()
        self.uniqueA=0
        self.uniqueAAAA=0
        self.uniqueA24=0
        self.totalSitesv4=0
        self.totalSitesv4_unique24=0
        self.totalUnicastIPv4=0
        self.totalAnycastv4=0
        self.uniquev4Addr=set()
        self.AnycastPrefixesArecs=set()
        self.uniquev6Addr=set()

    def calcPrefixes(self,prefixes):

        for k,v in self.NSes_A.items():
            for singleIP in v:

                self.uniquev4Addr.add(singleIP)
                sp=singleIP.split(".")
                prefix=sp[0]+"."+sp[1]+"."+sp[2]

                if prefix in prefixes:
                    nSites=int(prefixes[prefix])
                    self.totalSitesv4 = self.totalSitesv4 + nSites

                    if prefix not in self.AnycastPrefixesArecs:
                        if ":" in prefix:
                            print("shoot")
                        self.totalSitesv4_unique24= self.totalSitesv4_unique24 + nSites
                        self.AnycastPrefixesArecs.add(prefix)


                else:
                    self.totalUnicastIPv4=self.totalUnicastIPv4+1




        for k, v in self.NSes_AAAA.items():
            for singleIP in v:
                self.uniquev6Addr.add(singleIP)

    #need to print,: Number of tld,nses, number of unique IPv4, number of unique IPv6, and later uniqueANycastV4, uniqueAnycastV6
    def printStats(self,):
        uniqueAaddr=set()
        uniqueAAAAaddr=set()

        for k,v in self.NSes_A.items():
            uniqueAaddr.add(k)
        self.uniqueA=len(uniqueAaddr)

        for k, v in self.NSes_AAAA.items():
            uniqueAAAAaddr.add(k)
        self.uniqueAAAA = len(uniqueAAAAaddr)

        #aus.write("tld,NumberNSrecords,UniqueARecs,UniqueAAAArecs,AnycastPrefixesArecs,totalAnycastSitesIPv4,totalAnycastSitesIPv4Slash24,totalUnicastIPv4\n")
        return (str(self.tld) +"," + str(len(self.NSSet)) +"," + str(self.uniqueA) +"," +
                str(self.uniqueAAAA) + "," + str(len(self.AnycastPrefixesArecs)) + "," + str(self.totalSitesv4) + ","
                + str(self.totalSitesv4_unique24) + "," + str(self.totalUnicastIPv4))

class glue(object):
    def __init__(self,nsname):
        self.nsname=nsname
        self.Arecords=[]
        self.AAAArecords=[]

def run(input,anycastDict):


    #infile=sys.argv[0]
    #outfile=sys.argv[1]
    z = dnszone.zone_from_file('.', input)

    tldDict=dict()
    glueDict=dict()

    names=z.get_names()

    for singleName, data in names.items():
        sp=singleName.split(".")
        isTLD=False
        tld=''
        if len(sp)==2 and sp[1]=='':
            isTLD=True
            tld=singleName
            tld=str(tld)
        if isTLD:
            tempTLD=''



            if tld in tldDict:
                tempTLD=tldDict[tld]
            else:
                tempTLD = TLD(tld)

            records=(data._node.rdatasets)

            for rrecord in records:
                #first, ns records
                if rrecord.rdtype==2:
                    NSrecords=rrecord.items
                    for singleNS in NSrecords:
                        tempTLD.NSSet.add(str(singleNS))
            tldDict[tld]=tempTLD
        #then is glues and stuff
        else:
           # print("fix here")

            records=(data._node.rdatasets)
            name_server=str(singleName)

            tempGlue=''
            if name_server not in glueDict:
                tempGlue=glue(name_server)
            else:
                tempGlue=glueDict[name_server]


            for rrecord in records:
                #first, ns records
                if rrecord.rdtype==1:
                    Arecords=rrecord.items
                    for singleA in Arecords:
                        tempGlue.Arecords.append(str(singleA))
                elif rrecord.rdtype==28:
                    AAAArecords=rrecord.items
                    for singleAAAA in AAAArecords:
                        tempGlue.AAAArecords.append(str(singleAAAA))

            glueDict[name_server] = tempGlue


    #now, match both:

    for tld, tld_data in tldDict.items():
        tempNSSet=tld_data.NSSet



        # print( 'analyzing tld' + str(tld))
        for eachNS in tempNSSet:
            #print("analyzing tld/ns " + str(tld) + "," + str(eachNS) )
            if eachNS in glueDict:
                local_glue=glueDict[eachNS]
                for eachA in local_glue.Arecords:
                    localA=''
                    if eachNS not in tld_data.NSes_A:
                        localA=set()
                    else:
                        localA=tld_data.NSes_A[eachNS]

                    localA.add(eachA)
                tld_data.NSes_A[eachNS] = localA
                for eachAAAA in local_glue.AAAArecords:
                    localAAAA=''
                    if eachNS not in  tld_data.NSes_AAAA:
                        localAAAA=set()
                    else:
                        localAAAA=tld_data.NSes_AAAA[eachNS]

                    localAAAA.add(eachAAAA)
                tld_data.NSes_AAAA[eachNS]=localAAAA

        tldDict[tld] =tld_data

    #now add anycast info

    #get unique prefixes
    for k,v in tldDict.items():
        tld=k
        #if tld == 'nl.':
       #     print("debug")
        v.calcPrefixes(anycastDict)
        tldDict[k] =v



    return tldDict




if __name__ == '__main__':

    if len(sys.argv)!=4:
        print("wrong pars: to run it, type:\n python parser.py $ZONEFILE $OUTFILE $ANYCAST_FILE")

    else:
        infile=sys.argv[1]
        outfile=sys.argv[2]
        anycastFile=sys.argv[3]

        anycastDict=dict()
        with open(anycastFile, 'r') as f:
            for l in f:
                if 'number'  not in l  :
                    sp=l.split(",")
                    prefix=sp[0]
                    np=prefix.split(".")
                    prefix=np[0]+"."+np[1]+"."+np[2]
                    sites=sp[1].strip()
                    anycastDict[prefix]=sites


        mappedTLDs= run(infile,anycastDict)

        aus=open(outfile, 'w')

        aus.write(
            "tld,NumberNSrecords,UniqueARecs,UniqueAAAArecs,AnycastPrefixesArecs,totalAnycastSitesIPv4,totalAnycastSitesIPv4Slash24,totalUnicastIPv4\n")
        for k,v in mappedTLDs.items():
            if v is not None:
                resp=v.printStats()
                aus.write(resp+"\n")
        aus.close()
