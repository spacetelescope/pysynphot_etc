import sys
import os
import tempfile

from pysynphot import spectrum,observation, observationmode
from pysynphot import locations
from pysynphot import spparser as P
from pysynphot import units, planck
from pysynphot import newetc as etc

from pytools import testutil 



#Places used by test code
userdir   = os.environ['PYSYN_USERDATA']
testdata  = os.path.join(locations.rootdir,'calspec','feige66_002.fits')

#Freeze the version of the comptable so tests are not susceptible to
# updates to CDBS
cmptb_name = os.path.join('mtab','r1j2146sm_tmc.fits')
observationmode.COMPTABLE = observationmode._refTable(cmptb_name)
print "Tests are being run with %s"%observationmode.COMPTABLE
print "Synphot comparison results were computed with r1j2146sm_tmc.fits"
#Synphot comparison results are identified with the varname synphot_ref.

accuracy = 1.0e-5    # default floating point comparison accuracy
etc.debug = 0        # suppress messages from ETC-support tasks

testindex = 0
# spectrum values @ testindex
values = {'flam':           2.79979E-11,
          'flam z=2.5':     6.53011E-13,
          'fnu':            1.23037E-23,
          'photlam':        1.61773E+00,
          'photlam z=1.0':  4.04432E-01,
          'photlam z=2.5':  1.32060E-01,
          'photnu':         7.10915E-13,
          'jy':             1.23037E+00,
          'mjy':            1.23037E+03,
          'abmag':          8.67490E+00,
          'stmag':          5.28218E+00,
          'obmag':          -1.23590E+01,
          'v=0.0':          4.38149E-07,
          'v=5.0':          4.38149E-09,
          'vegamag':        1.81443E+00,
          'counts':         8.78177E+04,
          'angstrom':       1.14780E+03,
          'angstrom z=1.0': 2.29560E+03,
          'angstrom z=2.5': 4.01730E+03,
          'hz':             2.61189E+15,
          'nm':             1.14780E+02,
          'micron':         1.14780E-01,
          'mm':             1.14780E-04,
          'cm':             1.14780E-05,
          'm':              1.14780E-07,
          'integral':       1.65862E+03,
          'sp_npoints':     5.11000E+03,
          'thru_npoints':   1.1E+04,
          'thru_5000':      1.22327E-01,
          'obsmode':        'acs,hrc,f555w',
          'hstarea':        4.52389E+04,
          'countrate':      8.30680E+05,
          'efflam':         5328.12
          }

format_spec = '%.5E'    # floating point precision in assert
format_offset = {'win32':1,'sunos5':0,'linux2':0}

def format(value):
    ''' Formats scientific notation according to platform.    
    '''
    str = format_spec%(value)

    index1 = str.index('E') + 2
    index2 = index1 + format_offset[sys.platform]

    str1 = str[0:index1]
    str2 = str[index2:len(str)]

    return str1+str2



class SpectrumReadTestCase(testutil.FPTestCase):
    def setUp(self):
        self.sp = spectrum.TabularSourceSpectrum(testdata)

    def testunits(self):
        self.assertEqual(self.sp.waveunits.name,'angstrom')
        self.assertEqual(self.sp.fluxunits.name,'flam')

    def testlength(self):
        self.assertEqual(len(self.sp._wavetable), values['sp_npoints'])
        self.assertEqual(len(self.sp._fluxtable), values['sp_npoints'])

    def testinternalunits(self):
        # check internal arrays; they should always be expressed
        # in internal units.
        self.assertApproxFP(self.sp._wavetable[testindex],values['angstrom'])
        self.assertApproxFP(self.sp._fluxtable[testindex],values['photlam'])

    def testpointvalue(self):
        # fluxes should be expressed in flam
        (wav,flux) = self.sp.getArrays()
        self.assertApproxFP(flux[testindex],values['flam'])




