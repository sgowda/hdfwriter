import unittest
import tables
import os
import numpy as np

from hdfwriter import HDFWriter


class TestHDFWriter(unittest.TestCase):
    test_output_fname = "test.hdf"
    def setUp(self):
        self.wr = wr = HDFWriter(self.test_output_fname)
        self.table1_dtype = np.dtype([("stuff", np.float64)])
        self.table2_dtype = np.dtype([("stuff2", np.float64), ("stuff3", np.uint8)])
        wr.register("table1", self.table1_dtype, include_msgs=True)
        wr.register("table2", self.table2_dtype, include_msgs=False)

        # send some data
        wr.send("table1", np.zeros(3, dtype=self.table1_dtype))
        wr.send("table1", np.ones(1, dtype=self.table1_dtype))
        wr.send("table2", np.ones(1, dtype=self.table2_dtype))
        wr.sendMsg("message!")
        wr.close()

    def test_h5_file_created(self):
        h5 = tables.open_file(self.test_output_fname)
        self.assertTrue(hasattr(h5, "root"))
        h5.close()

    def test_tables_exist(self):
        h5 = tables.open_file(self.test_output_fname)
        self.assertTrue(hasattr(h5.root, "table1"))
        self.assertTrue(hasattr(h5.root, "table1_msgs"))
        self.assertTrue(hasattr(h5.root, "table2"))
        self.assertFalse(hasattr(h5.root, "table2_msgs"))

        self.assertEqual(len(h5.root.table1), 4) # NOTE this only works after a bugfix in HDFWriter
        self.assertEqual(len(h5.root.table2), 1)
        self.assertEqual(len(h5.root.table1_msgs), 1)

        self.assertEqual(h5.root.table1_msgs[0]['msg'].decode("utf-8"), "message!")
        self.assertEqual(h5.root.table1_msgs[0]['time'], 4)

        self.assertTrue(np.all(h5.root.table2[:]['stuff2'] == 1))
        h5.close()

    def test_auto_temp_file_naming(self):
        hdfwriter = HDFWriter()

        dtype = np.dtype([("x", "f8", (1,))])

        data = hdfwriter.register("data", dtype, include_msgs=False)
        data['x'] = 2
        hdfwriter.send("data", data)

        hdfwriter.close("test.h5")

        hdf = tables.open_file("test.h5")
        self.assertTrue(np.all(hdf.root.data[:]['x'] == 2))
        hdf.close()
        
        if os.path.exists("test.h5"):
            os.remove("test.h5")

    def test_pre_spec_file_naming(self):
        fname = "prespec_file_name.h5"
        hdfwriter = HDFWriter(fname)

        dtype = np.dtype([("x", "f8", (1,))])

        data = hdfwriter.register("data", dtype, include_msgs=False)
        data['x'] = 2
        hdfwriter.send("data", data)

        hdfwriter.close()

        hdf = tables.open_file(fname)
        self.assertTrue(np.all(hdf.root.data[:]['x'] == 2))
        hdf.close()

        if os.path.exists(fname):
            os.remove(fname)        

    def tearDown(self):
        if os.path.exists(self.test_output_fname):
            os.remove(self.test_output_fname)

if __name__ == '__main__':
    unittest.main()

