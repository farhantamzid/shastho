"""
Service to fetch regulatory dashboard data from MySQL.
This isolates MySQL access from Flask routes and templates.
"""

from typing import Any, Dict, List

from app.utils.mysql_db import get_mysql_connection


def get_dashboard_data() -> Dict[str, Any]:
    conn = get_mysql_connection()
    cur = conn.cursor(dictionary=True)

    # Top stats
    cur.execute("SELECT total_cases, new_cases_today, active_outbreaks, regions_affected, hospitals_reporting, alerts FROM regulatory_stats ORDER BY id DESC LIMIT 1")
    stats_row = cur.fetchone() or {}
    stats = {
        'total_cases': stats_row.get('total_cases', 0),
        'new_cases_today': stats_row.get('new_cases_today', 0),
        'active_outbreaks': stats_row.get('active_outbreaks', 0),
        'regions_affected': stats_row.get('regions_affected', 0),
        'hospitals_reporting': stats_row.get('hospitals_reporting', 0),
        'alerts': stats_row.get('alerts', 0),
    }

    # Regions list
    cur.execute("SELECT name FROM regions ORDER BY name ASC")
    regions = [r['name'] for r in cur.fetchall()]  # type: ignore

    # Diseases summary
    cur.execute("SELECT name, cases, trend, risk_level FROM diseases ORDER BY cases DESC")
    diseases = cur.fetchall()  # type: ignore

    # Recent outbreaks
    cur.execute("""
        SELECT id, disease, region, cases, status, trend, DATE_FORMAT(start_date, '%Y-%m-%d') as start_date, severity
        FROM outbreaks
        ORDER BY id ASC
        LIMIT 5
    """)
    recent_outbreaks = cur.fetchall()  # type: ignore

    # Region summaries
    cur.execute("SELECT region, total_cases, active_outbreaks, population_affected, hospital_capacity FROM region_summary")
    region_rows = cur.fetchall()  # type: ignore

    # Attach primary diseases per region
    cur.execute("SELECT region, GROUP_CONCAT(disease ORDER BY disease SEPARATOR '||') AS primary_diseases FROM region_primary_diseases GROUP BY region")
    primary_map = {row['region']: (row['primary_diseases'] or '').split('||') for row in cur.fetchall()}  # type: ignore

    region_data: List[Dict[str, Any]] = []
    for row in region_rows:
        region_name = row['region']
        diseases_list = [d for d in primary_map.get(region_name, []) if d]
        region_data.append({
            'region': region_name,
            'total_cases': row['total_cases'],
            'active_outbreaks': row['active_outbreaks'],
            'primary_diseases': diseases_list,
            'population_affected': row['population_affected'],
            'hospital_capacity': row['hospital_capacity'],
        })

    # Monthly trends (build same structure as template expects)
    months = ['January','February','March','April','May','June','July']
    monthly_trends = {
        'months': months,
        'dengue': [],
        'malaria': [],
        'cholera': [],
        'covid': [],
        'influenza': [],
    }

    def fetch_series(name: str) -> List[int]:
        cur.execute("SELECT month_index, cases FROM monthly_trends WHERE disease = %s ORDER BY month_index ASC", (name,))
        series = cur.fetchall()  # type: ignore
        # Map month_index 1..7 to values
        values = [0]*7
        for r in series:
            idx = int(r['month_index']) - 1
            if 0 <= idx < 7:
                values[idx] = int(r['cases'])
        return values

    monthly_trends['dengue'] = fetch_series('Dengue')
    monthly_trends['malaria'] = fetch_series('Malaria')
    monthly_trends['cholera'] = fetch_series('Cholera')
    monthly_trends['covid'] = fetch_series('COVID-19')
    monthly_trends['influenza'] = fetch_series('Influenza')

    cur.close()
    conn.close()

    return {
        'stats': stats,
        'regions': regions,
        'diseases': diseases,
        'recent_outbreaks': recent_outbreaks,
        'region_data': region_data,
        'monthly_trends': monthly_trends,
    }


