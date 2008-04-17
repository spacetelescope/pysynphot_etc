"""Test that exceptions really are raised when they should be."""
import unittest,sys,os
import testutil
from pysynphot import observationmode
import pysynphot as S

class TMCmismatch(unittest.TestCase):
    """Can arise with mismatched graph & component tables"""
    def setUp(self):
        tmcname = os.path.join('mtab','r1j2146sm_tmc.fits')
        observationmode.COMPTABLE = observationmode._refTable(tmcname)
        tmgname = os.path.join('mtab','rbg2236im_tmg.fits')
        observationmode.GRAPHTABLE = observationmode._refTable(tmgname)
        self.omstring='acs,hrc,f555w,mjd#54000'

    def test1(self):
        "compname not found in tmc"
        self.assertRaises(IndexError, observationmode.ObservationMode,
                          self.omstring)

class RenormNonsense(unittest.TestCase):
    """Can arise with zero, negative, or nan spectra"""
    def setUp(self):
        self.sp=S.UnitSpectrum(1)
        self.bp=S.ObsBandpass('johnson,v')

    def testneg(self):
        sp2=self.sp*(-10)
        self.assertRaises(ValueError,
                          sp2.renorm,
                          self.bp, 15, 'vegamag')


        
        
if __name__ == '__main__':
    if 'debug' in sys.argv:
        testutil.debug(__name__)
    else:
        testutil.testall(__name__,2)
