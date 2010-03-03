"""Contains SpecCase used by commissioning_cases.CommCase*.
Defines all the common setup and testing.
"""

import os

import numpy as N
import pysynphot as S
from pysynphot import etc
#For thermal classes only
from pysynphot.observationmode import ObservationMode

#BUG: find a better way
DATADIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'data')


#TODO: set a specified graph/comp/therm table set in a module setup
                                       
class SpecCase(object):
    @classmethod
    def setUpClass(cls):
        """Always overridden by the child cases, but let's put some
        real values in here to test with"""
        cls.obsmode=None
        cls.spectrum=None
        cls.bp=None
        cls.sp=None
        cls.obs=None
        cls.fname=None #Pattern like "tname_%s.fits"
        cls.setup2()

    @classmethod
    def tearDownClass(cls):
        """Add names of failed items to the okfile"""
        
        if cls.okset:
            f=open(cls.tda['_okfile'],'w')
            for item in cls.okset:
                refname=os.path.join(HERE,
                                     cls.fname%item.replace('.fits',
                                                             '_ref.fits'))
                tname=os.path.join(HERE,cls.fname%item)
                f.write("%s %s\n"%(tname,refname))
            f.close()


    @classmethod    
    def setup2(cls):
        #Do the common setup here.
        cls.sigthresh = 0.01
        cls.thresh = 0.01
        cls.tda=dict(obsmode=cls.obsmode,
                      spectrum=cls.spectrum,
                      thresh=cls.thresh,
                      sigthresh=cls.sigthresh,
                      _okfile=cls.fname.replace('_%s.fits','.okfile'))
        cls.tra=dict()

        cls.okset=set() #Tracks okifying bookkeeping

        if cls.obsmode != "None":
            kind = 'thru'
            cls.bp=S.ObsBandpass(cls.obsmode)
            cls.bp.writefits(cls.fname%kind, clobber=True,
                              trimzero=False)
            cls.tra[kind]=cls.bp.name
            cls.okset.add(kind)
        else:
            cls.bp = None

            
        if cls.spectrum != "None":
            kind = 'spec'
        #All the data lives in a parallel directory, so go sit there
        #in case we need a file
            os.chdir(DATADIR)
            cls.sp=etc.parse_spec(cls.spectrum)
            os.chdir(HERE)
            cls.sp.writefits(cls.fname%kind, clobber=True,
                              trimzero=False)
            cls.tra[kind]=cls.sp.name
            cls.okset.add(kind)
        else:
            cls.sp = None

            
        if "None" not in (cls.obsmode, cls.spectrum):
            kind='obs'
            try:
                cls.obs = S.Observation(cls.sp, cls.bp)
            except ValueError, e:
                cls.tra['obs_error']=str(e)
                cls.obs = str(e)
                return #then the obs tests should raise errors
            cls.obs.convert('counts')
            x = dict(PSCNTRAT = (cls.obs.countrate(),'countrate'),
                     PSEFFLAM = (cls.obs.efflam(),'efflam'))
            cls.obs.writefits(cls.fname%kind, hkeys=x, clobber=True,
                               trimzero=False)
            cls.tra[kind]=cls.obs.name
            cls.okset.add(kind)
        else:
            cls.obs = None

#Helper methods for arrays
    def count_outliers(self,Nsigma=3):
        mean=self.adiscrep.mean()
        std=self.adiscrep.std()
        outliers=N.where(abs(self.adiscrep) > mean + Nsigma*std)
        return len(outliers[0])

    def arraysigtest(self,ref,test):
        #Raise an error if the arrays are not the same size
        if test.shape != ref.shape:
            raise ValueError("Array size mismatch")
        tt=test[2:-2]
        rr=ref[2:-2]
        #Identify the significant elements
        tidx=N.where(tt>(self.sigthresh*tt.max()))[0]
        ridx=N.where(rr>(self.sigthresh*rr.max()))[0]
        #Set a flag if they're not the same set
        if not (N.alltrue(tidx == ridx)):
            self.tra['SigElemDiscrep']=True
            tidx=ridx

        #Now compare only the significant elements.
        #We no longer need to exclude points with zero value, because
        #those points were already excluded as insignificant.
        self.arraytest(tt[ridx],rr[ridx])

    def arraydiff(self,test,ref):
        idx=N.nonzero(ref)
        ans=(test[idx]-ref[idx])/ref[idx]
        return ans

    def arraytest(self,ref,test):
        self.adiscrep=self.arraydiff(test,ref)
        count=N.where(abs(self.adiscrep)>self.thresh)[0].size
        try:
            self.tra['Discrepfrac']=float(count)/self.adiscrep.size
            self.tra['Discrepmin']=self.adiscrep.min()
            self.tra['Discrepmax']=self.adiscrep.max()
            self.tra['Discrepmean']=self.adiscrep.mean()
            self.tra['Discrepstd']=self.adiscrep.std()
            self.tra['Outliers']=self.count_outliers(5)
            self.failUnless(N.alltrue(abs(self.adiscrep)<self.thresh),
                            msg="Worst case %f"%abs(self.adiscrep).max())
        except ZeroDivisionError:
            self.tra['Discrepfrac']=0.0
            self.tra['Discrepmin']=0.0
            self.tra['Discrepmax']=0.0