class UnitsTestCase(testutil.FPTestCase):
    def setUp(self):
        self.sp = spectrum.TabularSourceSpectrum(testdata)
        

    def testang(self):
        self._testWave(self.sp,'angstrom')
    def testnm(self):
        self._testWave(self.sp,'nm')
    def testmicron(self):
        self._testWave(self.sp,'micron')
    def testmm(self):
        self._testWave(self.sp,'mm')
    def testcm(self):
        self._testWave(self.sp,'cm')
    def testm(self):
        self._testWave(self.sp,'m')
    def testhz(self):
        self._testWave(self.sp,'hz')
    def testflam(self):
        self._testFlux(self.sp,'flam')
    def testfnu(self):
        self._testFlux(self.sp,'fnu')
    def testphotlam(self):
        self._testFlux(self.sp,'photlam')
    def testphotnu(self):
        self._testFlux(self.sp,'photnu')
    def testjy(self):
        self._testFlux(self.sp,'jy')
    def testmjy(self):
        self._testFlux(self.sp,'mjy')
    def testabmag(self):
        self._testFlux(self.sp,'abmag')
    def teststmag(self):
        self._testFlux(self.sp,'stmag')
    def testobmag(self):
        self._testFlux(self.sp,'obmag')
    def testvegamag(self):
        self._testFlux(self.sp,'vegamag')
    def testcounts(self):
        self._testFlux(self.sp,'counts')

    def _testFlux(self, spectrum, units):
        spectrum.convert(units)
        (waves, fluxes) = spectrum.getArrays()
        self.assertApproxFP(fluxes[testindex], values[units])

    def _testWave(self, spectrum, units):
        spectrum.convert(units)
        (waves, fluxes) = spectrum.getArrays()
        self.assertApproxFP(waves[testindex], values[units])


class SpectrumTestCase(testutil.FPTestCase):
    def setUp(self):
        self.sp = spectrum.TabularSourceSpectrum(testdata)


    def testRedshift0(self):
        # redshift = 0 should return the same input.
        sp = self.sp.redshift(0.0)
        self.assertApproxFP(sp._wavetable[testindex], values['angstrom'])
        self.assertApproxFP(sp._fluxtable[testindex], values['photlam'])
        (dummy, fluxes) = sp.getArrays()
        self.assertApproxFP(fluxes[testindex],values['flam'])

        # convert to photnu, then redshift, and check that flux in
        # photonu units didn't change.
        sp.convert('photnu')
        self.assertApproxFP(sp._wavetable[testindex], values['angstrom'])
        self.assertApproxFP(sp._fluxtable[testindex], values['photlam'])
        (dummy, fluxes) = sp.getArrays()
        self.assertApproxFP(fluxes[testindex],values['photnu'])

    def testRedshift1(self):
        z = 1.0
        sp1 = self.sp.redshift(0.0)
        sp1.convert('photnu')
        sp2 = sp1.redshift(z)
        self.assertApproxFP(sp2._wavetable[testindex], values['angstrom z=1.0'])
        (dummy, fluxes) = sp2.getArrays()
        self.assertApproxFP(fluxes[testindex],values['photnu'])

        # internal array should change though, it's in photlam units.
        self.assertApproxFP(sp2._fluxtable[testindex],values['photlam z=1.0'])

        # now test redshift in flam units.
        sp1.convert('flam')
        sp2 = sp1.redshift(2.5)
        self.assertApproxFP(sp2._wavetable[testindex], values['angstrom z=2.5'])
        self.assertApproxFP(sp2._fluxtable[testindex], values['photlam z=2.5'])
        (dummy, fluxes) = sp2.getArrays()
        self.assertApproxFP(fluxes[testindex],values['flam z=2.5'])

    def testIntegrate(self):
        integral = self.sp.integrate()
        self.assertApproxFP(integral, values['integral'])

    def testMagnitude0(self):
        bp = spectrum.Band(('johnson','v'))
        sp2 = self.sp.setMagnitude(bp,0.0)
        (dummy, fluxes) = sp2.getArrays()
        self.assertApproxFP(fluxes[testindex], 4.37421e-07)

    def testMagnitude5(self):
        bp = spectrum.Band(('johnson','v'))
        sp2 = self.sp.setMagnitude(bp,5.0)
        (dummy, fluxes) = sp2.getArrays()
        self.assertApproxFP(fluxes[testindex], 4.37421e-09)

class PlanckTestCase(testutil.FPTestCase):
    def testbb(self):
        flux = planck.bb_photlam_arcsec(spectrum.default_waveset, 1000.)
        self.assertApproxFP(flux[5000], 3.8914E-8)


class ObsmodeTestCase(testutil.FPTestCase):

    def test1(self):
        obsmode = observationmode.ObservationMode(values['obsmode'])
        self.assertApproxFP(obsmode.area, values['hstarea'])
        throughput = obsmode.Throughput().throughputtable
        self.assertEqual(len(throughput), 11003)
        self.assertApproxFP(throughput[5000], 0.12232652011958853)

    #Add some COS cases


