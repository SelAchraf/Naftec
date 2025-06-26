from ast import literal_eval
from odoo import http
from odoo.http import request
import io
import xlsxwriter

class ArtecProductionReport(http.Controller):
    @http.route('/artec_production/excel/report/<string:production_ids>', type='http', auth='user')
    
    def generate_production_report(self, production_ids):
        production_ids = request.env['artec.production'].browse(literal_eval(production_ids))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Productions')

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
            'num_format': 'yyyy-mm-dd'
        })
        
        float_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0.00'
        })

        headers = ['Tank', 'Date', 'Produced volume [m³]']

        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        for row_num, record in enumerate(production_ids, start=1):
            worksheet.write(row_num, 0, record.tank_id.name, string_format)
            worksheet.write(row_num, 1, record.date, date_format)
            worksheet.write(row_num, 2, record.produced_volume, float_format)

        worksheet.set_column(0, 0, 20)  # Tank: 20 units
        worksheet.set_column(1, 1, 15)  # Date: 15 units
        worksheet.set_column(2, 2, 22)  # Produced volume: 22 units
        
        workbook.close()
        output.seek(0)

        report_name = 'Production_Report.xlsx'

        return request.make_response(
            output.getvalue(),
            headers = [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={report_name}')
            ]
        )