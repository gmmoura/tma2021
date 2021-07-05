# TMA2021 



* This repository cointains the source code to reproduce Section 4 from the paper ``"Characterization of Anycast Adoption in the DNS Authoritative Infrastructure``
* This paper will appear in the forthcoming [TMA2021](https://tma.ifip.org/2021) conference

### Steps to reproduce it

##### 1. Run `parser.py` on both zone files and anycast prefix files. 
```bash
#2017:
#parameters:  $ZONEFILE $OUTFILE $ANYCAST_FILE 
python parser.py root-20170601.040412 out-2017.csv anycast2017.csv

#2021
python parser.py root-20210131.000122 out-2021.csv anycast2021.csv
```

Your out-files should look as something like:
```
#tld,NumberNSrecords,UniqueARecs,UniqueAAAArecs,AnycastPrefixesArecs,totalAnycastSitesIPv4,totalAnycastSitesIPv4Slash24,totalUnicastIPv4
aramco.,6,6,6,6,74,74,0
xn--55qw42g.,5,5,5,0,0,0,5
xn--mgbt3dhd.,4,4,4,4,122,122,0
nissay.,4,4,4,4,31,31,0
party.,6,6,6,6,99,99,0
cm.,5,5,5,1,2,2,4
casino.,4,4,4,4,73,73,0
...
```

 * The original repositories for the input files are:
   * Root zone DNS file: [IANA Root Zone File](https://www.iana.org/domains/root/files)
    * Anycast prefixes file: [Utwente Anycast Census](https://github.com/ut-dacs/Anycast-Census)
    

##### 2. Run the notebook called `match.ipynb`, and run each step:
    * `jupyter notebook match.ipynb`
    * This step allows you to retrieve the information necessary to write Tables II and III from the paper

##### 3. Create CDFs (Figures 1 and 2)

   * Let's do some pre-processing to make things easier for R
   
```shell
#filter only anycast ccTLDs in both measuremenst
head -n 1 cctld.csv > ccTLD-anycast-anycast.csv
cat cctld.csv |awk -F',' '$23=="Anycast" && $24=="Anycast"' >>ccTLD-anycast-anycast.csv

head -n 1 cctld.csv > cctld-unicast-mixed-or-anycast.csv
cat cctld.csv |awk -F',' '$23=="Unicast" && $24!="Unicast"' >> cctld-unicast-mixed-or-anycast.csv
```

Now, it's time to use [R](https://www.r-project.org/_) to generate the figures (you can also use Python for that)
  * Figure 1: `Rscript fig1.R`
    * fig1.pdf will  be generated 
  * Figure 2: `Rscript fig2.R`
    * fig2.pdf will  be generated 

EOF