class FunctionTestCase(testutil.FPTestCase):
    def setUp(self):
        self.an = spectrum.AnalyticSpectrum()
        self.wave = self.an.GetWaveSet()

    def testunit1(self):
        sp = spectrum.UnitSpectrum(1.0,fluxunits='photlam')
        fluxes = sp(self.wave)
        self.assertApproxFP(fluxes.shape[0], 1.0E+04)
        self.assertApproxFP(fluxes[0], 1.0)
        self.assertApproxFP(fluxes[9000], 1.0)

    def testunit2(self):
        sp = spectrum.UnitSpectrum(1.0,fluxunits='flam')
        fluxes = sp(self.wave)
        self.assertApproxFP(fluxes[0], 2.51701E+10)
        self.assertApproxFP(fluxes[9000], 8.81633E+11)
        waves,fluxes = sp.getArrays()
        self.assertApproxFP(fluxes[0],1.0)
        self.assertApproxFP(fluxes[9000],1.0)

    def testbox1(self):
        box = spectrum.Box(5500.0,1.0)
        self.assertApproxFP(box.wavetable.shape[0], 22.)
        self.assertApproxFP(box.throughputtable.shape[0], 22.)
        self.assertApproxFP(box.throughputtable[1], 1.0)

    def testmult1(self):
        sp = spectrum.UnitSpectrum(1.0,fluxunits='photlam')
        box = spectrum.Box(5500.0,1.0)
        sp = sp * box
        wave = sp.GetWaveSet()
        fluxes = sp(wave)
        self.assertApproxFP(fluxes.sum(), 20.)

    def testmult2(self):
        sp = spectrum.UnitSpectrum(1.0,fluxunits='flam')
        box = spectrum.Box(5500.0,1.0)
        sp = sp * box
        wave = sp.GetWaveSet()
        fluxes = sp(wave)
        self.assertApproxFP(fluxes.sum(), 5.53744E+12)

