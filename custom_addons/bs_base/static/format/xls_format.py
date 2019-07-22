# -*- coding: utf-8 -*


def get_xlsx_formats(workbook):
    formats = {}
    bold_head = workbook.add_format({'bold': True, 'align': 'center'})
    bold_head_left = workbook.add_format({'bold': True, 'align': 'left'})
    bold_head_right = workbook.add_format({'bold': True, 'align': 'right'})
    big_header = workbook.add_format({'font_size': 13, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
    header = workbook.add_format({'font_size': 10.5, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
    align_header_right = workbook.add_format({'font_size': 10.5, 'bold': True, 'align': 'right', 'valign': 'vcenter'})
    align_header_left = workbook.add_format({'font_size': 10.5, 'bold': True, 'align': 'left', 'valign': 'vcenter'})

    align_body_left = workbook.add_format({'font_size': 10.5, 'bold': False, 'align': 'left', 'valign': 'vcenter'})
    align_body_right = workbook.add_format({'font_size': 10.5, 'bold': False, 'align': 'right', 'valign': 'vcenter'})

    center_bold = workbook.add_format({'bold': True, 'font_size': 10.5})
    center_bold.set_align('center')
    center_narrow = workbook.add_format({'bold': False, 'font_size': 10.5})
    center_narrow.set_align('center')

    money_format = workbook.add_format({'num_format': '#,##0.00', 'bold': False, 'font_size': 10.5})
    money_format_bold = workbook.add_format({'num_format': '#,##0.00', 'bold': True, 'font_size': 10.5})
    date_format = workbook.add_format({'num_format': 'mmmm d yyyy', 'bold': False, 'font_size': 10.5})
    date_format_bold = workbook.add_format({'num_format': 'mmmm d yyyy', 'bold': True, 'font_size': 10.5})

    formats.update({
        'big_header': big_header,
        'bold_head': bold_head,
        'bold_head_left': bold_head_left,
        'bold_head_right': bold_head_right,
        'header': header,
        'header_right': align_header_right,
        'header_left': align_header_left,
        'body_left': align_body_left,
        'body_right': align_body_right,
        'center_bold': center_bold,
        'center_narrow': center_narrow,
        'money_format': money_format,
        'money_format_bold': money_format_bold,
        'date_format': date_format,
        'date_format_bold': date_format_bold
    })
    return formats
