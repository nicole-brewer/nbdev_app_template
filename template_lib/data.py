# AUTOGENERATED! DO NOT EDIT! File to edit: template_nbs/02_data.ipynb (unless otherwise specified).

__all__ = ['logger', 'DATA_DIR', 'DATA_FILE', 'DOWNLOAD_DATA_NAME', 'FLOAT_FORMAT', 'FILENAME', 'DataModel', 'DataView',
           'DataDelegate', 'DataTab']

# Cell
from IPython.display import display, clear_output
import glob, csv
import ipywidgets as widgets
from traitlets import HasTraits, Int
import pandas as pd
import os
import logging
logger = logging.getLogger()

# Cell
DATA_DIR = '../data' # TODO: symlink?
DATA_FILE = 'loti.csv'
DOWNLOAD_DATA_NAME = 'loti-download'
FLOAT_FORMAT = '0,.4f'
FILENAME = os.path.join(DATA_DIR, DATA_FILE)

# Cell
class DataModel(HasTraits):

    min_year = Int()
    max_year = Int()
    start_year = Int()
    end_year = Int()

    def __init__(self, filename):
        super().__init__()

        # Load data into memory from file
        self.data = pd.read_csv(filename, escapechar='#')
        self.headers = list(self.data.columns.values)
        self.min_year = min(self.data[self.data.columns[0]])
        self.max_year = max(self.data[self.data.columns[0]])
        self.start_year = self.min_year
        self.end_year = self.max_year
        self.results = None

    def filter_data(self):
        """Use selection criteria to filter the data"""

        self.results = self.data[(self.data[self.headers[0]] >= self.start_year) &
                                       (self.data[self.headers[0]] <= self.end_year)]
        self.num_results = self.results.shape[0]

    def create_download_file(self):
        """Prep data for export."""

        # First, to save space, delete existing download file(s)
        for filename in glob.glob(DOWNLOAD_DATA_NAME + '.*'):
            os.remove(filename)

        filename = DOWNLOAD_DATA_NAME + '.csv'
        self.results.to_csv(filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

        return filename

# Cell
class DataView(widgets.Output):

    def __init__(self):
        super().__init__()
        layout = {
            'overflow': 'scroll',
            'max_height': '400px',
            'max_width': '300px'
        }
        self.layout = widgets.Layout(**layout)

# Cell
class DataDelegate(DataView):

    def __init__(self, model=None, wide=False):
        super().__init__()
        self.wide = wide
        if model:
            self.initialize(model)

    def initialize(self, model):
        self.model = model
        self.display_data()

    def _ipython_display_(self):
        """the function that is envoked when `display` is called with a DataDelegate parameter"""
        super()._ipython_display_()

    def display_data(self):
        self.clear_output()
        self.set_display()
        with self:
            if self.model.results is not None:
                display(self.model.results)
            else:
                display(self.model.data)

    def set_display(self):
        """Prep Pandas to display specific number of data lines."""
        with self:
            pd.set_option('display.width', 1000)# Prevent data desc line breaking
            pd.set_option('display.max_rows', self.model.data.shape[0] + 1)
            if self.wide:
                pd.set_option('display.float_format', lambda x: format(x, FLOAT_FORMAT))

# Cell
class DataTab(widgets.Accordion):

    def __init__(self, dataModel):
        super().__init__()
        self.set_title(0, 'Data')
        self.data = DataDelegate(dataModel)
        self.children = (self.data, )