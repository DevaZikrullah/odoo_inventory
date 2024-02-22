{
    'name' : 'Custom Sale HIJ',
    'description': """
        Custome Sale
    """,
    "depends": ["sale_management","product","purchase","stock","base","fleet","digest", "account", 'hr','mail'],
    'category': 'custom HIJ',
    'data': [
        'views/sale_quot_views.xml',
        'wizard/trans_date_view.xml',
        'views/fleet_views.xml',
        'wizard/delivered_view.xml',
        'wizard/rpb_views.xml',
        'wizard/rpb_views_wizard.xml',
        'views/product_template_views.xml',
        'views/prb_views.xml',
        'views/rpb_rpb_views.xml',
        'reports/report_rpb.xml',
        'reports/rpb_format_report.xml',
        'reports/report_so.xml',
        'reports/so_format_report.xml',
        'wizard/mutation_views.xml',
        'wizard/update_stock.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'sales_custom/static/src/js/update_accurate_button.js',
        ],
        'web.assets_qweb': [
            'sales_custom/static/src/xml/update_accurate_button.xml',
        ],
    },
}
