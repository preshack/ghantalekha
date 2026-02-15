import io
from datetime import datetime, timezone

from flask import request, send_file, jsonify
from flask_login import login_required

from app.api import api_bp
from app.services.payroll_service import generate_payroll_csv, generate_payroll_excel
from app.utils.decorators import manager_required


@api_bp.route('/export/csv')
@login_required
@manager_required
def export_csv():
    """Download payroll data as CSV."""
    now = datetime.now(timezone.utc)
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)

    csv_data = generate_payroll_csv(year, month)

    # Convert StringIO to BytesIO for send_file
    output = io.BytesIO(csv_data.getvalue().encode('utf-8'))
    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'workclock_payroll_{year}_{month:02d}.csv'
    )


@api_bp.route('/export/excel')
@login_required
@manager_required
def export_excel():
    """Download payroll data as Excel."""
    now = datetime.now(timezone.utc)
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)

    excel_data = generate_payroll_excel(year, month)

    return send_file(
        excel_data,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'workclock_payroll_{year}_{month:02d}.xlsx'
    )


@api_bp.route('/status')
def status():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'app': 'WorkClock'}), 200