class ParserTestCase(testutil.FPTestCase):
    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        os.chdir(locations.specdir)
        
    def tearDown(self):
        os.chdir(self.oldpath)
       
    def testunit1(self):
        expr = "unit(1,photlam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        fluxes = sp(wave)
        self.assertApproxFP(fluxes.shape[0], 1.0E+04)
        self.assertApproxFP(fluxes[0], 1.0)
        self.assertApproxFP(fluxes[9000], 1.0)

    def testunit2(self):
        expr = "unit(1,flam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        fluxes = sp(wave)
        self.assertApproxFP(fluxes[0], 2.51701E+10)
        self.assertApproxFP(fluxes[9000], 8.81633E+11)
        waves,fluxes = sp.getArrays()
        self.assertApproxFP(fluxes[0], 1.0)
        self.assertApproxFP(fluxes[9000], 1.0)

    def testmult1(self):
        expr = "(unit(1,flam) * box(5500.0,1.0))"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        fluxes = sp(wave)
        self.assertApproxFP(fluxes.sum(), 5.53744E+12)

    def testmult2(self):
        expr = "(unit(1,flam) * box(5500.0,20.0))"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        fluxes = sp(wave)
        self.assertApproxFP(fluxes.sum(), 1.13241E+14)

    def testrn1(self):
        expr = "rn(unit(1,flam),box(5500.0,1000),1.0E-18,flam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        sp.convert('flam')
        wave = sp.GetWaveSet()
        sp(wave)
        wav,flux = sp.getArrays()
        self.assertApproxFP(flux[0], 1.0E-18)
        box = spectrum.Box(5500.0,1.0)
        sp = sp * box
        integral = sp.integrate(fluxunits='flam')
        self.assertApproxFP(integral, 1.0E-18)

    #Add some cos test modes
    def testzodi(self):
        expr = "spec(Zodi.fits)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        f = sp(wave)
        w,f = sp.getArrays()
        self.assertApproxFP(f[0], 4.74300E-29)

    def testearthshine(self):
        expr = "earthshine.fits"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        f = sp(wave)
        w,f = sp.getArrays()
        self.assertApproxFP(f[0], 2.41358E-23)

    def testbandv(self):
        expr = "band(V)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[10], 9.78E-1)

    def testcomp1(self):
        expr = "rn(spec(Zodi.fits),band(V),22.7,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[100], 3.3173e-16)
        
    def testcomp2(self):
        expr = "(earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[1000], 1.17161e-13)

    def testcomp3(self):
        expr = "rn(unit(1,flam),band(johnson,v),15.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[1000], 0.000134817)

    def testcalspec(self):
        expr = "spec(crcalspec$gd71_mod_005.fits)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[1000], 9.44461E-2)

    def testpl1(self):
        expr = "pl(4000.,1,photlam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[5270], 1.00287)

    def testpl2(self):
        expr = "pl(4000.,1,jy)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        f = sp(wave)
        w,f = sp.getArrays()
        self.assertApproxFP(f[5270], 1.00287)

    def testbb1(self):
        expr = "bb(10000.0)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[5000], 1.06813E-2)

    def testzbb(self):
        expr = "z(bb(10000.0),1.0)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[5000], 2.67032E-3)

    def testem(self):
        expr = "em(3880.0,10.0,1.0000000168623835E-16,flam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[50], 1.83491E-6)

    def testcomp4(self):
        expr = "rn(elliptical.fits,band(johnson,v),15.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[50], 0.000220323)

    def testuserdir1(self):
        expr = "spec(%s)"%os.path.join(userdir,'vb8.inr.2a')
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[5000], 8.15545E-3)

    def testebmvx(self):
        expr = "rn(unit(1,flam)*ebmvx(0.1,gal1),box(5500.0,1),1.0E-18,flam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[5000], 1.53329E-7)

    def testuserdir2(self):
        expr = "spec(%stest.dat)"%userdir
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[5000], 6.08108E+10)

 
    def testk93(self):
        expr = "rn(icat(k93models,5770,0.0,4.5),band(johnson,v),20.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[500], 1.02585e-05)

    def testcomp5(self):
        expr = "rn(bb(5500.0),band(bessell,h),22.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[6000], 3.88200E-7)

    def testcomp6(self):
        expr = "rn(egal.dat,band(bessell,h),20.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[500], 9.60494E-7)

    def testcomp7(self):
        expr = "rn(bb(5500.0)*ebmvx(0.5,lmc),band(bessell,h),20.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[7000], 1.38877E-6)

    def testnullz(self):
        expr = "rn(z(null,NaN),band(johnson,v),15.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[5000], 0.000997219)

    def testcomp8(self):
        expr = "rn(icat(k93models,3500,0.0,4.6),band(johnson,v),15.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[1000], 0.000595778)

    def testcomp9(self):
        expr = "(spec(crcalspec$grw_70d5824_stis_001.fits))"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[1000], 5.08782E-2)

    def testcomp10(self):
        expr = "rn((icat(k93models,44500,0.0,5.0))*ebmvx(0.5,smc),band(johnson,v),15.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[1000], 0.00110939)

    def testcomp11(self):
        expr = "(spec(crcalspec$grw_70d5824_stis_001.fits))"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[2000], 1.41039E-2)

    def testgal1(self):
        expr = "ebmvx(0.1,gal1)"
        th = P.interpret(P.parse(P.scan(expr)))
        wave = th.GetWaveSet()
        throughput = th.throughputtable
        self.assertApproxFP(throughput[1000], 0.9816266)

    def testsmc(self):
        expr = "ebmvx(0.5,smc)"
        th = P.interpret(P.parse(P.scan(expr)))
        wave = th.GetWaveSet()
        throughput = th.throughputtable
        self.assertApproxFP(throughput[1000], 0.87486)

    def testcomp12(self):
        expr = "(spec(crcalspec$gd71_mod_005.fits))*ebmvx(0.1,gal1)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[2000], 7.15737E-3)

    def testcomp13(self):
        expr = "rn(z(qso_template.fits,1),band(johnson,v),18.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[2000],2.87964e-05 )

    def testcomp14(self):
        expr = "rn((icat(k93models,44500,0.0,5.0))*ebmvx(0.5,smc),band(johnson,v),15.0,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[200],2.09058e-06)

    def testcomp15(self):
        expr = "rn((icat(k93models,44500,0.0,5.0)),band(johnson,v),10.516,vegamag)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[200], 1.08749)

    def testcomp16(self):
        expr = "rn((spec(crcalspec$bd_28d4211_stis_001.fits)),box(2000.0,1),1.0E-12,flam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[200], 0.292770)

    def testcomp17(self):
        expr = "rn((spec(crcalspec$gd71_mod_005.fits))*ebmvx(0.1,gal1),box(5500.0,1),1.0E-16,flam)"
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        self.assertApproxFP(flux[2000], 4.37347E-5)