#Helper method for scalar comparison
    def tcompare(self,rval,tval):
        if rval != 0:
            self.discrep=(tval-rval)/rval
        else:
            self.discrep=tval-rval
        self.tra['Discrep']=self.discrep
        self.tra['ref']=rval
        self.tra['tst']=tval
        self.failUnless(abs(self.discrep) < self.thresh,
                        msg="Discrep=%f"%self.discrep)

    def failUnless(self, expr, msg=None):
        #Copied from unittest.TestCase
        """Fail the test unless the expression is true."""
        if not expr: raise self.failureException, msg

    def cleanup(self,item):
        #Pop from oklist & clean up file
        self.okset.remove(item)
        os.unlink(self.fname%item)
        
#The actual tests start here.
#In the parent case, we do spectrum-only tests.

    def testspec(self):
        if self.sp:
            self.spref = S.FileSpectrum((self.fname%'spec').replace('.fits','_ref.fits'))
            self.arraytest(self.spref.flux, self.sp.flux)
            self.cleanup('spec')
            
class CommCase(SpecCase):
    #In the default case, we also do throughput and observation tests
    def testthru(self):
            self.bpref = S.FileBandpass((self.fname%'thru').replace('.fits','_ref.fits'))
            self.arraytest(self.bpref.throughput, self.bp.throughput)
            self.cleanup('thru')

    def testobs(self):
            self.obsref = S.FileSpectrum((self.fname%'obs').replace('.fits','_ref.fits'))
            self.arraytest(self.obsref.flux, self.obs.binflux)
            self.cleanup('obs')
            
    def testcntrate(self):
            self.obsref = S.FileSpectrum((self.fname%'obs').replace('.fits','_ref.fits'))
            self.tcompare(self.obsref.fheader['PSCNTRAT'],
                          self.obs.countrate())

    def testefflam(self):
            self.obsref = S.FileSpectrum((self.fname%'obs').replace('.fits','_ref.fits'))
            self.tcompare(self.obsref.fheader['PSEFFLAM'],
                          self.obs.efflam())

class ThermCase(CommCase):
    #In the thermal case, we also do thermal tests.

    @classmethod
    def setup2(cls):
        #First call the parent
        super(CommCase,cls).setup2()

        kind = 'therm'
        #Then do the thermal stuff
        cls.omode=ObservationMode(cls.obsmode)
        cls.thspec=cls.omode.ThermalSpectrum()
        cls.tra['thspec']=cls.thspec.name
        
        cls.thspec.convert('counts')
        cls.thermback=cls.thspec.integrate()*cls.omode.pixscale**2*cls.omode.area
        x = dict(PSTHMBCK = (cls.thermback,'thermback'))
        cls.thspec.writefits(cls.fname%kind, clobber=True,
                              trimzero=False, hkeys=x)
        cls.okset.add(kind)
        
    def testthspec(self):
        self.thref = S.FileSpectrum((self.fname%'therm').replace('.fits','_ref.fits'))
        self.arraytest(self.thref.flux, self.thspec.flux)
        self.cleanup('therm')
                                    

    def testhermback(self):
        self.thref = S.FileSpectrum((self.fname%'therm').replace('.fits','_ref.fits'))
        self.tcompare(self.thref.fheader['PSTHMBCK'],
                      self.thermback)
        
class Testing(CommCase):
    @classmethod
    def setUpClass(cls):
        cls.obsmode="stis,e230h,i1913"
        cls.spectrum="bb(30000)"
        cls.fname="T1_%s.fits"
        cls.setup2()
