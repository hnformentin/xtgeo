"""GridProperty (not GridProperies) export functions"""

from __future__ import print_function, absolute_import

import xtgeo.cxtgeo.cxtgeo as _cxtgeo
from xtgeo.common import XTGeoDialog
from xtgeo.grid3d import _gridprop_lowlevel

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)

_cxtgeo.xtg_verbose_file('NONE')
XTGDEBUG = xtg.get_syslevel()


def to_file(self, pfile, fformat='roff', name=None, append=False,
            dtype=None):
    """Export the grid property to file."""
    logger.debug('Export property to file...')

    if 'roff' in fformat:
        if name is None:
            name = self.name

        binary = True
        if 'asc' in fformat:
            binary = False

        # for later usage
        append = False
        last = True

        export_roff(self, pfile, name, append=append,
                    last=last, binary=binary)

    elif fformat == 'grdecl':
        export_grdecl(self, pfile, name, append=append,
                      binary=False)

    elif fformat == 'bgrdecl':
        export_grdecl(self, pfile, name, append=append,
                      binary=True)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export ascii or binary ROFF format
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def export_roff(self, pfile, name, append=False, last=True, binary=True):

    logger.debug('Exporting {} to file {}'.format(name, pfile))

    if self._isdiscrete:
        _export_roff_discrete(self, pfile, name, append=append, last=last,
                              binary=binary)
    else:
        _export_roff_continuous(self, pfile, name, append=append, last=last,
                                binary=binary)


def _export_roff_discrete(self, pfile, name, append=False, last=True,
                          binary=True):

    logger.debug('Exporting {} to file {}'.format(name, pfile))

    carray = _gridprop_lowlevel.update_carray(self, undef=-999)

    ptr_idum = _cxtgeo.new_intpointer()
    ptr_ddum = _cxtgeo.new_doublepointer()

    # codes:
    ptr_codes = _cxtgeo.new_intarray(256)
    ncodes = self.ncodes
    codenames = ""
    logger.info(self.codes.keys())
    for inum, ckey in enumerate(sorted(self.codes.keys())):
        if ckey is not None:
            codenames += str(self.codes[ckey])
            codenames += '|'
            _cxtgeo.intarray_setitem(ptr_codes, inum, int(ckey))
        else:
            logger.warn('For some odd reason, None is a key. Check!')

    mode = 0
    if not binary:
        mode = 1

    if not append:
        _cxtgeo.grd3d_export_roff_pstart(mode, self._ncol, self._nrow,
                                         self._nlay, pfile,
                                         XTGDEBUG)

    nsub = 0
    isub_to_export = 0
    _cxtgeo.grd3d_export_roff_prop(mode, self._ncol, self._nrow,
                                   self._nlay, nsub, isub_to_export,
                                   ptr_idum, name, 'int', carray,
                                   ptr_ddum, ncodes, codenames,
                                   ptr_codes, pfile, XTGDEBUG)

    if last:
        _cxtgeo.grd3d_export_roff_end(mode, pfile, XTGDEBUG)

    _gridprop_lowlevel.delete_carray(self, carray)


def _export_roff_continuous(self, pfile, name, append=False, last=True,
                            binary=True):

    logger.debug('Exporting {} to file {}'.format(name, pfile))

    carray = _gridprop_lowlevel.update_carray(self, undef=-999.0)

    ptr_idum = _cxtgeo.new_intpointer()

    mode = 0
    if not binary:
        mode = 1

    if not append:
        _cxtgeo.grd3d_export_roff_pstart(mode, self._ncol, self._nrow,
                                         self._nlay, pfile,
                                         XTGDEBUG)

    # now the actual data
    nsub = 0
    isub_to_export = 0

    _cxtgeo.grd3d_export_roff_prop(mode, self._ncol, self._nrow,
                                   self._nlay, nsub, isub_to_export,
                                   ptr_idum, name, 'double', ptr_idum,
                                   carray, 0, '',
                                   ptr_idum, pfile, XTGDEBUG)

    if last:
        _cxtgeo.grd3d_export_roff_end(mode, pfile, XTGDEBUG)

    _gridprop_lowlevel.delete_carray(self, carray)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export ascii or binary GRDECL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def export_grdecl(self, pfile, name, append=False, binary=False):

    logger.debug('Exporting {} to file {}, GRDECL format'.format(name, pfile))

    if self._isdiscrete:
        dtype = 'int32'
    else:
        dtype = 'float32'

    carray = _gridprop_lowlevel.update_carray(self, dtype=dtype)

    iarr = _cxtgeo.new_intpointer()
    farr = _cxtgeo.new_floatpointer()
    darr = _cxtgeo.new_doublepointer()

    if 'double' in str(carray):
        ptype = 3
        darr = carray

    elif 'float' in str(carray):
        ptype = 2
        farr = carray

    else:
        ptype = 1
        iarr = carray

    mode = 0
    if not binary:
        mode = 1

    _cxtgeo.grd3d_export_grdeclprop2(self._ncol, self._nrow, self._nlay,
                                     ptype, iarr, farr, darr, self.name,
                                     pfile, mode, XTGDEBUG)



    _gridprop_lowlevel.delete_carray(self, carray)
