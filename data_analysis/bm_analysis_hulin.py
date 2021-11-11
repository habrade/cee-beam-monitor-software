#!/usr/bin/env python3
# import coloredlogs
# import logging

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
# coloredlogs.install(level="DEBUG", logger=log)


from glob import glob
import os
from ROOT import TGraph, TCanvas, TFile, TH1F, TH2F, TChain, gDirectory, TLegend, TColor
from array import array
import numpy as np

class myrun(object):
    def __init__(self, filename='../data/arst1.05_20k_200mV_in.dat', tag=''):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.basename = os.path.basename(filename)
        self.outfilenameraw = self.dirname + "/" + tag + self.basename.split('.')[0]+"_raw.root"
        self.outfilenamesel = self.dirname + "/" + tag + self.basename.split('.')[0]+"_sel.root"
        self.outfilenamesub = self.dirname + "/" + tag + self.basename.split('.')[0]+"_sub.root"
        #self.hexdataall = 0
        #self.lhexframe = [None]*4000 #notice!!
        self.lhexframe = []
        self.outfileraw = None
        self.outfilesel = None
        self.outfilesub = None
        #self.labelcut = [7600,7600,100,7600]
        self.labelcut = [5000,5000,100,5000]
        self.arrdataframealign0 = None
        self.arrdataframealign1 = None
        self.arrdataframealign2 = None
        self.arrdataframealign3 = None
        self.mean0 = None
        self.mean1 = None
        self.mean2 = None
        self.mean3 = None
        self.std0 = None
        self.std1 = None
        self.std2 = None
        self.std3 = None
        self.arrdataframealignsub0 = None
        self.arrdataframealignsub1 = None
        self.arrdataframealignsub2 = None
        self.arrdataframealignsub3 = None
        # log.debug("my run initialed")

    def getinput_from_dat(self):
        # log.debug("Get input from data file: {:s}".format(self.file_name))
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
                #print("frame start {}, stop {}, length {}".format(iframestart, iframestop, iframestop - iframestart + 1))
                if (iframestop - iframestart + 1) == 10368 :
                    self.lhexframe.append((lhex[iframestart:iframestop+1],ih))
                    #self.lhexframe[ilhex] = (lhex[iframestart:iframestop+1],ih)
                    #ilhex += 1
            #self.lhexframe = self.lhexframe[:ilhex]
            print("{} good frames".format(len(self.lhexframe)))


    def process_input(self):
        self.outfileraw = TFile(self.outfilenameraw,'recreate')
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
        self.outfilesel = TFile(self.outfilenamesel,'recreate')
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
        self.arrdataframealign0 = np.asarray(ldataframealign0)
        self.arrdataframealign1 = np.asarray(ldataframealign1)
        self.arrdataframealign2 = np.asarray(ldataframealign2)
        self.arrdataframealign3 = np.asarray(ldataframealign3)
        self.mean0 = self.arrdataframealign0.mean(axis=0) if self.arrdataframealign0.size > 0 else np.zeros(72*72)
        self.mean1 = self.arrdataframealign1.mean(axis=0) if self.arrdataframealign1.size > 0 else np.zeros(72*72)
        self.mean2 = self.arrdataframealign2.mean(axis=0) if self.arrdataframealign2.size > 0 else np.zeros(72*72)
        self.mean3 = self.arrdataframealign3.mean(axis=0) if self.arrdataframealign3.size > 0 else np.zeros(72*72)
        self.std0 = self.arrdataframealign0.std(axis=0) if self.arrdataframealign0.size > 0 else np.zeros(72*72)
        self.std1 = self.arrdataframealign1.std(axis=0) if self.arrdataframealign1.size > 0 else np.zeros(72*72)
        self.std2 = self.arrdataframealign2.std(axis=0) if self.arrdataframealign2.size > 0 else np.zeros(72*72)
        self.std3 = self.arrdataframealign3.std(axis=0) if self.arrdataframealign3.size > 0 else np.zeros(72*72)
        writeframetoroot(self.mean0, "mean0", self.outfilesel) 
        writeframetoroot(self.mean1, "mean1", self.outfilesel) 
        writeframetoroot(self.mean2, "mean2", self.outfilesel) 
        writeframetoroot(self.mean3, "mean3", self.outfilesel) 
        writeframetoroot(self.std0, "std0", self.outfilesel) 
        writeframetoroot(self.std1, "std1", self.outfilesel) 
        writeframetoroot(self.std2, "std2", self.outfilesel) 
        writeframetoroot(self.std3, "std3", self.outfilesel) 

    def process_bksub(self, bkg):
        self.outfilesub = TFile(self.outfilenamesub,'recreate')
        self.arrdataframealignsub0 = self.arrdataframealign0 - bkg.mean0 if self.arrdataframealign0.size > 0 else np.array([]) 
        self.arrdataframealignsub1 = self.arrdataframealign1 - bkg.mean1 if self.arrdataframealign1.size > 0 else np.array([])
        self.arrdataframealignsub2 = self.arrdataframealign2 - bkg.mean2 if self.arrdataframealign2.size > 0 else np.array([])
        self.arrdataframealignsub3 = self.arrdataframealign3 - bkg.mean3 if self.arrdataframealign3.size > 0 else np.array([])
        writearrframetoroot(self.arrdataframealignsub0, "framealignsub0", self.outfilesub)
        writearrframetoroot(self.arrdataframealignsub1, "framealignsub1", self.outfilesub)
        writearrframetoroot(self.arrdataframealignsub2, "framealignsub2", self.outfilesub)
        writearrframetoroot(self.arrdataframealignsub3, "framealignsub3", self.outfilesub)

    def finalize(self):
        self.lhexframe = 0
        if self.outfileraw : self.outfileraw.Close()
        if self.outfilesel : self.outfilesel.Close()
        if self.outfilesub : self.outfilesub.Close()

