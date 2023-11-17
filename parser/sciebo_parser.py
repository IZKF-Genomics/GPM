import openpyxl
import xlrd

def parse_sciebo_report(report_path):
    if report_path.lower().endswith(".xlsx"):
        parse_sciebo_xlsx_report(report_path)
    elif report_path.lower().endswith(".xls"):
        parse_sciebo_xls_report(report_path)
    else:
        return BaseException
    
def parse_sciebo_xls_report(report_path):
    """ Gather:
    - Sequencing Kit
    - Cycles Read 1/2
    - Cycles Index 1/2
    """
    sequencing_kit = None
    cycles_read_1 = None
    cycles_index_1 = None
    cycles_read_2 = None
    cycles_index_2 = None

    # Open the Excel file
    workbook = xlrd.open_workbook(report_path)

    # Iterate through sheets
    for sheet_name in workbook.sheet_names():
        sheet = workbook.sheet_by_name(sheet_name)

        # Iterate through rows and columns
        for i in range(sheet.nrows):
            for j in range(sheet.ncols):
                cell_value = sheet.cell_value(i, j)

                if cell_value is None:
                    continue
                if cell_value == "Cycles Read 1":
                    cycles_read_1 = sheet.cell_value(i, j + 1)
                elif cell_value == "Cycles Index 1":
                    cycles_index_1 = sheet.cell_value(i, j + 1)
                elif cell_value == "Cycles Index 2":
                    cycles_index_2 = sheet.cell_value(i, j + 1)
                elif cell_value == "Cycles Read 2":
                    cycles_read_2 = sheet.cell_value(i, j + 1)
                elif isinstance(cell_value, str) and "kit" in cell_value.lower():
                    # Find the position of ':' and get the substring after it
                    index_colon = cell_value.find(':')
                    if index_colon != -1:
                        sequencing_kit = cell_value[index_colon + 1:].strip()

    print([sequencing_kit, cycles_read_1, cycles_index_1, cycles_read_2, cycles_index_2])
    # return [sequencing_kit, cycles_read_1, cycles_index_1, cycles_read_2, cycles_index_2]
    

def parse_sciebo_xlsx_report(report_path):
    """ Gather:
    - Sequencing Kit
    - Cycles Read 1/2
    - Cycles Index 1/2
    -
    -
    """
    sequencing_kit = None
    cycles_read_1 = None
    cycles_index_1 = None
    cycles_read_2 = None
    cycles_index_2 = None

    wb = openpyxl.load_workbook(filename=report_path, data_only=True)

    # Get All Sheets
    for excel_sheet_name in wb.sheetnames:

        # Get Sheet Object by names
        excel_sheet = wb[excel_sheet_name]

        for i in range(1,excel_sheet.max_row):
            for j in range(1, excel_sheet.max_column):
                excel_sheet_name_cell = excel_sheet.cell(row=i, column=j).value
                if excel_sheet_name_cell == None:
                    continue
                elif excel_sheet_name_cell == "Cycles Read 1":
                    cycles_read_1 = excel_sheet.cell(row=i, column=j+1).value
                elif excel_sheet_name_cell == "Cycles Index 1":
                    cycles_index_1 = excel_sheet.cell(row=i, column=j+1).value
                elif excel_sheet_name_cell == "Cycles Index 2":
                    cycles_index_2 = excel_sheet.cell(row=i, column=j+1).value
                elif excel_sheet_name_cell == "Cycles Read 2":
                    cycles_read_2 = excel_sheet.cell(row=i, column=j+1).value
                elif type(excel_sheet_name_cell) == str and "kit" in excel_sheet_name_cell.lower():
                    # Find the position of ':' and get the substring after it
                    index_colon = excel_sheet_name_cell.find(':')
                    if index_colon != -1:
                        sequencing_kit = excel_sheet_name_cell[index_colon + 1:].strip()
                    
                # print(str(excel_sheet_name_cell) + " - ", end ="")
            # print("\n")

    print([sequencing_kit, cycles_read_1, cycles_index_1, cycles_read_2, cycles_index_2])
    # return [sequencing_kit, cycles_read_1, cycles_index_1, cycles_read_2, cycles_index_2]

if __name__ == "__main__":
    #report_path = '231106_Möllmann_MedI_mRNA-Seq_5.xlsx'
    report_path = '230817_Jakovcevski_BioII_ChIP-Seq.xls'
    # report_path = '230712_Gui_MedIII_scSeq.xls'
    parse_sciebo_report(report_path)