'''
Base code for 'saveHDF' feature in experiments for writing data to an HDF file during experiment
'''
import tables
import numpy as np
import tempfile
import shutil
import re

compfilt = tables.Filters(complevel=5, complib="zlib", shuffle=True)


class MsgTable(tables.IsDescription):
    '''
    Pytables custom table atom type used for the HDF tables named *_msgs
    '''
    time = tables.UIntCol()
    msg = tables.StringCol(256)


class HDFWriter(object):
    '''
    Used by the SaveHDF feature (features.hdf_features.SaveHDF) to save data
    to an HDF file in "real-time", as the task is running
    '''
    def __init__(self, filename='', verbose=True, mode="a"):
        '''
        Constructor for HDFWriter

        Parameters
        ----------
        filename : string
            Name of file to use to send data

        Returns
        -------
        HDFWriter instance
        '''
        if filename == '':
            # If no filename specified, create a temporary file which can be renamed later
            hdf_file = tempfile.NamedTemporaryFile(suffix='.h5', delete=False)
            hdf_file.flush()
            hdf_file.close()
            filename = hdf_file.name

        self.filename = filename
        self.verbose = verbose
        if self.verbose:
            print("HDFWriter: Saving datafile to %s"%filename)

        self.data = {}
        self.msgs = {}
        self.open_file(mode=mode)

    def open_file(self, mode="a"):
        print("HDFWriter: opening file")
        self.h5 = tables.open_file(self.filename, mode=mode)

        top_level_tables = self.h5.root._v_children.keys()
        for key in top_level_tables:
            if '_msgs' in key:
                # message group
                m = re.match('(.*)_msgs', key)
                system_key = m.group(1)
                self.msgs[system_key] = getattr(self.h5.root, key)
            else:
                self.data[key] = getattr(self.h5.root, key)


    def register(self, name, dtype, include_msgs=False):
        '''
        Create a table in the HDF file corresponding to the specified source name and data type

        Parameters
        ----------
        system : string
            Name of the system being registered
        dtype : np.dtype instance
            Datatype of incoming data, for later decoding of the binary data during analysis
        include_msgs : boolean, optional, default=True
            Flag to indicated whether a table should be created for "msgs" from the current source (default True)

        Returns
        -------
        np.array of shape (1,)
            dtype of return array matches input dtype
        '''
        if self.verbose:
            print("HDFWriter registered %r" % name)
        if dtype.subdtype is not None:
            #just a simple dtype with a shape
            dtype, sliceshape = dtype.subdtype
            arr = self.h5.create_earray("/", name, tables.Atom.from_dtype(dtype),
                shape=(0,)+sliceshape, filters=compfilt)
        else:
            arr = self.h5.create_table("/", name, dtype, filters=compfilt)

        self.data[name] = arr
        if include_msgs:
            msg = self.h5.create_table("/", name+"_msgs", MsgTable, filters=compfilt)
            self.msgs[name] = msg

        return np.zeros((1,), dtype=dtype)

    def send(self, system, data):
        '''
        Add a new row to the HDF table for 'system' and fill it with the 'data' values

        Parameters
        ----------
        system : string
            Name of system where the data originated
        data : object
            Data to send. Must have a '.tostring()' attribute

        Returns
        -------
        None
        '''
        if system in self.data:
            if data is not None:
                self.data[system].append(data)

    def sendMsg(self, msg):
        '''
        Write a string to the *_msgs table for each system registered with the HDF sink

        Parameters
        ----------
        msg : string
            Message to link to the current row of the HDF table

        Returns
        -------
        None
        '''
        for system in list(self.msgs.keys()):
            row = self.msgs[system].row
            row['time'] = len(self.data[system])
            row['msg'] = msg
            row.append()

    def sendAttr(self, system, attr, value):
        '''
        While the HDF writer process is running, set an attribute of the table

        Parameters
        ----------
        system : string
            Name of the table where the attribute should be set
        attr : string
            Name of the attribute
        value : object
            Value of the attribute to set

        Returns
        -------
        None
        '''
        if system in self.data:
            self.data[system].attrs[attr] = value

    def close(self, fname=None):
        '''
        Close the HDF file so that it saves properly after the process terminates

        Parameters
        ----------
        fname : string, optional
            Created HDF5 file gets renamed to this filename if specified
        '''
        self.h5.close()
        if self.verbose:
            print("Closed hdf")

        if not fname is None:
            shutil.copyfile(self.h5.filename, fname)
            if self.verbose:
                print("Copied output file to %s" % fname)

    def save(self, fname=None):
        """Save the HDF5 file by closing it and reopening"""
        self.close(fname=fname)
        self.open_file()