def calmeanstd(ldataframe):
    print("calaveragerms:")
    if len(ldataframe) > 0 :
        arrdataframe = np.asarray(ldataframe)
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

def writearrframetoroot(arrdataframe, savetag, outfile):
    outfile.cd()
    for i in range(arrdataframe.shape[0]):
        gr = arr2tgraph(arrdataframe[i])
        h2 = arr2th2f(arrdataframe[i],("h2"+savetag+"_{}").format(i))
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

def test(file_path):
    f1 = open(file_path,'rb')
    b0 = f1.read(10)
    print(len(b0.hex()))
    print(len(b0))
    #print(hex(b0))

def test1():
    #dirname = "../2021.11.8test_data/a4/"
    dirname = "../2021.11.11test_data/a2/"

    filenamebkg = "background2.dat"
    pathbkg = dirname+filenamebkg
    runbkg = myrun(pathbkg, tag="bkg")
    runbkg.getinput_from_dat()
    runbkg.process_input_align()
    runbkg.finalize()


#    filenamesig = "AdcData-11-8-20-23-40.dat"
#    pathsig = dirname + filenamesig
#    runsig = myrun(pathsig)
#    runsig.getinput_from_dat()
#    runsig.process_input_align()
#    runsig.process_bksub(runbkg)
#    runsig.finalize()

    paths = glob(dirname+'*/*.dat')
    print(f"{len(paths)} files")
    for f in paths:
        print(f'\n{f}')
        runsig = myrun(f, tag="sig")
        runsig.getinput_from_dat()
        runsig.process_input_align()
        runsig.process_bksub(runbkg)
        runsig.finalize()

def test2(file_path):
    runbkg = myrun(file_path, tag="bkg")
    runbkg.getinput_from_dat()


if __name__ == '__main__':
    dir_path = "../data/"
    file_name = "AdcData-11-11-15-56-28.dat"
    file_path = dir_path + file_name
    # test(file_path)
    test2(file_path)
