from ast import literal_eval
from odoo import http
from odoo.http import request
import io
import xlsxwriter

class ArtecExpeditionReport(http.Controller):
    @http.route('/artec_expedition/excel/report/<string:expedition_ids>', type='http', auth='user')
    
    def generate_expedition_report(self, expedition_ids):
        expedition_ids = request.env['artec.expedition'].browse(literal_eval(expedition_ids))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Expeditions')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1, 
            'align': 'center'
        })

        string_format = workbook.add_format({
            'border': 1, 
            'align': 'center'
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': 'yyyy-mm-dd hh:mm:ss'
        })
        
        float_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0.00'
        })

        headers = ['Tank', 'Start date', 'End date', 'Expedited volume [m³]']

        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        for row_num, record in enumerate(expedition_ids, start=1):
            worksheet.write(row_num, 0, record.tank_id.name, string_format)
            worksheet.write(row_num, 1, record.start_datetime, date_format)
            worksheet.write(row_num, 2, record.end_datetime, date_format)
            worksheet.write(row_num, 3, record.expedited_volume, float_format)

        worksheet.set_column(0, 0, 20)  # Tank: 20 units
        worksheet.set_column(1, 1, 18)  # Start date: 18 units
        worksheet.set_column(2, 2, 18)  # End date: 18 units
        worksheet.set_column(3, 3, 22)  # Expedited volume: 22 units
        
        workbook.close()
        output.seek(0)

        report_name = 'Expedition_Report.xlsx'

        return request.make_response(
            output.getvalue(),
            headers = [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={report_name}')
            ]
        )