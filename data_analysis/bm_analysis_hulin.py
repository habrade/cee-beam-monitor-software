#!/usr/bin/env python3

from glob import glob
import os
import matplotlib.pyplot as plt
from ROOT import TGraph, TCanvas, TFile, TH1F, TH2F, TChain, gDirectory, TLegend, TColor
from array import array
import numpy as np

class myrun(object):
    def __init__(self, filename='../data/arst1.05_20k_200mV_in.dat'):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.basename = os.path.basename(filename)
        self.outfilenameraw = self.dirname + "/" + self.basename.split('.')[0]+"_raw.root"
        self.outfilenamesel = self.dirname + "/" + self.basename.split('.')[0]+"_sel.root"
        #self.hexdataall = 0
        #self.lhexframe = [None]*4000 #notice!!
        self.lhexframe = []
        self.outfileraw = TFile(self.outfilenameraw,'recreate')
        self.outfilesel = TFile(self.outfilenamesel,'recreate')
        #self.labelcut = [7600,7600,100,7600]
        self.labelcut = [5000,5000,100,5000]
        self.meanstd = 0

    def getinput_from_dat(self):
        with open(self.filename,'rb') as f1:
            hexdataall = f1.read().hex()
            hexlen = len(hexdataall)
            print("{}: {} byte, {} data,  {} frame".format(self.basename, hexlen/2, hexlen/8, hexlen/8/16384))
            lhex = [hexdataall[i*8:i*8+8] for i in range(hexlen//8)]
            for f in lhex[:8]: print(f)
            lhead = [i for i, x in enumerate(lhex) if x=='eb9055aa']
            ltail = [i for i, x in enumerate(lhex) if x=='eb905aa5']
            lheaddiff = [j-i for i, j in zip(lhead[:-1],lhead[1:])]
            ltaildiff = [j-i for i, j in zip(ltail[:-1],ltail[1:])]
            lheadtaildiff = []
            if(lhead[0]>ltail[0]) : ltail.pop(0)
            lheadtaildiff = [j-i for i, j in zip(lhead,ltail)]
            print("len head tail",len(lhead),len(ltail))
            #print("lhead")
            #print(lhead)
            #print("lheaddiff")
            #print(lheaddiff)
            #print("ltail")
            #print(ltail)
            #print("ltaildiff")
            #print(ltaildiff)
            #print("lheadtaildiff")
            #print(lheadtaildiff)
            #ilhex = 0
            for ih in range(len(lhead)-1) :
                iframestart = lhead[ih] + 8
                iframestop = lhead[ih] + 8
                for it in range(len(ltail)) :
                    if ltail[it] > lhead[ih] and ltail[it] < lhead[ih+1]:
                        iframestop = ltail[it]-5
                        break
                print("frame start {}, stop {}, length {}".format(iframestart, iframestop, iframestop - iframestart + 1))
                if (iframestop - iframestart + 1) == 10368 :
                    self.lhexframe.append((lhex[iframestart:iframestop+1],ih))
                    #self.lhexframe[ilhex] = (lhex[iframestart:iframestop+1],ih)
                    #ilhex += 1
            #self.lhexframe = self.lhexframe[:ilhex]
            print("{} good frames".format(len(self.lhexframe)))


    def process_input(self):
        index = 0
        self.outfileraw.cd()
        for frame in self.lhexframe :
            #print("index {}, length {}".format(frame[1], len(frame[0])))
        #for frame in self.lhexframe[:1] :  #notice!!
            subframe0 = frame[0][0::4]
            subframe1 = frame[0][1::4]
            subframe2 = frame[0][2::4]
            subframe3 = frame[0][3::4]
            #print("subframe size: {} {} {} {}".format(len(subframe0), len(subframe1), len(subframe2), len(subframe3)))  
            dataframe0 = hexframetodataframe(subframe0)
            dataframe1 = hexframetodataframe(subframe1)
            dataframe2 = hexframetodataframe(subframe2)
            dataframe3 = hexframetodataframe(subframe3)
            #print("dataframe size: {} {} {} {}".format(len(dataframe0), len(dataframe1), len(dataframe2), len(dataframe3)))
            gr0 = list2tgraph(dataframe0) 
            gr1 = list2tgraph(dataframe1) 
            gr2 = list2tgraph(dataframe2) 
            gr3 = list2tgraph(dataframe3) 
            h20 = list2th2f(dataframe0,"h2frame0_{}".format(index))
            h21 = list2th2f(dataframe1,"h2frame1_{}".format(index))
            h22 = list2th2f(dataframe2,"h2frame2_{}".format(index))
            h23 = list2th2f(dataframe3,"h2frame3_{}".format(index))
            gr0.Write("tgframe0_{}".format(index))
            gr1.Write("tgframe1_{}".format(index))
            gr2.Write("tgframe2_{}".format(index))
            gr3.Write("tgframe3_{}".format(index))
            h20.Write()
            h21.Write()
            h22.Write()
            h23.Write()
            #c1 = TCanvas("c1","c1",800,600)
            #gr.Draw("APL")
            #c1.Update()
            #c = input("ddd")

            #plt.plot(dataframe0)
            #plt.plot(dataframe1)
            #plt.plot(dataframe2)
            #plt.plot(dataframe3)
            #plt.show()
            index += 1

    def process_input_align(self):
        ldataframeall0 = []
        ldataframeall1 = []
        ldataframeall2 = []
        ldataframeall3 = []
        for i in range(len(self.lhexframe)) :
            subframe0 = self.lhexframe[i][0][0::4]
            subframe1 = self.lhexframe[i][0][1::4]
            subframe2 = self.lhexframe[i][0][2::4]
            subframe3 = self.lhexframe[i][0][3::4]
            #print("subframe size: {} {} {} {}".format(len(subframe0), len(subframe1), len(subframe2), len(subframe3)))  
            dataframe0 = hexframetodataframe(subframe0)
            dataframe1 = hexframetodataframe(subframe1)
            dataframe2 = hexframetodataframe(subframe2)
            dataframe3 = hexframetodataframe(subframe3)
            labelframe0, islabel0 = find_label(dataframe0, self.labelcut[0])
            labelframe1, islabel1 = find_label(dataframe1, self.labelcut[1])
            labelframe2, islabel2 = find_label(dataframe2, self.labelcut[2])
            labelframe3, islabel3 = find_label(dataframe3, self.labelcut[3])
            #print(i, "labelframe0", labelframe0, islabel0)
            #print(i, "labelframe1", labelframe1, islabel1)
            #print(i, "labelframe2", labelframe2, islabel2)
            #print(i, "labelframe3", labelframe3, islabel3)
            ldataframeall0.append((dataframe0, self.lhexframe[i][1], labelframe0, islabel0)) 
            ldataframeall1.append((dataframe1, self.lhexframe[i][1], labelframe1, islabel1))
            ldataframeall2.append((dataframe2, self.lhexframe[i][1], labelframe2, islabel2)) 
            ldataframeall3.append((dataframe3, self.lhexframe[i][1], labelframe3, islabel3)) 

        ldataframealign0 = ldataframealltoalign(ldataframeall0)
        ldataframealign1 = ldataframealltoalign(ldataframeall1)
        ldataframealign2 = ldataframealltoalign(ldataframeall2)
        ldataframealign3 = ldataframealltoalign(ldataframeall3)
        print("ldataframealign size {} {} {} {}".format(len(ldataframealign0),len(ldataframealign1),len(ldataframealign2),len(ldataframealign3)))
        writelframetoroot(ldataframealign0, "framealign0", self.outfilesel)
        writelframetoroot(ldataframealign1, "framealign1", self.outfilesel)
        writelframetoroot(ldataframealign2, "framealign2", self.outfilesel)
        writelframetoroot(ldataframealign3, "framealign3", self.outfilesel)
#        for i in range(len(ldataframealign0)):
#            gr = list2tgraph(ldataframealign0[i])
#            h2 = list2th2f(ldataframealign0[i],"h2framealign0_{}".format(i))
#            self.outfilesel.cd()
#            gr.Write("tgframeslign0_{}".format(i))
#            h2.Write()
#        for i in range(len(ldataframealign1)):
#            gr = list2tgraph(ldataframealign1[i])
#            h2 = list2th2f(ldataframealign1[i],"h2framealign1_{}".format(i))
#            self.outfilesel.cd()
#            gr.Write("tgframeslign1_{}".format(i))
#            h2.Write()
#        for i in range(len(ldataframealign2)):
#            gr = list2tgraph(ldataframealign2[i])
#            h2 = list2th2f(ldataframealign2[i],"h2framealign2_{}".format(i))
#            self.outfilesel.cd()
#            gr.Write("tgframeslign2_{}".format(i))
#            h2.Write()
#        for i in range(len(ldataframealign3)):
#            gr = list2tgraph(ldataframealign3[i])
#            h2 = list2th2f(ldataframealign3[i],"h2framealign3_{}".format(i))
#            self.outfilesel.cd()
#            gr.Write("tgframeslign3_{}".format(i))
#            h2.Write()

        self.meanstd0 = calmeanstd(ldataframealign0)
        self.meanstd1 = calmeanstd(ldataframealign1)
        self.meanstd2 = calmeanstd(ldataframealign2)
        self.meanstd3 = calmeanstd(ldataframealign3)
        writeframetoroot(self.meanstd0[0], "mean0", self.outfilesel) 
        writeframetoroot(self.meanstd0[1], "std0", self.outfilesel) 
        writeframetoroot(self.meanstd1[0], "mean1", self.outfilesel)      
        writeframetoroot(self.meanstd1[1], "std1", self.outfilesel)
        #writeframetoroot(self.meanstd2[0], "mean2", self.outfilesel)      
        #writeframetoroot(self.meanstd2[1], "std2", self.outfilesel)
        writeframetoroot(self.meanstd3[0], "mean3", self.outfilesel)      
        writeframetoroot(self.meanstd3[1], "std3", self.outfilesel)

    def finalize(self):
        self.outfileraw.Close()
        self.outfilesel.Close()

def calmeanstd(ldataframe):
    print("calaveragerms:")
    if len(ldataframe) > 0 :
        arrdataframe = np.array(ldataframe)
        print("ldataframe shape {} ndim {}".format(arrdataframe.shape, arrdataframe.ndim))
        arrmean = arrdataframe.mean(axis=0)
        arrstd = arrdataframe.std(axis=0)
        #print(arrmean)
        #print(arrstd)
        print(arrmean.mean(), arrmean.std())
        print(arrstd.mean(), arrstd.std())
        return (arrmean, arrstd)
    else :
        print("empty selected frames")
        return (np.zeros(72*72), np.zeros(72*72))

def writelframetoroot(ldataframe, savetag, outfile):
    outfile.cd()
    for i in range(len(ldataframe)):
        gr = list2tgraph(ldataframe[i])
        h2 = list2th2f(ldataframe[i],("h2"+savetag+"_{}").format(i))
        gr.Write(("tg"+savetag+"_{}").format(i))
        h2.Write() 

def writeframetoroot(dataframe, savetag, outfile):
    gr = arr2tgraph(dataframe)
    h2 = arr2th2f(dataframe,"h2_"+savetag)
    gr.Write("tg_"+savetag)
    h2.Write()

def hexframetodataframe(hexframe):
    dataframe = []
    for hexdata in hexframe:
        hexdata0 = hexdata[:4]
        hexdata1 = hexdata[4:]
        #print(hexdata, hexdata0, hexdata1, int(hexdata0, 16), int(hexdata1, 16), bin(int(hexdata0, 16)).lstrip('0b').zfill(16), bin(int(hexdata1, 16)).lstrip('0b').zfill(16))
        dataframe.append(int(hexdata0, 16) & int('0011111111111111',2))
        dataframe.append(int(hexdata1, 16) & int('0011111111111111',2))        
    return dataframe

def list2tgraph(lframe):
    n = len(lframe)
    x = array('f', [i for i in range(n)])
    y = array('f', lframe)
    tgframe = TGraph(n, x, y)
    return tgframe

def arr2tgraph(arrframe):
    n = arrframe.size
    x = array('f', [i for i in range(n)])
    y = array('f', arrframe.tolist())
    tgframe = TGraph(n, x, y)
    return tgframe

def list2th2f(lframe, h2name):
    h2 = TH2F(h2name,h2name,72,0,72,72,0,72)
    h2.SetOption("colz")
    for i in range(len(lframe)):
        nx = i%72 + 1
        ny = i//72 + 1
        #print(i,nx,ny)
        h2.SetBinContent(nx,ny,lframe[i])
    return h2

def arr2th2f(arrframe, h2name):
    h2 = TH2F(h2name,h2name,72,0,72,72,0,72)
    h2.SetOption("colz")
    for i in range(arrframe.size):
        nx = i%72 + 1
        ny = i//72 + 1
        #print(i,nx,ny)
        h2.SetBinContent(nx,ny,arrframe[i])
    return h2 

def find_label(dataframe, cut):
    lindex = []
    for i in range(len(dataframe)-1) :
        if dataframe[i] < cut :
            lindex.append(i)
    islabel = False
    if((len(lindex)>=3) and (lindex[1] - lindex[0] == 1) and (lindex[2]-lindex[1]==1)) : islabel = True
    return (lindex, islabel)

def ldataframealltoalign(ldataframeall0):
    ldataframealign0 = []
    for i in range(len(ldataframeall0)-1):
        #print(ldataframeall0[i][0][:1], ldataframeall0[i][1], ldataframeall0[i][2], ldataframeall0[i][3])
        isseq = (ldataframeall0[i+1][1] - ldataframeall0[i][1] == 1)
        isbothindex = (ldataframeall0[i+1][3] and ldataframeall0[i][3])
        #print(isseq, isbothindex)
        if isseq and isbothindex :
            if ldataframeall0[i+1][2][0] == ldataframeall0[i][2][0] :
                dataframealign0 = ldataframeall0[i][0][ldataframeall0[i][2][0]:] + ldataframeall0[i+1][0][:ldataframeall0[i][2][0]]
                ldataframealign0.append(dataframealign0)
            else :
                print("index not same place {} {}".format(ldataframeall0[i+1][2], ldataframeall0[i][2]))
    #print("ldataframealign0 size {}".format(len(ldataframealign0)))
    return ldataframealign0

def test():
    f1 = open('../data/arst1.05_20k_200mV_in.dat','rb')
    b0 = f1.read(10)
    print(len(b0.hex()))
    print(len(b0))
    #print(hex(b0))

def test1():
    #filename = '../data/AdcData-11-4-21-3-38.dat'
    #filename = '/Users/wanghulin/Workdir/CEE/harddriveallcee/data2/AdcData-11-5-18-9-20.dat'
    #filename = '/Users/wanghulin/Workdir/CEE/testDongsheng/software/data/dataout.dat'
    #filename = '/Users/wanghulin/Workdir/CEE/harddriveallcee/data/AdcData-11-5-17-57-12.dat'
    #filename = '/Users/wanghulin/Workdir/CEE/harddriveallcee/background.dat'
    #filename = '/Users/wanghulin/Workdir/CEE/harddriveallcee/50Hz_50mV_in.dat'
    dirname = "../2021.11.8test_data/a4/"
    filename1 = "AdcData-11-8-20-23-29.dat"
    filename = dirname+filename1
    run1 = myrun(filename)
    run1.getinput_from_dat()
    run1.process_input()
    run1.process_input_align()
    run1.finalize()

if __name__ == '__main__':
    test1()
