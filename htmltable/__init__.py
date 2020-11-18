#import numpy as np
class HTMLtable:
    """
    HTML Table helper class. 

    """
    CELLTYPE = 'type'
    CELLCONTENTS = 'contents'
    CELLSPANDOWN = 'spandown'
    CELLSPANRIGHT = 'spanright'
    CELLTYPE_NORMAL         = 0
    CELLTYPE_BEGINSPANRIGHT = 1
    CELLTYPE_BEGINSPANDOWN  = 2
    CELLTYPE_SPANNED        = 4 
    def __init__(self, rows:int=2, cols:int=2, caption:str=None):
        if not (isinstance(rows, int) and isinstance(cols, int)):
            raise TypeError('rows and cols must be integers')
        if (rows<1) or (cols<1):
            raise ValueError('(rows<1) or (cols<1)')
        self.__rows=rows
        self.__cols=cols
        self.__caption=caption
        self.__cells = {row:{col:{HTMLtable.CELLTYPE:HTMLtable.CELLTYPE_NORMAL, 
                                  HTMLtable.CELLCONTENTS:'', 
                                  HTMLtable.CELLSPANRIGHT: 0, 
                                  HTMLtable.CELLSPANDOWN:0} for col in range(cols)} for row in range(rows)}
        return None
    def add_rows(self, nrows:int):
        if not isinstance(nrows, int):
            raise TypeError(f'excpeted int, got {type(nrows).__repr__(nrows)} ')
        if nrows<=0:
            raise ValueError(f' number of rows must not be smaller than 1')
        self.__cells.update( {row:{col:{HTMLtable.CELLTYPE:HTMLtable.CELLTYPE_NORMAL, 
                                HTMLtable.CELLCONTENTS:'', 
                                HTMLtable.CELLSPANRIGHT: 0, 
                                HTMLtable.CELLSPANDOWN:0} for col in range(self.__cols)} for row in range(self.__rows, self.__rows+nrows)} )
        self.__rows += nrows
        return self
    def add_columns(self, ncols:int):
        if not isinstance(ncols, int):
            raise TypeError(f'excpeted int, got {type(ncols).__repr__(ncols)} ')
        if ncols<=0:
            raise ValueError(f' number of ncols must not be smaller than 1')
        for row in range(self.__rows):
            self.__cells[row].update({col:{HTMLtable.CELLTYPE:HTMLtable.CELLTYPE_NORMAL, 
                                        HTMLtable.CELLCONTENTS:'', 
                                        HTMLtable.CELLSPANRIGHT: 0, 
                                        HTMLtable.CELLSPANDOWN:0} for col in range(self.__cols, self.__cols+ncols)})
        self.__cols += ncols
        return self
    def __getcell(self, row, col, attr:str=None):
        if attr is None:
            return self.__cells[row][col]
        else:
            return self.__cells[row][col][attr]
    @property
    def caption(self):
        return self.__caption

    @caption.setter
    def caption(self, caption:str):
        """
        Set the extra caption under the table.
        Use None to remove it.
        """
        self.__caption=caption
        return self

    def merge_cells(self, row_start, col_start, row_end=None, col_end=None):
        """
        Merge the cells into one span. Will fail if cells are already part of a span
        Enter first and last column, 0-indexed
        """
        if (row_end is None and col_end is None): 
            raise ValueError('merge must be at least 2 rows or two columns in size')
        if row_end is None: row_end = row_start
        if col_end is None: col_end = col_start
        if col_end-col_start<1 and row_end-row_start<1:
            raise ValueError(f'merge must be at least 2 rows or 2 columns in size. Given:  {row_start}, {col_start} to {row_end}, {col_end}')
        if col_end<col_start or row_end<row_start:
            raise ValueError(f'merge cannot start before end: Given {row_start}, {col_start} to {row_end}, {col_end}')            
        #check, all cells must be CELLTYPE==0
        if sum([self.__getcell(row, col, HTMLtable.CELLTYPE) for row in range(row_start, row_end+1) for col in range(col_start, col_end+1) ])>0:
            raise ValueError(f'Cells in the range {row_start}, {col_start}, {row_end}, {col_end} are already spanned')
        # set all cells to spanned
        for row in range(row_start, row_end+1):
            for col in range(col_start, col_end+1):
                self.__cells[row][col][HTMLtable.CELLTYPE] = HTMLtable.CELLTYPE_SPANNED
        # new type of left top cell
        ntLT = HTMLtable.CELLTYPE_NORMAL + (HTMLtable.CELLTYPE_BEGINSPANDOWN if row_end>row_start else 0) + (HTMLtable.CELLTYPE_BEGINSPANRIGHT if col_end>col_start else 0) 
        self.__cells[row_start][col_start][HTMLtable.CELLTYPE] = ntLT
        if (col_end-col_start)!=0:
            self.__cells[row_start][col_start][HTMLtable.CELLSPANRIGHT] = (col_end-col_start)+1
        if (row_end-row_start)!=0:
            self.__cells[row_start][col_start][HTMLtable.CELLSPANDOWN] = (row_end-row_start)+1
    
        return self

    def __setitem__(self, key, value):
        """
        write value(s) to the table.
        
        """
        # [row] int
        # [row,:] tuple(int,  slice(None, None, None))
        # [row, col] tuple(int, int)
        # [:, col] tuple( slice(None, None, None), int)
        # [row:row2, col] tuple(slice(row, row2, None), int)

        if isinstance(key, tuple) and len(key)==2 and isinstance(key[0], int) and isinstance(key[1], int):
            # row, col
            row, col = key
            if row>=self.__rows or col>=self.__cols:
                raise KeyError(f'{row}, {col} out of bounds {self.__rows}, {self.__cols} ')
            if self.__getcell(row, col, HTMLtable.CELLTYPE) == HTMLtable.CELLTYPE_SPANNED:
                raise KeyError(f'{row}, {col} part of spanned rows/columns ')
            self.__cells[row][col][HTMLtable.CELLCONTENTS] = str(value)
        else:
            raise NotImplementedError(f'key == {key} not yet supported')

    def _repr_html_(self)->str:
        head = """  <head> 
        <meta charset="utf-8">
        <style>
            table, th, td {border: 1px solid #AAAAAA; border-collapse: collapse; padding: 4px 8px}
        </style> 
        </head>
        <body><table>"""
        if self.__caption is not None:
            head += ' <caption>' + str(self.__caption) + '</caption> '
        tail = '</table>'
        bodystr = ''
        for row in range(0, self.__rows):
            bodystr += '<tr>'
            for col in range(0, self.__cols):
                if self.__getcell(row, col, HTMLtable.CELLTYPE)!=HTMLtable.CELLTYPE_SPANNED:
                    colspan = ''
                    rowspan = ''
                    if self.__getcell(row, col, HTMLtable.CELLTYPE) & HTMLtable.CELLTYPE_BEGINSPANRIGHT:
                        colspan = f' colspan="{self.__getcell(row, col, HTMLtable.CELLSPANRIGHT)}" '
                    if self.__getcell(row, col, HTMLtable.CELLTYPE) & HTMLtable.CELLTYPE_BEGINSPANDOWN:
                        rowspan = f' rowspan="{self.__getcell(row, col, HTMLtable.CELLSPANDOWN)}" '
                    bodystr += f'<td {colspan} {rowspan} >' + self.__getcell(row, col, HTMLtable.CELLCONTENTS) + '</td>'
                else:
                    pass
            bodystr += '</tr>'
        return head + bodystr + tail
    def __repr__(self)->str:
        return str(self.__cells)
