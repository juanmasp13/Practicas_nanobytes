from odoo import models, tools, fields, SUPERUSER_ID, _

class LeaveReportCalendarInherit(models.Model):
    _inherit = "hr.leave.report.calendar"

    leave_type_name = fields.Char(string="Tipo de ausencia", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'hr_leave_report_calendar')
        self._cr.execute("""CREATE OR REPLACE VIEW hr_leave_report_calendar AS
        (SELECT 
            hl.id AS id,
            CONCAT(em.name, ': ', hl.duration_display) AS name,
            hl.date_from AS start_datetime,
            hl.date_to AS stop_datetime,
            hl.employee_id AS employee_id,
            hl.state AS state,
            hl.department_id AS department_id,
            hl.number_of_days AS duration,
            em.company_id AS company_id,
            lt.name AS leave_type_name,
            em.job_id AS job_id,
            COALESCE(
                CASE WHEN hl.holiday_type = 'employee' THEN COALESCE(rr.tz, rc.tz) END,
                cc.tz,
                'UTC'
            ) AS tz,
            hl.state = 'refuse' AS is_striked,
            hl.state NOT IN ('validate', 'refuse') AS is_hatched
            
            FROM hr_leave hl
            LEFT JOIN hr_employee em
                ON em.id = hl.employee_id
            LEFT JOIN hr_leave_type lt -- Nueva tabla agregada
                ON lt.id = hl.holiday_status_id
            LEFT JOIN resource_resource rr
                ON rr.id = em.resource_id
            LEFT JOIN resource_calendar rc
                ON rc.id = em.resource_calendar_id
            LEFT JOIN res_company co
                ON co.id = em.company_id
            LEFT JOIN resource_calendar cc
                ON cc.id = co.resource_calendar_id
            WHERE 
                hl.state IN ('confirm', 'validate', 'validate1')
                AND hl.active IS TRUE
        );
        """)

    def _read(self, fields):
        res = super()._read(fields)
        if self.env.context.get('hide_employee_name') and 'employee_id' in self.env.context.get('group_by', []):
            name_field = self._fields['leave_type_name']
            for record in self.with_user(SUPERUSER_ID):
                self.env.cache.set(record, name_field, record.name.split(':')[-1].strip())
        return res