class ETCTestCase_Imag1(testutil.FPTestCase):

    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        self.expr = "(earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5)"
        os.chdir(locations.specdir)
       
    def tearDown(self):
        os.chdir(self.oldpath)
class ETCTestCase_Imag2(testutil.FPTestCase):
    
    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        os.chdir(locations.specdir)
       
    def tearDown(self):
        os.chdir(self.oldpath)


class ETCTestCase_Spec1(testutil.FPTestCase):

    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        os.chdir(locations.specdir)
       
    def tearDown(self):
        os.chdir(self.oldpath)
class ETCTestCase_Spec3(testutil.FPTestCase):
    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        os.chdir(locations.specdir)
        
    def tearDown(self):
        os.chdir(self.oldpath)
    def test4(self):
        spectrum = "spectrum=((earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5))"
        instrument = "instrument=cos,fuv,g130m,c1309"
        parameters = [spectrum, instrument]
        countrate = etc.specrate(parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 26.5409)


class IcatTestCase(testutil.FPTestCase):
    def setUp(self):

        self.testValues = \
            [["icat(k93models,18700,0.0,3.9)", 406,  8.7123058e+19],
             ["icat(k93models,15400,0.0,3.9)", 406,  6.1933150e+19],
             ["icat(k93models,11900,0.0,4.0)", 406,  3.8388731e+19],
             ["icat(k93models,9230,0.0,4.1)",  406,  2.1363460e+19],
             ["icat(k93models,8720,0.0,4.2)",  406,  1.7682054e+19],
             ["icat(k93models,8200,0.0,4.3)",  406,  1.3512093e+19],
             ["icat(k93models,7700,0.0,1.7)",  406,  1.1607616e+19],
             ["icat(k93models,7200,0.0,4.3)",  406,  6.8040033e+18],
             ["icat(k93models,6890,0.0,4.3)",  406,  5.4028874e+18],
             ["icat(k93models,6440,0.0,4.3)",  406,  3.7663594e+18],
             ["icat(k93models,6200,0.0,4.4)",  406,  3.0581503e+18],
             ["icat(k93models,5860,0.0,4.4)",  406,  2.2302826e+18],
             ["icat(k93models,4850,0.0,1.1)",  406,  5.9987856e+17],
             ["icat(k93models,5770,0.0,4.5)",  406,  2.0318679e+18],
             ["icat(k93models,5570,0.0,4.5)",  406,  1.6494994e+18],
             ["icat(k93models,5250,0.0,4.5)",  407,  1.2888412e+18],
             ["icat(k93models,4560,0.0,4.5)",  406,  4.1022782e+17],
             ["icat(k93models,4060,0.0,4.5)",  406,  1.5154204e+17],
             ["icat(k93models,3500,0.0,4.6)",  406,  3.9988099e+16],
             ["icat(k93models,44500,0.0,5.0)", 406,  3.9595035e+20],
             ["icat(k93models,38000.,0.0,4.5)", 406,  3.2685556e+20],
             ["icat(k93models,33000.,0.0,4.0)", 407, 2.5947967e+20]]

    def compute(self,expr):
        sp = P.interpret(P.parse(P.scan(expr)))
        wave = sp.GetWaveSet()
        flux = sp(wave)
        return wave, flux

    def test1(self):
        failed=[]
        for (expr,i,ref) in self.testValues:
            wave,flux = self.compute(expr)
            try:
                self.assertApproxFP(flux[i], ref)
            except AssertionError:
                failed.append("%30s   %10.9g   %10.9g\n"%(expr,ref,flux[i]))

        msg="%15s   %10s   %10s\n"%('expr','ref','test')+ "".join(failed)+ "Summary: %d/%d failed"%(len(failed),len(self.testValues))
        self.failUnless(len(failed) == 0,msg)

class WritefitsTestCase(testutil.FPTestCase):
    def test1(self):
        sp = P.interpret(P.parse(P.scan("icat(k93models,5750,0.0,4.5)")))

        filename = os.path.join(tempfile.gettempdir(),"resampler.fits")
        sp.writefits(filename)
        
        sp = spectrum.TabularSourceSpectrum(testdata)

        (wave, flux) = sp.getArrays()
        i = len(flux)/3
        self.assertApproxFP(flux[i], 9.634403E-13)
        

if __name__ == '__main__':
    if 'debug' in sys.argv:
        testutil.debug(__name__)
    else:
        testutil.testall(__name__,2)

